# vim: ts=4 sw=4 et ai:
# -*- coding: utf8 -*-
"""This module implements the TftpPacketFactory class, which can take a binary
buffer, and return the appropriate TftpPacket object to represent it, via the
parse() method."""


from .TftpShared import *
from .TftpPacketTypes import *
import logging

log = logging.getLogger('tftpy.TftpPacketFactory')

class TftpPacketFactory(object):
    """This class generates TftpPacket objects. It is responsible for parsing
    raw buffers off of the wire and returning objects representing them, via
    the parse() method."""
    def __init__(self):
        self.classes = {
            1: TftpPacketRRQ,
            2: TftpPacketWRQ,
            3: TftpPacketDAT,
            4: TftpPacketACK,
            5: TftpPacketERR,
            6: TftpPacketOACK
            }

    def parse(self, buffer):
        """This method is used to parse an existing datagram into its
        corresponding TftpPacket object. The buffer is the raw bytes off of
        the network."""
        log.debug("parsing a %d byte packet" % len(buffer))
        (opcode,) = struct.unpack(str("!H"), buffer[:2])
        log.debug("opcode is %d" % opcode)
        packet = self.__create(opcode)
        packet.buffer = buffer
        return packet.decode()

    def __create(self, opcode):
        """This method returns the appropriate class object corresponding to
        the passed opcode."""
        tftpassert(opcode in self.classes,
                   "Unsupported opcode: %d" % opcode)

        packet = self.classes[opcode]()

        return packet
