"""This library implements the tftp protocol, based on rfc 1350.
http://www.faqs.org/rfcs/rfc1350.html
At the moment it implements only a client class, but will include a server,
with support for variable block sizes.
"""

import sys

# Make sure that this is at least Python 2.3
verlist = sys.version_info
if not verlist[0] >= 2 or not verlist[1] >= 3:
    raise AssertionError, "Requires at least Python 2.3"

from TftpShared import *
from TftpPacketTypes import *
from TftpPacketFactory import *
from TftpClient import *
from TftpServer import *
