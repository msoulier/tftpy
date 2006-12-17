from TftpShared import *
from TftpPacketTypes import *

class TftpPacketFactory(object):
    """This class generates TftpPacket objects."""
    def __init__(self):
        self.classes = {
            1: TftpPacketRRQ,
            2: TftpPacketWRQ,
            3: TftpPacketDAT,
            4: TftpPacketACK,
            5: TftpPacketERR,
            6: TftpPacketOACK
            }

    def create(self, opcode):
        tftpassert(self.classes.has_key(opcode), 
                   "Unsupported opcode: %d" % opcode)

        packet = self.classes[opcode]()

        logger.debug("packet is %s" % packet)
        return packet

    def parse(self, buffer):
        """This method is used to parse an existing datagram into its
        corresponding TftpPacket object."""
        logger.debug("parsing a %d byte packet" % len(buffer))
        (opcode,) = struct.unpack("!H", buffer[:2])
        logger.debug("opcode is %d" % opcode)
        packet = self.create(opcode)
        packet.buffer = buffer
        return packet.decode()
