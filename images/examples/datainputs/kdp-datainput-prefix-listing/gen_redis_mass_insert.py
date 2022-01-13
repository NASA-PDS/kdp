# creates the bulk insert file to send over to redis server for parse and ingest
# should be the fastest way to insert 1M+ keys remotely
# docs: https://redis.io/topics/mass-insert

# this datainput pushes a listing of all unique fully-qualified s3 prefixes
# in cases where the s3 prefixes mirror a directory structure, this pushes all directories that contain files

import os
import json
import boto3 

bundle_bucket = json.loads(os.getenv('DATA_JSON'))['bundle_bucket']
bundle_subpath = json.loads(os.getenv('DATA_JSON'))['bundle_subpath']
output_bucket = json.loads(os.getenv('DATA_JSON'))['out_dir']
key_name = os.getenv('QUEUE_ID')

s3 = boto3.resource('s3')
bucket = s3.Bucket(bundle_bucket.replace('s3://', ''))
object_summaries = bucket.objects.filter(Prefix=bundle_subpath) # full objs

# get set of prefixes
prefixes = set()
for obj in object_summaries:
    prefixes.add(os.path.dirname(obj.key))

def gen_redis_proto(cmd):
    proto = '*'+str(len(cmd))+'\r\n'
    for c in cmd:
        proto += '$'+str(len(str(c).encode('utf-8')))+'\r\n'
        proto += c+'\r\n'
    return proto

for prefix in prefixes:
    # input  is s3://{input_bucket}/{prefix}
    # output is s3://{output_bucket}/{prefix}
    output = {
        'input_bucket': f'{bundle_bucket}',
        'output_bucket': f'{output_bucket}',
        'prefix': f'{prefix}',
    }
    print(gen_redis_proto(['LPUSH', key_name, json.dumps(output, separators=(',', ':'))]), end='')
