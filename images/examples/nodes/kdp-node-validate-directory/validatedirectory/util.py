import os
import subprocess

def delete_all(filepath_list):
    """delete all files in list"""
    for filepath in filepath_list:
        try:
            os.remove(filepath)
        except:
            pass # this will happen when error.label.missing_file occurs


def get_products_from_label(label):
    """get all product filepaths associated with a label"""
    dir = os.path.dirname(label) # should be a temp dir

    # need to parse with xmllint, use shell script to avoid having to do that in python
    commands = [
        '/bin/sh', 
        '/opt/local/kdp/scripts/get_products_from_label.sh',
        label
    ]
    proc = subprocess.run(commands, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    
    products = []
    for line in proc.stdout.decode('utf-8').splitlines():
        products.append(os.path.join(dir, line))
    return products


def summarize_validation_report(report_json, report_uri, allValid):
    """product summary json for validation report"""
    summary = report_json.get('summary')
    results = report_json.get('productLevelValidationResults')
    validated_count = len(results)
    pass_count = len(list(filter(lambda x: x.get('status') == 'PASS', results)))
    fail_count = len(list(filter(lambda x: x.get('status') == 'FAIL', results)))
    output = {
        'allValid': allValid,
        'report': report_uri,
        'summary': {
            'validationSummary': summary,
            'productsValidated': validated_count,
            'passCount': pass_count,
            'failCount': fail_count
        }
    }
    return output


def merge_summaries(summaries):
    """merge list of summaries into one complete aggregate summary"""
    # all(somePredicate(elem) for elem in someIterable)
    allValid = all(summary.get('allValid') for summary in summaries)
    reports = list(map(lambda x: x.get('report'), summaries))
    validation_summary = {
        'totalErrors': sum(list(map(lambda x: int(x.get('summary').get('validationSummary').get('totalErrors')), summaries))),
        'totalWarnings': sum(list(map(lambda x: int(x.get('summary').get('validationSummary').get('totalWarnings')), summaries))),
        'messageTypes': _collate_message_types(summaries)
    }
    products_validated = sum(list(map(lambda x: x.get('summary').get('productsValidated'), summaries)))
    pass_count = sum(list(map(lambda x: x.get('summary').get('passCount'), summaries)))
    fail_count = sum(list(map(lambda x: x.get('summary').get('failCount'), summaries)))
    validation_iterations = len(summaries)

    return {
        'allValid': allValid,
        'reports': reports,
        'validation_iterations': validation_iterations,
        'summary': {
            'validationSummary': validation_summary,
            'productsValidated': products_validated,
            'passCount': pass_count,
            'failCount': fail_count
        }
    }
    

def _collate_message_types(summaries):
    """collate different error message types"""
    message_type_count = {}
    for summary in summaries:
        for message in summary.get('summary').get('validationSummary').get('messageTypes'):
            message_type_count[message.get('messageType')] = message_type_count.setdefault(message.get('messageType'), 0) + int(message.get('total'))

    ret = []
    for message_type, total in message_type_count.items():
        ret.append({
            'messageType': message_type,
            'total': total
        })
    return ret