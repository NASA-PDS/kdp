#!/bin/env python3

from inputhandler import InputHandler
import logging
import json
import sys
import os

def main():
    # logging
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s %(message)s')

    # env variables from k8s
    HOSTNAME = os.getenv('QUEUE_HOSTNAME')
    INPUT = json.loads(os.getenv('QUEUE_INPUT'))
    OUTPUT = json.loads(os.getenv('QUEUE_OUTPUT'))
    NAME = os.getenv('CONTAINER_NAME')
    PIPELINE = os.getenv('PIPELINE_ID')

    # commands to run in subprocess come as input to this script
    commands = sys.argv[1:]

    input_handler = InputHandler(HOSTNAME, INPUT, OUTPUT, NAME, PIPELINE, commands)

    # TODO: shutdown on poisonpill
    while True:
        input_handler.process_next_input()
        
if __name__ == "__main__":
    main()