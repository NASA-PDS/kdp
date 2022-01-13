import os
import boto3
import fnmatch

s3 = boto3.resource('s3')
client = boto3.client('s3')


def get_matching_objects_from_s3_prefix(bucket_name, s3_prefix='', regex='*'):
    """Given an S3 prefix and regex pattern, return a list of all matching objects."""
    bucket = s3.Bucket(sanitize_bucket_name(bucket_name))
    object_summaries = bucket.objects.filter(Prefix=s3_prefix)
    return fnmatch.filter(map(lambda object: object.key, object_summaries), regex)


def download_all_from_s3_prefix(bucket_name, working_directory='.', s3_prefix=''):
    """Given an S3 prefix and working directory, download all
    files under that prefix to the working directory"""
    matching_objs = get_matching_objects_from_s3_prefix(bucket_name, s3_prefix)
    _download_object_list(bucket_name, working_directory, matching_objs)


def download_all_xml_from_s3_prefix(bucket_name, working_directory='.', s3_prefix=''):
    """Given an S3 prefix and working directory, download all XML 
    files under that prefix to the working directory"""
    case_insensitive_xml_pattern = '*.[xX][mM][lL]'
    matching_objs = get_matching_objects_from_s3_prefix(bucket_name, s3_prefix, regex=case_insensitive_xml_pattern)
    _download_object_list(bucket_name, working_directory, matching_objs)


def push_file_to_s3(bucket_name, s3_prefix, local_filepath):
    """Push given file to s3 bucket and prefix"""
    s3_uri = _local_filepath_to_s3_uri(local_filepath, s3_prefix)
    client.upload_file(local_filepath, sanitize_bucket_name(bucket_name), s3_uri)


def _download_object_list(bucket_name, working_directory, objs):
    """Download list of s3 objects from given bucket into given directory"""
    for obj in objs:
        client.download_file(sanitize_bucket_name(bucket_name), obj, _s3_to_local_filepath(working_directory, obj))


def _s3_to_local_filepath(directory, s3_uri):
    """Return valid local filepath given a directory and s3 URI"""
    return os.path.join(directory, os.path.basename(s3_uri))


def _local_filepath_to_s3_uri(local_filepath, s3_prefix):
    """Return valid s3 URI given a local filepath and target bucket + prefix"""
    return os.path.join(s3_prefix, os.path.basename(local_filepath))


def sanitize_bucket_name(bucket_name):
    """removes s3:// if present"""
    if bucket_name.startswith('s3://'):
        return bucket_name[5:]
    else:
        return bucket_name