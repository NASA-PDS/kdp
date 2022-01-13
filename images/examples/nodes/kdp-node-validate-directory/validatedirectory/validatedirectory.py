#!/bin/env python3

import os
import sys
import json
import glob
import tempfile
import subprocess

import s3utils
import util


def main():

    # parse input from env
    env = parse_env()

    # stage the data locally
    with tempfile.TemporaryDirectory() as working_directory:
        s3utils.download_all_from_s3_prefix(env.get('input_bucket'), working_directory, env.get('s3_prefix'))
        output_json = validate_entire_dir(env, working_directory)


        with open('kdp_output.json', 'w') as f:
            f.write(json.dumps(output_json))


def parse_env():
    """parse dict of relevant env values from KDP/K8s"""
    inp = json.loads(os.getenv('KDP_INPUT'))
#     output = {
#         'input_bucket': f'{bundle_bucket}',
#         'output_bucket': f'{output_bucket}',
#         'prefix': f'{prefix}',
#     }

    return {
        'validate_bin': os.getenv('VALIDATE_BIN'),
        'validate_ldds': os.getenv('VALIDATE_LDDS'),
        's3_prefix': inp.get('prefix'),
        'input_bucket': inp.get('input_bucket'),
        'output_bucket': inp.get('output_bucket')
    }


def validate_entire_dir(env, working_directory):
    """validate a directory until validate has dealt with all products"""
    # validate inputs
    # `env.get('validate_ldds') or ''` to support running this container without custom LDD overrides
    schematron_glob = glob.glob(os.path.join(env.get('validate_ldds') or '', 'schematron', '*.sch'))
    schema_glob = glob.glob(os.path.join(env.get('validate_ldds') or '', 'schema', '*.xsd'))

    # if validate hit its error limit, parse out pass/fail products and try again until all passed
    done = False
    i = 1
    output = {
        'summaries': [],
        'valid_labels': [],
        'valid_products': [],
        'invalid_labels': [],
        'invalid_products': []
    }
    while not done:
        # call validate on product directory & push json result to s3
        report_name = f'validation_report{i}.json'
        report_json, allValid = validate_dir(env, working_directory, schematron_glob, schema_glob, report_name)

        # push report to s3
        s3utils.push_file_to_s3(env.get('output_bucket'), env.get('s3_prefix'), report_name)
        report_uri = s3utils._local_filepath_to_s3_uri(report_name, env.get('s3_prefix'))

        # summarize this report for aggregates later
        output.get('summaries').append(util.summarize_validation_report(report_json, report_uri, allValid))
        
        passed_labels, passed_products, failed_labels, failed_products = parse_pass_fail(report_json, env.get('s3_prefix'), working_directory) # also prunes the failed from current working dir
        output.get('valid_labels').extend(passed_labels)
        output.get('valid_products').extend(passed_products)
        output.get('invalid_labels').extend(failed_labels)
        output.get('invalid_products').extend(failed_products)

        if not check_max_errors(report_json):
            # validate didn't hit max errors, we're done
            done = True
        else:
            i += 1 # try again

    return json.dumps({
        'summary': util.merge_summaries(output.get('summaries')),
        'valid_labels': output.get('valid_labels'),
        'valid_products': output.get('valid_products'),
        'invalid_labels': output.get('invalid_labels'),
        'invalid_products': output.get('invalid_products')
    })


def check_max_errors(report_json):
    """checks whether the validation report indicates that validate hit its max error count and exited early"""
    max_errors = int(report_json.get('parameters').get('maxErrors'))
    errors_encountered = int(report_json.get('summary').get('totalErrors'))
    return max_errors == errors_encountered


def parse_pass_fail(report_json, s3_prefix, working_directory):
    """parse validation report into dict containing passed and failed products"""
    results = report_json.get('productLevelValidationResults')
    passed = list(filter(lambda x: x.get('status') == 'PASS', results))
    failed = list(filter(lambda x: x.get('status') == 'FAIL', results))
    passed_labels = list(map(lambda x: s3utils._local_filepath_to_s3_uri(x.get('label'), s3_prefix), passed))
    failed_labels = list(map(lambda x: s3utils._local_filepath_to_s3_uri(x.get('label'), s3_prefix), failed))
    failed_local = list(map(lambda x: s3utils._local_filepath_to_s3_uri(x.get('label'), working_directory), failed))
    passed_local = list(map(lambda x: s3utils._local_filepath_to_s3_uri(x.get('label'), working_directory), passed))

    # prune out source products (.IMG, etc) of failed labels in local temp dir
    # this will allow us to reprocess if necessary, and just copy everything over that succeeded
    all_failed_products_from_labels = []
    all_passed_products_from_labels = []

    for passed_label in passed_local:
        products_from_label = util.get_products_from_label(passed_label)
        all_passed_products_from_labels.extend(products_from_label)
        # remove successes so we don't validate them again
        # sys.stderr.write(f'deleting passed: {products_from_label}')
        util.delete_all(products_from_label)

    for failed_label in failed_local:
        products_from_label = util.get_products_from_label(failed_label)
        all_failed_products_from_labels.extend(products_from_label)
        # remove failures so we don't validate again
        # sys.stderr.write(f'deleting failed: {products_from_label}')
        util.delete_all(products_from_label)
    
    # delete passed and failed labels
    util.delete_all(failed_local)
    util.delete_all(passed_local)

    # convert pass/fail products from local to s3 prefix
    passed_products_s3 = list(map(lambda x: s3utils._local_filepath_to_s3_uri(x, s3_prefix), all_passed_products_from_labels))
    failed_products_s3 = list(map(lambda x: s3utils._local_filepath_to_s3_uri(x, s3_prefix), all_failed_products_from_labels))

    return passed_labels, passed_products_s3, failed_labels, failed_products_s3


def validate_dir(env, working_directory, schematron_glob, schema_glob, report_name):
    """validate all products under an s3 prefix (directory)"""

    input_bucket = env.get('input_bucket')
    s3_prefix = env.get('s3_prefix')
    validate_bin = env.get('validate_bin')

    # run validate on the labels
    commands = [
        '/bin/sh', 
        os.path.join(validate_bin, 'validate'), 
        working_directory,      # files to validate
        '-s', 'json',           # json report type
        '-r', report_name       # validation report name
    ]

    # user might not need to specify LDDs, so don't require they be there
    if schematron_glob:
        commands.append('-S')
        commands.extend(schematron_glob) # schematron files
    if schema_glob:
        commands.append('-x')
        commands.extend(schema_glob)     # schema files
        
    proc = subprocess.run(commands, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    # report = open('OUTPUT.TXT', 'r').readlines()[0].rstrip('\n')

    if proc.returncode != 0:
        sys.stderr.write(proc.stdout.decode('utf-8'))
        sys.stderr.flush()

    # extract report summary
    with open(report_name) as report:
        parsed = json.load(report)
        return parsed, proc.returncode == 0


if __name__ == "__main__":
    main()
