"""This library implements the tftp protocol, based on rfc 1350.
http://www.faqs.org/rfcs/rfc1350.html
At the moment it implements only a client class, but will include a server,
with support for variable block sizes.
"""

import struct, socket, logging, time, sys

# Make sure that this is at least Python 2.4
verlist = sys.version_info
if not verlist[0] >= 2 or not verlist[1] >= 4:
    raise AssertionError, "Requires at least Python 2.4"

# Change this as desired. FIXME - make this a command-line arg
LOG_LEVEL = logging.INFO
MIN_BLKSIZE = 8
DEF_BLKSIZE = 512
MAX_BLKSIZE = 65536
SOCK_TIMEOUT = 5
MAX_DUPS = 20

def tftpassert(condition, msg):
    """This function is a simple utility that will check the condition
    passed for a false state. If it finds one, it throws a TftpException
    with the message passed. This just makes the code throughout cleaner
    by refactoring."""
    if not condition:
        raise TftpException, msg

def setLogLevel(level=LOG_LEVEL):
    """This function is a utility function for setting the internal log level.
    The log level defaults to logging.NOTSET, so unwanted output to stdout is not
    created."""
    global logger
    # Initialize the logger.
    logging.basicConfig(
        level=level,
        format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
        datefmt='%m-%d %H:%M:%S')
    logger = logging.getLogger('tftpy')

# The logger used by this library. Feel free to clobber it with your own, if you like, as
# long as it conforms to Python's logging.
logger = None
# Set up the default logger.
setLogLevel()

class TftpException(Exception):
    """This class is the parent class of all exceptions regarding the handling
    of the TFTP protocol."""
    pass

class TftpPacket(object):
    """This class is the parent class of all tftp packet classes. It is an
    abstract class, providing an interface, and should not be instantiated
    directly."""
    def __init__(self):
        self.opcode = 0
        self.buffer = None

    def encode(self):
        """The encode method of a TftpPacket takes keyword arguments specific
        to the type of packet, and packs an appropriate buffer in network-byte
        order suitable for sending over the wire.
        
        This is an abstract method."""
        raise NotImplementedError, "Abstract method"

    def decode(self):
        """The decode method of a TftpPacket takes a buffer off of the wire in
        network-byte order, and decodes it, populating internal properties as
        appropriate. This can only be done once the first 2-byte opcode has
        already been decoded, but the data section does include the entire
        datagram.
        
        This is an abstract method."""
        raise NotImplementedError, "Abstract method"

    def decode_options(self, buffer):
        """This method decodes the section of the buffer that contains an
        unknown number of options. It returns a dictionary of option names and
        values."""
        nulls = 0
        format = ""
        options = {}

        # Count the nulls in the buffer. Each one terminates a string.
        self.debug("about to iterate options buffer counting nulls")
        length = 0
        for c in buffer:
            if ord(c) == 0:
                self.debug("found a null at length %d" % length)
                if length > 0:
                    format += "%dsx" % length
                    length = 0
                else:
                    raise TftpException, "Invalid options buffer"
            length += 1
                
        # Unpack the buffer.
        mystruct = struct.unpack(format, buffer)
        for key in mystruct:
            self.debug("option name is %s, value is %s" 
                       % (key, mystruct[key]))
        
        tftpassert(len(mystruct) % 2 == 0, 
                   "packet with odd number of option/value pairs")
        
        for i in range(0, len(mystruct), 2):
            options[mystruct[i]] = mystruct[i+1]

        return options

class TftpPacketInitial(TftpPacket):
    """This class is a common parent class for the RRQ and WRQ packets, as 
    they share quite a bit of code."""
    def __init__(self):
        TftpPacket.__init__(self)
        self.filename = None
        self.mode = None
        self.options = {}
        
    def encode(self):
        """Encode the packet's buffer from the instance variables."""
        tftpassert(self.filename, "filename required in initial packet")
        tftpassert(self.mode, "mode required in initial packet")
        
        format = "!H"
        format += "%dsx" % len(self.filename)
        if self.mode == "octet":
            format += "5sx"
        else:
            raise AssertionError, "Unsupported mode: %s" % mode
        # Add options.
        options_list = []
        if self.options.keys() > 0:
            for key in self.options:
                format += "%dsx" % len(key)
                format += "%dsx" % len(self.options[key])
                options_list.append(key)
                options_list.append(self.options[key])
        #format += "B"
        logger.debug("format is %s" % format)
        logger.debug("size of struct is %d" % struct.calcsize(format))

        self.buffer = struct.pack(format, self.opcode, self.filename, self.mode, *options_list)
        return self
    
    def decode(self):
        tftpassert(self.buffer, "Can't decode, buffer is empty")

        # FIXME - this shares a lot of code with decode_options
        nulls = 0
        # 2 byte opcode, followed by filename and mode strings, optionally
        # followed by options.
        format = ""
        nulls = length = tlength = 0
        logger.debug("about to iterate buffer counting nulls")
        for c in self.buffer:
            if ord(c) == 0:
                nulls += 1
                logger.debug("found a null at length %d, now have %d" 
                             % (length, nulls))
                length = 0
                format += "%dsx" % length
                # At 2 nulls, we want to mark that position for decoding.
                if nulls == 2:
                    break
            length += 1
            tlength += 1
        logger.debug("hopefully found end of mode at length %d" % tlength)
        # length should now be the end of the mode.
        tftpassert(nulls == 2, "malformed packet")
        shortbuf = self.buffer[2:tlength]
        mystruct = struct.unpack(format, shortbuf)
        for key in mystruct:
            logger.debug("option name is %s, value is %s" 
                         % (key, mystruct[key]))

        tftpassert(len(mystruct) == 2, "malformed packet")
        self.options = self.decode_options(self.buffer[tlength:])
        return self

class TftpPacketRRQ(TftpPacketInitial):
    """
        2 bytes    string   1 byte     string   1 byte
        -----------------------------------------------
RRQ/  | 01/02 |  Filename  |   0  |    Mode    |   0  |
WRQ    -----------------------------------------------
    """
    def __init__(self):
        TftpPacketInitial.__init__(self)
        self.opcode = 1

class TftpPacketWRQ(TftpPacketInitial):
    """
        2 bytes    string   1 byte     string   1 byte
        -----------------------------------------------
RRQ/  | 01/02 |  Filename  |   0  |    Mode    |   0  |
WRQ    -----------------------------------------------
    """
    def __init__(self):
        TftpPacketInitial.__init__(self)
        self.opcode = 2

class TftpPacketDAT(TftpPacket):
    """
        2 bytes    2 bytes       n bytes
        ---------------------------------
DATA  | 03    |   Block #  |    Data    |
        ---------------------------------
    """
    def __init__(self):
        TftpPacket.__init__(self)
        self.opcode = 3
        self.blocknumber = 0
        self.data = None

    def encode(self):
        """Encode the DAT packet. This method populates self.buffer, and
        returns self for easy method chaining."""
        tftpassert(len(self.data) > 0, "no point encoding empty data packet")
        format = "!HH%ds" % len(self.data)
        self.buffer = struct.pack(format, 
                                  self.opcode, 
                                  self.blocknumber, 
                                  self.data)
        return self

    def decode(self):
        """Decode self.buffer into instance variables. It returns self for
        easy method chaining."""
        # We know the first 2 bytes are the opcode. The second two are the
        # block number.
        (self.blocknumber,) = struct.unpack("!H", self.buffer[2:4])
        logger.info("decoding DAT packet, block number %d" % self.blocknumber)
        logger.debug("should be %d bytes in the packet total" 
                     % len(self.buffer))
        # Everything else is data.
        self.data = self.buffer[4:]
        logger.debug("found %d bytes of data"
                     % len(self.data))
        return self

class TftpPacketACK(TftpPacket):
    """
        2 bytes    2 bytes
        -------------------
ACK   | 04    |   Block #  |
        --------------------
    """
    def __init__(self):
        TftpPacket.__init__(self)
        self.opcode = 4
        self.blocknumber = 0

    def encode(self):
        logger.debug("encoding ACK: opcode = %d, block = %d" 
                     % (self.opcode, self.blocknumber))
        self.buffer = struct.pack("!HH", self.opcode, self.blocknumber)
        return self

    def decode(self):
        self.opcode, self.blocknumber = struct.unpack("!HH", self.buffer)
        logger.debug("decoded ACK packet: opcode = %d, block = %d"
                     % (self.opcode, self.blocknumber))
        return self

class TftpPacketERR(TftpPacket):
    """
        2 bytes  2 bytes        string    1 byte
        ----------------------------------------
ERROR | 05    |  ErrorCode |   ErrMsg   |   0  |
        ----------------------------------------
    Error Codes

    Value     Meaning

    0         Not defined, see error message (if any).
    1         File not found.
    2         Access violation.
    3         Disk full or allocation exceeded.
    4         Illegal TFTP operation.
    5         Unknown transfer ID.
    6         File already exists.
    7         No such user.
    """
    def __init__(self):
        TftpPacket.__init__(self)
        self.opcode = 5
        self.errorcode = 0
        self.errmsg = None
        self.errmsgs = {
            1: "File not found",
            2: "Access violation",
            3: "Disk full or allocation exceeded",
            4: "Illegal TFTP operation",
            5: "Unknown transfer ID",
            6: "File already exists",
            7: "No such user"
            }

    def encode(self):
        """Encode the DAT packet based on instance variables, populating
        self.buffer, returning self."""
        format = "!HH%dsx" % len(self.errmsgs[self.errorcode])
        self.debug("encoding ERR packet with format %s" % format)
        self.buffer = struct.pack(format,
                                  self.opcode,
                                  self.errorcode,
                                  self.errmsgs[self.errorcode])
        return self

    def decode(self):
        "Decode self.buffer, populating instance variables and return self."
        tftpassert(len(self.buffer) >= 5, "malformed ERR packet")
        format = "!HH%dsx" % len(self.buffer)-5
        self.opcode, self.errorcode, self.errmsg = struct.unpack(format, 
                                                                 self.buffer)
        logger.error("ERR packet - errorcode: %d, message: %s"
                     % (errorcode, self.errmsg))
        return self
    
class TftpPacketOACK(TftpPacket):
    """
    #  +-------+---~~---+---+---~~---+---+---~~---+---+---~~---+---+
    #  |  opc  |  opt1  | 0 | value1 | 0 |  optN  | 0 | valueN | 0 |
    #  +-------+---~~---+---+---~~---+---+---~~---+---+---~~---+---+
    """
    def __init__(self):
        TftpPacket.__init__(self)
        self.opcode = 6
        self.options = {}
        
    def encode(self):
        format = "!H" # opcode
        options_list = []
        for key in self.options:
            format += "%dsx" % len(key)
            format += "%dsx" % len(self.options[key])
            options_list.append(key)
            options_list.append(self.options[key])
        self.buffer = struct.pack(format, self.opcode, *options_list)
        return self
    
    def decode(self):
        self.options = self.decode_options(self.buffer[2:])
        return self

class TftpPacketFactory(object):
    """This class generates TftpPacket objects."""
    def __init__(self):
        self.classes = {
            1: TftpPacketRRQ,
            2: TftpPacketWRQ,
            3: TftpPacketDAT,
            4: TftpPacketACK,
            5: TftpPacketERR
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

class TftpState(object):
    """This class represents a particular state for a TFTP Session. It encapsulates a
    state, kind of like an enum. The states mean the following:
    nil - Session not yet established
    rrq - Just sent RRQ in a download, waiting for response
    wrq - Just sent WRQ in an upload, waiting for response
    dat - Transferring data
    oack - Received oack, negotiating options
    ack - Acknowledged oack, awaiting response
    err - Fatal problems, giving up
    fin - Transfer completed
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
        "Class constructor. Note that the state property must be a TftpState object."
        self.options = None
        self.state = TftpState()
        self.dups = 0
        self.errors = 0

class TftpClient(TftpSession):
    """This class is an implementation of a tftp client."""
    def __init__(self, host, port, options):
        """This constructor returns an instance of TftpClient, taking the
        remote host, the remote port, and the filename to fetch."""
        TftpSession.__init__(self)
        self.host = host
        self.port = port
        self.options = options

    def download(self, filename, output, packethook=None):
        """This method initiates a tftp download from the configured remote
        host, requesting the filename passed."""
        # Open the output file.
        outputfile = open(output, "wb")
        recvpkt = None
        curblock = 0
        dups = {}
        start_time = time.time()
        bytes = 0

        tftp_factory = TftpPacketFactory()
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(SOCK_TIMEOUT)

        logger.debug("Sending tftp download request to %s" % self.host)
        pkt = TftpPacketRRQ()
        pkt.filename = filename
        pkt.mode = "octet" # FIXME - shouldn't hardcode this
        sock.sendto(pkt.encode().buffer, (self.host, self.port))
        self.state.state = 'rrq'
        
        while True:
            (buffer, (raddress, rport)) = sock.recvfrom(MAX_BLKSIZE)
            recvpkt = tftp_factory.parse(buffer)

            logger.debug("Received %d bytes from %s:%s" 
                         % (len(buffer), raddress, rport))
            # FIXME - check sender port and ip address
            if isinstance(recvpkt, TftpPacketDAT):
                logger.debug("recvpkt.blocknumber = %d" % recvpkt.blocknumber)
                logger.debug("curblock = %d" % curblock)
                if recvpkt.blocknumber == curblock+1:
                    logger.debug("good, received block %d in sequence" 
                                % recvpkt.blocknumber)
                    curblock += 1
                    # ACK the packet, and save the data.
                    logger.info("sending ACK to block %d" % curblock)
                    logger.debug("ip = %s, port = %s" % (self.host, self.port))
                    ackpkt = TftpPacketACK()
                    ackpkt.blocknumber = curblock
                    sock.sendto(ackpkt.encode().buffer, (self.host, self.port))
                    
                    logger.debug("writing %d bytes to output file" 
                                % len(recvpkt.data))
                    outputfile.write(recvpkt.data)
                    bytes += len(recvpkt.data)
                    # If there is a packethook defined, call it.
                    if packethook:
                        packethook(recvpkt)
                    # Check for end-of-file, any less than full data packet.
                    if len(recvpkt.data) < DEF_BLKSIZE:
                        logger.info("end of file detected")
                        break

                elif recvpkt.blocknumber == curblock:
                    logger.warn("dropping duplicate block %d" % curblock)
                    if dups.has_key(curblock):
                        dups[curblock] += 1
                    else:
                        dups[curblock] = 1
                    tftpassert(dups[curblock] < MAX_DUPS,
                            "Max duplicates for block %d reached" % curblock)
                    logger.debug("ACKing block %d again, just in case" % curblock)
                    ackpkt = TftpPacketACK()
                    ackpkt.blocknumber = curblock
                    sock.sendto(ackpkt.encode().buffer, (self.host, self.port))

                else:
                    msg = "Whoa! Received block %d but expected %d" % (recvpkt.blocknumber, 
                                                                    curblock+1)
                    logger.error(msg)
                    raise TftpException, msg

            # Check other packet types.
            elif isinstance(recvpkt, TftpPacketOACK):
                tftpassert(False, "Options currently unsupported")

            elif isinstance(recvpkt, TftpPacketACK):
                # Umm, we ACK, the server doesn't.
                tftpassert(False, "Received ACK from server while in download")

            elif isinstance(recvpkt, TftpPacketERR):
                tftpassert(False, "Received ERR from server: " + recvpkt)

            elif isinstance(recvpkt, TftpPacketWRQ):
                tftpassert(False, "Received WRQ from server: " + recvpkt)

            else:
                tftpassert(False, "Received unknown packet type from server: "
                        + recvpkt)


        # end while

        end_time = time.time()
        duration = end_time - start_time
        outputfile.close()
        logger.info("Downloaded %d bytes in %d seconds" % (bytes, duration))
        bps = (bytes * 8.0) / duration
        kbps = bps / 1024.0
        logger.info("Average rate: %.2f kbps" % kbps)
        dupcount = 0
        for key in dups:
            dupcount += dups[key]
        logger.info("Received %d duplicate packets" % dupcount)
