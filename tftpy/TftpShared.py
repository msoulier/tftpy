"""This module holds all objects shared by all other modules in tftpy."""

from __future__ import absolute_import, division, print_function, unicode_literals
import logging
from logging.handlers import RotatingFileHandler

LOG_LEVEL = logging.NOTSET
MIN_BLKSIZE = 8
DEF_BLKSIZE = 512
MAX_BLKSIZE = 65536
SOCK_TIMEOUT = 5
MAX_DUPS = 20
TIMEOUT_RETRIES = 5
DEF_TFTP_PORT = 69

# A hook for deliberately introducing delay in testing.
DELAY_BLOCK = 0

# Initialize the logger.
logging.basicConfig()

# The logger used by this library. Feel free to clobber it with your own, if
# you like, as long as it conforms to Python's logging.
log = logging.getLogger('tftpy')

def create_streamhandler():
    """add create_streamhandler output logging.DEBUG msg to stdout.
    """
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    formatter = logging.Formatter('%(levelname)-8s %(message)s')
    console.setFormatter(formatter)
    return console

def create_rotatingfilehandler(path, maxbytes=10*1024*1024, count=20):
    """
    add create_rotatingfilehandler record the logging.DEBUG msg to logfile. you can change the maxsize (10*1024*1024)
    and amount of the logfiles
    """
    Rthandler = RotatingFileHandler(path, maxbytes, count)
    Rthandler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s')
    Rthandler.setFormatter(formatter)
    return Rthandler

def addHandler(hdlr):
    """add handler methods
    More details see the page:
    https://docs.python.org/2/library/logging.handlers.html#module-logging.handlers
    """
    log.addHandler(hdlr)

def tftpassert(condition, msg):
    """This function is a simple utility that will check the condition
    passed for a false state. If it finds one, it throws a TftpException
    with the message passed. This just makes the code throughout cleaner
    by refactoring."""
    if not condition:
        raise TftpException(msg)

def setLogLevel(level):
    """This function is a utility function for setting the internal log level.
    The log level defaults to logging.NOTSET, so unwanted output to stdout is
    not created."""
    log.setLevel(level)

class TftpErrors(object):
    """This class is a convenience for defining the common tftp error codes,
    and making them more readable in the code."""
    NotDefined = 0
    FileNotFound = 1
    AccessViolation = 2
    DiskFull = 3
    IllegalTftpOp = 4
    UnknownTID = 5
    FileAlreadyExists = 6
    NoSuchUser = 7
    FailedNegotiation = 8

class TftpException(Exception):
    """This class is the parent class of all exceptions regarding the handling
    of the TFTP protocol."""
    pass

class TftpTimeout(TftpException):
    """This class represents a timeout error waiting for a response from the
    other end."""
    pass
