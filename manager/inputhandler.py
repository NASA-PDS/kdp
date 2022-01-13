from workqueue import Workqueue
from util import util, errors
from redis.exceptions import RedisError
import subprocess
import tempfile
import logging
import json
import sys
import os

class InputHandler:

    def __init__(self, hostname, inp, out, name, pipeline, commands):
        """Initialize InputHandler class instances"""
        self.workqueue = Workqueue(hostname, inp, out, name, pipeline)
        self.hostname = hostname
        self.input = inp
        self.output = out
        self.name = name
        self.pipeline = pipeline
        self.commands = commands

    def process_next_input(self):
        """Process the next input on the input queue.
        Runs a subprocess for each input, using the specified commands. 
    
        Input is provided to subprocess in two ways:
            - As the KDP_INPUT environment variable
            - As the kdp_input.json file in the subprocess's working directory

        Will retry failed redis connection with exponential backoff (up to approx 1 hour), and push output to configured output queues upon success
        """
        inp = self.get_next_with_retries()

        # try again on no input
        if inp == None:
            logging.debug(f"No input from queues ({self.input}), continuing...")
            return

        with tempfile.TemporaryDirectory() as tmpdirname:

            # supply input both as env var and local file
            with open(os.path.join(tmpdirname, 'kdp_input.json'), "wb") as infile:
                infile.write(inp)

            # copy os env & add input to it
            env = os.environ.copy()
            env['KDP_INPUT'] = inp.decode('utf-8')

            # spawn a subprocess for this task
            logging.info(f"Spawning process for input: {inp}")
            logging.debug(f"COMMANDS: {self.commands} ENV: {env} CWD: {tmpdirname}")
            try:
                stdout, stderr = util.run_commands_in_subprocess(self.commands, env, tmpdirname)
                output = util.load_json_file(tmpdirname, 'kdp_output.json') # check expected output
                logging.info(f"Subprocess returned output: {output}")
                # pass output down the line
                self.push_output(output)
            except errors.SubprocessReturnedError as e:
                logging.error(f"Subprocess finished with non-zero exit code: {e.err_code}. Details: {e.message}")
            except errors.FileNotFoundError as e:
                logging.error(f"Could not read subprocess output file ({e.filepath}). Details: {e.message}")
            except errors.InvalidJSONFormatError as e:
                logging.error(f"Subprocess output file ({e.filepath}) is not valid JSON! Details: {e.message}")


    def get_next_with_retries(self):
        """Try to get the next input from the queue using retries & exponential backoff"""
        try: 
            return util.try_with_exponential_backoff(self.workqueue.next, RedisError, "Unable to connect to redis.", 12) # 12 gives approx 1 hour
        except errors.MaxTriesExceededError as e:
            logging.error(f"Failed to get next queue input after {e.tries} tries, encountered {e.exception}. Details: {e.message}")
            sys.exit(1) # fatal, trigger pod restart
        except Exception as e:
            print(type(e))
            logging.error(f"Unknown error occurred while getting queue input. Details: {e}")
            sys.exit(1) # fatal, trigger pod restart

    def push_output(self, output):
        """Push pipeline output to output queues"""
        queues_pushed = self.workqueue.push_output(json.dumps(output))
        if queues_pushed:
            logging.info(f"Pushed output to queues: {queues_pushed}")
        else:
            logging.info(f"End of pipeline. Final output: {output}")