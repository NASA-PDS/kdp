import itertools
import logging
import redis
import json
import os

class Workqueue:

    # TODO: Support multiple input / output queues
    #       which will require output mapping logic
    #       to determine which queue to push output to

    def __init__(self, hostname, inp, out, name, pipeline):
        self.r = redis.Redis(host=hostname, port=6379, db=0, socket_timeout=3)
        self.current_input = None
        self.current_queue = None
        self.input_queue_round_robin = itertools.cycle(inp) # round-robin inputs
        self.hostname = hostname
        self.input = inp
        self.output = out
        self.name = name
        self.pipeline = pipeline

    def next(self):
        self.pop_input()
        
        # TODO: check for poisonpill & shutdown
        return self.current_input
        

    def pop_input(self):
        '''pop input off the input queue and put it into the claimed list'''
        self.current_queue = next(self.input_queue_round_robin)
        work,claimed = self.get_input_queue_ids(self.current_queue)
        # blocking call, wait 1 second for an input
        logging.debug(f"BRPOPLPUSH({work}, {claimed}, timeout=1)")
        self.current_input = self.r.brpoplpush(work, claimed, timeout=1)

    def push_output(self, json):
        '''push output json to output queue(s)'''
        self.release_claim()
        # no outputs, this is the end of the pipeline
        if not self.output:
            return None
        for queue in self.output:
            logging.debug(f"LPUSH({self.get_output_queue_ids(queue)}, {json})")
            self.r.lpush(self.get_output_queue_ids(queue), json)
        return self.output

    def release_claim(self):
        '''remove this input from claimed queue'''
        work,claimed = self.get_input_queue_ids(self.current_queue)
        logging.debug(f"LREM({claimed}, 1, {self.current_input})")
        self.r.lrem(claimed, 1, self.current_input)
        self.current_input = None
        self.current_queue = None

    def get_input_queue_ids(self, input):
        '''construct redis queue ids (work, claimed)'''
        # check if this is the main pipeline input (if the input ID is the pipeline ID):
        prefix = f"{input}" if input == self.pipeline else f"{input}-{self.name}"
        return (f"{prefix}-work", f"{prefix}-claimed")
    
    def get_output_queue_ids(self, output):
        '''construct redis queue id for output'''
        return f"{self.name}-{output}-work"