import logging

LOG_LEVEL = logging.NOTSET
MIN_BLKSIZE = 8
DEF_BLKSIZE = 512
MAX_BLKSIZE = 65536
SOCK_TIMEOUT = 5
MAX_DUPS = 20
TIMEOUT_RETRIES = 5
DEF_TFTP_PORT = 69

# Initialize the logger.
#logging.basicConfig(
#    level=LOG_LEVEL,
#    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
#    datefmt='%m-%d %H:%M:%S')
logging.basicConfig()
# The logger used by this library. Feel free to clobber it with your own, if you like, as
# long as it conforms to Python's logging.
logger = logging.getLogger('tftpy')

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
    global logger
    logger.setLevel(level)
    
class TftpErrors(object):
    """This class is a convenience for defining the common tftp error codes, and making
    them more readable in the code."""
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

class TftpState(object):
    """This class represents a particular state for a TFTP Session. It encapsulates a
    state, kind of like an enum. The states mean the following:
    nil - Client/Server - Session not yet established
    rrq - Client - Just sent RRQ in a download, waiting for response
          Server - Just received an RRQ
    wrq - Client - Just sent WRQ in an upload, waiting for response
          Server - Just received a WRQ
    dat - Client/Server - Transferring data
    oack - Client - Just received oack
           Server - Just sent OACK
    ack - Client - Acknowledged oack, awaiting response
          Server - Just received ACK to OACK
    err - Client/Server - Fatal problems, giving up
    fin - Client/Server - Transfer completed
    """
    states = ['nil',
              'rrq',
              'wrq',
              'dat',
              'oack',
              'ack',
              'err',
              'fin']
    
    def __init__(self, state='nil'):
        self.state = state
        
    def getState(self):
        return self.__state
    
    def setState(self, state):
        if state in TftpState.states:
            self.__state = state
            
    state = property(getState, setState)

class TftpSession(object):
    """This class is the base class for the tftp client and server. Any shared
    code should be in this class."""

    def __init__(self):
        """Class constructor. Note that the state property must be a TftpState
        object."""
        self.options = None
        self.state = TftpState()
        self.dups = 0
        self.errors = 0
        
    def senderror(self, sock, errorcode, address, port):
        """This method uses the socket passed, and uses the errorcode, address and port to
        compose and send an error packet."""
        logger.debug("In senderror, being asked to send error %d to %s:%s"
                % (errorcode, address, port))
        errpkt = TftpPacketERR()
        errpkt.errorcode = errorcode
        self.sock.sendto(errpkt.encode().buffer, (address, port))
