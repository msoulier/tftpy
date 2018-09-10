# vim: ts=4 sw=4 et ai:
# -*- coding: utf8 -*-
"""
This library implements the tftp protocol, based on rfc 1350.
http://www.faqs.org/rfcs/rfc1350.html
At the moment it implements only a client class, but will include a server,
with support for variable block sizes.

As a client of tftpy, this is the only module that you should need to import
directly. The TftpClient and TftpServer classes can be reached through it.
"""


import sys

# Make sure that this is at least Python 2.7
required_version = (2, 7)
if sys.version_info < required_version:
    raise ImportError("Requires at least Python 2.7")

from .TftpShared import *
from . import TftpPacketTypes
from . import TftpPacketFactory
from .TftpClient import TftpClient
from .TftpServer import TftpServer
from . import TftpContexts
from . import TftpStates
