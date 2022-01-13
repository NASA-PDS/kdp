import time
import logging
import subprocess
from . import errors
import json
import os

def try_with_exponential_backoff(func, err_class, err_msg, max_tries):
    """
    Runs funct until it returns with a value, retrying with exponential backoff on occurrence of specified error class (or subtype thereof).
    Prints err_msg whenever func is retried. Will retry func up to max_tries, resulting in (2^max_tries) total wait (s).
    """
    tries = 0
    while True:
        try:
            return func()
        except Exception as e:
            exception_name = type(e).__name__
            if issubclass(type(e), err_class):
                if tries < max_tries:
                    logging.error(f"{err_msg} Encountered {exception_name}. Retrying after {2**tries} seconds.")
                    time.sleep(2**tries)
                    tries += 1
                else:
                    raise errors.MaxTriesExceededError(tries, exception_name, e)
            else:
                raise

def run_commands_in_subprocess(commands, env, cwd):
    """
    Run specified list of commands, given provided env, in specified working directory cwd.

    Returns subprocess stdout and stderr on success, determined by return code of zero (0).
    
    Raises the following exceptions:
        - SubprocessReturnedError exception on subprocess error.
    """
    proc = subprocess.run(commands, env=env, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if proc.returncode == 0:
        return (proc.stdout.decode('utf-8'), proc.stderr.decode('utf-8'))
    else:
        raise errors.SubprocessReturnedError(proc.returncode, proc.stderr.decode('utf-8'))

def load_json_file(dir, filename):
    """
    Ensure that filename exists in dir, and is formatted as proper JSON.
    
    Raises the following exceptions:
        - FileNotFoundError exception on filename not found.
        - InvalidJSONFormatError exception on filename not valid JSON.
    """
    filepath = os.path.join(dir, filename)
    try: 
        with open(filepath) as f:
            return json.load(f)
    except IOError as e:
        raise errors.FileNotFoundError(f"Could not find / open file. Details: {e}", filepath)
    except ValueError as e:
        raise errors.InvalidJSONFormatError(f"File does not contain valid JSON! Details: {e}", filepath)