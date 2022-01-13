#!/bin/env python3

import os
import json
import redis

def main():
    # env variables from k8s
    hostname = os.getenv('QUEUE_HOSTNAME')
    queue = os.getenv('QUEUE_ID')
    data = json.loads(os.getenv('DATA_JSON'))

    # redis
    r = redis.Redis(host=hostname, port=6379, db=0)

    # push input to queue
    r.lpush(queue, json.dumps(data.get('input')))

if __name__ == "__main__":
    main()