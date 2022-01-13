#!/usr/bin/env bash

# pipe input to redis
python3 /opt/local/kdp/gen_redis_mass_insert.py | redis-cli -h $QUEUE_HOSTNAME --pipe --pipe-timeout 0