# vim: ts=4 sw=4 et ai:
"""This module holds all objects shared by all other modules in tftpy."""


MIN_BLKSIZE = 8
DEF_BLKSIZE = 512
MAX_BLKSIZE = 65536
SOCK_TIMEOUT = 5
MAX_DUPS = 20
DEF_TIMEOUT_RETRIES = 3
DEF_TFTP_PORT = 69

# A hook for deliberately introducing delay in testing.
DELAY_BLOCK = 0
# A hook to simulate a bad network
NETWORK_UNRELIABILITY = 0
# 0 is disabled, anything positive is the inverse of the percentage of
# dropped traffic. For example, 1000 would cause 0.1% of DAT packets to
# be skipped to simulate lost packets.


def tftpassert(condition, msg):
    """This function is a simple utility that will check the condition
    passed for a false state. If it finds one, it throws a TftpException
    with the message passed. This just makes the code throughout cleaner
    by refactoring."""
    if not condition:
        raise TftpException(msg)


class TftpErrors:
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


class TftpFileNotFoundError(TftpException):
    """This class represents an error condition where we received a file
    not found error."""

    pass
