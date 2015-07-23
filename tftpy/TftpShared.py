"""This module holds all objects shared by all other modules in tftpy."""

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
logging.basicConfig(level=logging.DEBUG,
                format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                datefmt='%a, %d %b %Y %H:%M:%S',
                filename='tftp.log',
                filemode='w')
# The logger used by this library. Feel free to clobber it with your own, if you like, as
# long as it conforms to Python's logging.
log = logging.getLogger('tftpy')

def Streamhandler(): 
    """add Streamhandler output logging.DEBUG msg to stdout. 
    """
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    formatter = logging.Formatter('%(levelname)-8s %(message)s')
    console.setFormatter(formatter)
    return console
        
def Rotatingfilehandler():
    """
    add Rotatingfilehandler record the logging.DEBUG msg to logfile. you can change the maxsize (10*1024*1024)
    and amount of the logfiles
    """
    Rthandler = RotatingFileHandler('/tftpboot/tftp.log', maxBytes=10*1024*1024,backupCount=20)
    Rthandler.setLevel(logging.INFO)#maybe logging.INFO is more useful when u debugging.
    formatter = logging.Formatter('%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s')
    Rthandler.setFormatter(formatter)
    return Rthandler
    
def addHandler(hdlr):
    """add handler methods 
    More details see the page:
    https://docs.python.org/2/library/logging.handlers.html#module-logging.handlers
    """
    global log
    log.addHandler(hdlr)

def tftpassert(condition, msg):
    """This function is a simple utility that will check the condition
    passed for a false state. If it finds one, it throws a TftpException
    with the message passed. This just makes the code throughout cleaner
    by refactoring."""
    if not condition:
        raise TftpException, msg

def setLogLevel(level):
    """This function is a utility function for setting the internal log level.
    The log level defaults to logging.NOTSET, so unwanted output to stdout is
    not created."""
    global log
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
