"""
This library implements the tftp protocol, based on rfc 1350.
http://www.faqs.org/rfcs/rfc1350.html
At the moment it implements only a client class, but will include a server,
with support for variable block sizes.

As a client of tftpy, this is the only module that you should need to import
directly. The TftpClient and TftpServer classes can be reached through it.
"""

from __future__ import absolute_import, division, print_function, unicode_literals
import sys

# Make sure that this is at least Python 2.6
required_version = (2, 6)
if sys.version_info < required_version:
    raise ImportError("Requires at least Python 2.6")

from .TftpShared import *
from . import TftpPacketTypes
from . import TftpPacketFactory
from . import TftpClient
from . import TftpServer
from . import TftpContexts
from . import TftpStates
