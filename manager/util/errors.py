class UtilError(Exception):
    """Base class for exceptions in the util module."""
    pass

class MaxTriesExceededError(UtilError):
    """Exception raised when max tries for a function call have been exceeded.
    
    Attributes:
        tries -- number of times function call was tried
        exception -- exception encountered on the final try
        message -- explanation of the error
    """

    def __init__(self, tries, exception, message):
        self.tries = tries
        self.exception = exception
        self.message = message

class SubprocessReturnedError(UtilError):
    """Exception raised when a subprocess returned an error.

    Attributes:
        err_code -- return code of the failed subprocess
        message -- explanation of the error
    """

    def __init__(self, err_code, message):
        self.err_code = err_code
        self.message = message

class FileNotFoundError(UtilError):
    """Exception raised when file could not be found.

    Attributes:
        message -- explanation of the error
        filepath -- file that could not be found
    """

    def __init__(self, message, filepath):
        self.message = message
        self.filepath = filepath

class InvalidJSONFormatError(UtilError):
    """Exception raised when file is not valid JSON.

    Attributes:
        message -- explanation of the error
        filepath -- file that was invalid JSON
    """

    def __init__(self, message, filepath):
        self.message = message
        self.filepath = filepath