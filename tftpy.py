"""This library implements the tftp protocol, based on rfc 1350.
http://www.faqs.org/rfcs/rfc1350.html
At the moment it implements only a client class, but will include a server,
with support for variable block sizes.
"""

import struct, socket, logging, time, sys, types, re, random, os

# Make sure that this is at least Python 2.4
verlist = sys.version_info
if not verlist[0] >= 2 or not verlist[1] >= 4:
    raise AssertionError, "Requires at least Python 2.4"

LOG_LEVEL = logging.NOTSET
MIN_BLKSIZE = 8
DEF_BLKSIZE = 512
MAX_BLKSIZE = 65536
SOCK_TIMEOUT = 5
MAX_DUPS = 20
TIMEOUT_RETRIES = 5
DEF_TFTP_PORT = 69

# Initialize the logger.
logging.basicConfig(
    level=LOG_LEVEL,
    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
    datefmt='%m-%d %H:%M:%S')
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

class TftpPacketWithOptions(object):
    """This class exists to permit some TftpPacket subclasses to share code
    regarding options handling. It does not inherit from TftpPacket, as the
    goal is just to share code here, and not cause diamond inheritance."""
    def __init__(self):
        self.options = None

    def setoptions(self, options):
        logger.debug("in TftpPacketWithOptions.setoptions")
        logger.debug("options: " + str(options))
        myoptions = {}
        for key in options:
            newkey = str(key)
            myoptions[newkey] = str(options[key])
            logger.debug("populated myoptions with %s = %s"
                         % (newkey, myoptions[newkey]))

        logger.debug("setting options hash to: " + str(myoptions))
        self.__options = myoptions

    def getoptions(self):
        logger.debug("in TftpPacketWithOptions.getoptions")
        return self.__options

    # Set up getter and setter on options to ensure that they are the proper
    # type. They should always be strings, but we don't need to force the
    # client to necessarily enter strings if we can avoid it.
    options = property(getoptions, setoptions)

    def decode_options(self, buffer):
        """This method decodes the section of the buffer that contains an
        unknown number of options. It returns a dictionary of option names and
        values."""
        nulls = 0
        format = "!"
        options = {}

        logger.debug("decode_options: buffer is: " + repr(buffer))
        logger.debug("size of buffer is %d bytes" % len(buffer))
        if len(buffer) == 0:
            logger.debug("size of buffer is zero, returning empty hash")
            return {}

        # Count the nulls in the buffer. Each one terminates a string.
        logger.debug("about to iterate options buffer counting nulls")
        length = 0
        for c in buffer:
            #logger.debug("iterating this byte: " + repr(c))
            if ord(c) == 0:
                logger.debug("found a null at length %d" % length)
                if length > 0:
                    format += "%dsx" % length
                    length = -1
                else:
                    raise TftpException, "Invalid options in buffer"
            length += 1
                
        logger.debug("about to unpack, format is: %s" % format)
        mystruct = struct.unpack(format, buffer)
        
        tftpassert(len(mystruct) % 2 == 0, 
                   "packet with odd number of option/value pairs")
        
        for i in range(0, len(mystruct), 2):
            logger.debug("setting option %s to %s" % (mystruct[i], mystruct[i+1]))
            options[mystruct[i]] = mystruct[i+1]

        return options

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

class TftpPacketInitial(TftpPacket, TftpPacketWithOptions):
    """This class is a common parent class for the RRQ and WRQ packets, as 
    they share quite a bit of code."""
    def __init__(self):
        TftpPacket.__init__(self)
        self.filename = None
        self.mode = None
        
    def encode(self):
        """Encode the packet's buffer from the instance variables."""
        tftpassert(self.filename, "filename required in initial packet")
        tftpassert(self.mode, "mode required in initial packet")

        ptype = None
        if self.opcode == 1: ptype = "RRQ"
        else:                ptype = "WRQ"
        logger.debug("Encoding %s packet, filename = %s, mode = %s"
                     % (ptype, self.filename, self.mode))
        for key in self.options:
            logger.debug("    Option %s = %s" % (key, self.options[key]))
        
        format = "!H"
        format += "%dsx" % len(self.filename)
        if self.mode == "octet":
            format += "5sx"
        else:
            raise AssertionError, "Unsupported mode: %s" % mode
        # Add options.
        options_list = []
        if self.options.keys() > 0:
            logger.debug("there are options to encode")
            for key in self.options:
                format += "%dsx" % len(key)
                format += "%dsx" % len(str(self.options[key]))
                options_list.append(key)
                options_list.append(str(self.options[key]))

        logger.debug("format is %s" % format)
        logger.debug("size of struct is %d" % struct.calcsize(format))

        self.buffer = struct.pack(format,
                                  self.opcode,
                                  self.filename,
                                  self.mode,
                                  *options_list)

        logger.debug("buffer is " + repr(self.buffer))
        return self
    
    def decode(self):
        tftpassert(self.buffer, "Can't decode, buffer is empty")

        # FIXME - this shares a lot of code with decode_options
        nulls = 0
        format = ""
        nulls = length = tlength = 0
        logger.debug("in decode: about to iterate buffer counting nulls")
        subbuf = self.buffer[2:]
        for c in subbuf:
            logger.debug("iterating this byte: " + repr(c))
            if ord(c) == 0:
                nulls += 1
                logger.debug("found a null at length %d, now have %d" 
                             % (length, nulls))
                format += "%dsx" % length
                length = -1
                # At 2 nulls, we want to mark that position for decoding.
                if nulls == 2:
                    break
            length += 1
            tlength += 1

        logger.debug("hopefully found end of mode at length %d" % tlength)
        # length should now be the end of the mode.
        tftpassert(nulls == 2, "malformed packet")
        shortbuf = subbuf[:tlength+1]
        logger.debug("about to unpack buffer with format: %s" % format)
        logger.debug("unpacking buffer: " + repr(shortbuf))
        mystruct = struct.unpack(format, shortbuf)

        tftpassert(len(mystruct) == 2, "malformed packet")
        logger.debug("setting filename to %s" % mystruct[0])
        logger.debug("setting mode to %s" % mystruct[1])
        self.filename = mystruct[0]
        self.mode = mystruct[1]

        self.options = self.decode_options(subbuf[tlength+1:])
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
        if len(self.data) == 0:
            logger.debug("Encoding an empty DAT packet")
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
        logger.debug("decoding DAT packet, block number %d" % self.blocknumber)
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
    8         Failed to negotiate options
    """
    def __init__(self):
        TftpPacket.__init__(self)
        self.opcode = 5
        self.errorcode = 0
        self.errmsg = None
        # FIXME - integrate in TftpErrors references?
        self.errmsgs = {
            1: "File not found",
            2: "Access violation",
            3: "Disk full or allocation exceeded",
            4: "Illegal TFTP operation",
            5: "Unknown transfer ID",
            6: "File already exists",
            7: "No such user",
            8: "Failed to negotiate options"
            }

    def encode(self):
        """Encode the DAT packet based on instance variables, populating
        self.buffer, returning self."""
        format = "!HH%dsx" % len(self.errmsgs[self.errorcode])
        logger.debug("encoding ERR packet with format %s" % format)
        self.buffer = struct.pack(format,
                                  self.opcode,
                                  self.errorcode,
                                  self.errmsgs[self.errorcode])
        return self

    def decode(self):
        "Decode self.buffer, populating instance variables and return self."
        tftpassert(len(self.buffer) >= 5, "malformed ERR packet")
        format = "!HH%dsx" % (len(self.buffer) - 5)
        self.opcode, self.errorcode, self.errmsg = struct.unpack(format, 
                                                                 self.buffer)
        logger.error("ERR packet - errorcode: %d, message: %s"
                     % (self.errorcode, self.errmsg))
        return self
    
class TftpPacketOACK(TftpPacket, TftpPacketWithOptions):
    """
    #  +-------+---~~---+---+---~~---+---+---~~---+---+---~~---+---+
    #  |  opc  |  opt1  | 0 | value1 | 0 |  optN  | 0 | valueN | 0 |
    #  +-------+---~~---+---+---~~---+---+---~~---+---+---~~---+---+
    """
    def __init__(self):
        TftpPacket.__init__(self)
        self.opcode = 6
        
    def encode(self):
        format = "!H" # opcode
        options_list = []
        logger.debug("in TftpPacketOACK.encode")
        for key in self.options:
            logger.debug("looping on option key %s" % key)
            logger.debug("value is %s" % self.options[key])
            format += "%dsx" % len(key)
            format += "%dsx" % len(self.options[key])
            options_list.append(key)
            options_list.append(self.options[key])
        self.buffer = struct.pack(format, self.opcode, *options_list)
        return self
    
    def decode(self):
        self.options = self.decode_options(self.buffer[2:])
        return self
    
    def match_options(self, options):
        """This method takes a set of options, and tries to match them with
        its own. It can accept some changes in those options from the server as
        part of a negotiation. Changed or unchanged, it will return a dict of
        the options so that the session can update itself to the negotiated
        options."""
        for name in self.options:
            if options.has_key(name):
                if name == 'blksize':
                    # We can accept anything between the min and max values.
                    size = self.options[name]
                    if size >= MIN_BLKSIZE and size <= MAX_BLKSIZE:
                        logger.debug("negotiated blksize of %d bytes" % size)
                        options[blksize] = size
                else:
                    raise TftpException, "Unsupported option: %s" % name
        return True

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
        #import pdb
        #pdb.set_trace()
        errpkt = TftpPacketERR()
        errpkt.errorcode = errorcode
        self.sock.sendto(errpkt.encode().buffer, (address, port))

class TftpServer(TftpSession):
    """This class implements a tftp server object."""

    def __init__(self, tftproot='/tftpboot'):
        """Class constructor. It takes a single optional argument, which is
        the path to the tftproot directory to serve files from and/or write
        them to."""
        self.listenip = None
        self.listenport = None
        self.sock = None
        self.root = tftproot
        # A dict of handlers, where each session is keyed by a string like
        # ip:tid for the remote end.
        self.handlers = {}

        if os.path.exists(self.root):
            logger.debug("tftproot %s does exist" % self.root)
            if not os.path.isdir(self.root):
                raise TftpException, "The tftproot must be a directory."
            else:
                logger.debug("tftproot %s is a directory" % self.root)
                if os.access(self.root, os.R_OK):
                    logger.debug("tftproot %s is readable" % self.root)
                else:
                    raise TftpException, "The tftproot must be readable"
                if os.access(self.root, os.W_OK):
                    logger.debug("tftproot %s is writable" % self.root)
                else:
                    logger.warning("The tftproot %s is not writable" % self.root)
        else:
            raise TftpException, "The tftproot does not exist."

    def listen(self,
               listenip="",
               listenport=DEF_TFTP_PORT,
               timeout=SOCK_TIMEOUT):
        """Start a server listening on the supplied interface and port. This
        defaults to INADDR_ANY (all interfaces) and UDP port 69. You can also
        supply a different socket timeout value, if desired."""
        import select
        
        tftp_factory = TftpPacketFactory()
        
        logger.info("Server requested on ip %s, port %s"
                % (listenip if listenip else '0.0.0.0', listenport))
        try:
            # FIXME - sockets should be non-blocking?
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.sock.bind((listenip, listenport))
        except socket.error, err:
            # Reraise it for now.
            raise

        logger.info("Starting receive loop...")
        while True:
            # Build the inputlist array of sockets to select() on.
            inputlist = []
            inputlist.append(self.sock)
            for key in self.handlers:
                inputlist.append(self.handlers[key].sock)
                
            # Block until some socket has input on it.
            logger.debug("Performing select on this inputlist: %s" % inputlist)
            readyinput, readyoutput, readyspecial = select.select(inputlist,
                                                                  [],
                                                                  [],
                                                                  SOCK_TIMEOUT)
            
            #(buffer, (raddress, rport)) = self.sock.recvfrom(MAX_BLKSIZE)
            #recvpkt = tftp_factory.parse(buffer)
            #key = "%s:%s" % (raddress, rport)

            deletion_list = []
            
            for readysock in readyinput:
                if readysock == self.sock:
                    logger.debug("Data ready on our main socket")
                    buffer, (raddress, rport) = self.sock.recvfrom(MAX_BLKSIZE)
                    logger.debug("Read %d bytes" % len(buffer))
                    recvpkt = tftp_factory.parse(buffer)
                    key = "%s:%s" % (raddress, rport)

                    if isinstance(recvpkt, TftpPacketRRQ):
                        logger.debug("RRQ packet from %s:%s" % (raddress, rport))
                        if not self.handlers.has_key(key):
                            try:
                                logger.debug("New download request, session key = %s"
                                        % key)
                                self.handlers[key] = TftpServerHandler(key,
                                                                       TftpState('rrq'),
                                                                       self.root,
                                                                       listenip,
                                                                       tftp_factory)
                                self.handlers[key].handle((recvpkt, raddress, rport))
                            except TftpException, err:
                                logger.error("Fatal exception thrown from handler: %s"
                                        % str(err))
                                logger.debug("Deleting handler: %s" % key)
                                deletion_list.append(key)

                        else:
                            logger.warn("Received RRQ for existing session!")
                            self.senderror(self.sock,
                                           TftpErrors.IllegalTftpOp,
                                           raddress,
                                           rport)
                            continue
                        
                    elif isinstance(recvpkt, TftpPacketWRQ):
                        logger.error("Write requests not implemented at this time.")
                        self.senderror(self.sock,
                                       TftpErrors.IllegalTftpOp,
                                       raddress,
                                       rport)
                        continue
                    else:
                        # FIXME - this will have to change if we do symmetric UDP
                        logger.error("Should only receive RRQ or WRQ packets "
                                     "on main listen port. Received %s" % recvpkt)
                        self.senderror(self.sock,
                                       TftpErrors.IllegalTftpOp,
                                       raddress,
                                       rport)
                        continue
                    
                else:
                    for key in self.handlers:
                        if readysock == self.handlers[key].sock:
                            # FIXME - violating DRY principle with above code
                            try:
                                self.handlers[key].handle()
                                break
                            except TftpException, err:
                                deletion_list.append(key)
                                if self.handlers[key].state.state == 'fin':
                                    logger.info("Successful transfer.")
                                    break
                                else:
                                    logger.error("Fatal exception thrown from handler: %s"
                                            % str(err))

                    else:
                        logger.error("Can't find the owner for this packet.  Discarding.")

            logger.debug("Looping on all handlers to check for timeouts")
            now = time.time()
            for key in self.handlers:
                try:
                    self.handlers[key].check_timeout(now)
                except TftpException, err:
                    logger.error("Fatal exception thrown from handler: %s"
                            % str(err))
                    deletion_list.append(key)

            logger.debug("Iterating deletion list.")
            for key in deletion_list:
                if self.handlers.has_key(key):
                    logger.debug("Deleting handler %s" % key)
                    del self.handlers[key]
            deletion_list = []

class TftpServerHandler(TftpSession):
    """This class implements a handler for a given server session, handling
    the work for one download."""

    def __init__(self, key, state, root, listenip, factory):
        TftpSession.__init__(self)
        logger.info("Starting new handler. Key %s." % key)
        self.key = key
        self.host, self.port = self.key.split(':')
        self.port = int(self.port)
        self.listenip = listenip
        # Note, correct state here is important as it tells the handler whether it's
        # handling a download or an upload.
        self.state = state
        self.root = root
        self.mode = None
        self.filename = None
        self.sock = False
        self.options = {}
        self.blocknumber = 0
        self.buffer = None
        self.fileobj = None
        self.timesent = 0
        self.timeouts = 0
        self.tftp_factory = factory
        count = 0
        while not self.sock:
            self.sock = self.gensock(listenip)
            count += 1
            if count > 10:
                raise TftpException, "Failed to bind this handler to any port"

    def check_timeout(self, now):
        """This method checks to see if we've timed-out waiting for traffic
        from the client."""
        if self.timesent:
            if now - self.timesent > SOCK_TIMEOUT:
                self.timeout()

    def timeout(self):
        """This method handles a timeout condition."""
        logger.debug("Handling timeout for handler %s" % self.key)
        self.timeouts += 1
        if self.timeouts > TIMEOUT_RETRIES:
            raise TftpException, "Hit max retries, giving up."

        # FIXME - still need to handle Sorceror's Apprentice problem

        if self.state.state == 'dat' or self.state.state == 'fin':
            logger.debug("Timing out on DAT. Need to resend.")
            self.send_dat(resend=True)
        elif self.state.state == 'oack':
            logger.debug("Timing out on OACK. Need to resend.")
            self.send_oack()
        else:
            tftpassert(False,
                       "Timing out in unsupported state %s" %
                       self.state.state)

    def gensock(self, listenip):
        """This method generates a new UDP socket, whose listening port must
        be randomly generated, and not conflict with any already in use. For
        now, let the OS do this."""
        random.seed()
        port = random.randrange(1025, 65536)
        # FIXME - sockets should be non-blocking?
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        logger.debug("Trying a handler socket on port %d" % port)
        try:
            sock.bind((listenip, port))
            return sock
        except socket.error, err:
            if err[0] == 98:
                logger.warn("Handler %s, port %d was already taken" % (self.key, port))
                return False
            else:
                raise

    def handle(self, pkttuple=None):
        """This method informs a handler instance that it has data waiting on
        its socket that it must read and process."""
        recvpkt = raddress = rport = None
        if pkttuple:
            logger.debug("Handed pkt %s for handler %s" % (recvpkt, self.key))
            recvpkt, raddress, rport = pkttuple
        else:
            logger.debug("Data ready for handler %s" % self.key)
            buffer, (raddress, rport) = self.sock.recvfrom(MAX_BLKSIZE)
            logger.debug("Read %d bytes" % len(buffer))
            recvpkt = self.tftp_factory.parse(buffer)
            
        # FIXME - refactor into another method, this is too big
        if isinstance(recvpkt, TftpPacketRRQ):
            logger.debug("Handler %s received RRQ packet" % self.key)
            logger.debug("Requested file is %s, mode is %s" % (recvpkt.filename,
                                                               recvpkt.mode))
            # FIXME - only octet mode is supported at this time.
            if recvpkt.mode != 'octet':
                self.senderror(self.sock,
                               TftpErrors.IllegalTftpOp,
                               raddress,
                               rport)
                raise TftpException, "Unsupported mode: %s" % recvpkt.mode

            if self.state.state == 'rrq':
                logger.debug("Received RRQ. Composing response.")
                self.filename = self.root + os.sep + recvpkt.filename
                logger.debug("The path to the desired file is %s" %
                        self.filename)
                self.filename = os.path.abspath(self.filename)
                logger.debug("The absolute path is %s" % self.filename)
                # Security check. Make sure it's prefixed by the tftproot.
                if re.match(r'%s' % self.root, self.filename):
                    logger.debug("The path appears to be safe: %s" %
                            self.filename)
                else:
                    logger.error("Insecure path: %s" % self.filename)
                    self.errors += 1
                    self.senderror(self.sock,
                                   TftpErrors.AccessViolation,
                                   raddress,
                                   rport)
                    raise TftpException, "Insecure path: %s" % self.filename

                # Does the file exist?
                if os.path.exists(self.filename):
                    logger.debug("File %s exists." % self.filename)

                    # Check options. Currently we only support the blksize
                    # option.
                    if recvpkt.options.has_key('blksize'):
                        logger.debug("RRQ includes a blksize option")
                        blksize = int(recvpkt.options['blksize'])
                        if blksize >= MIN_BLKSIZE and blksize <= MAX_BLKSIZE:
                            logger.debug("Client requested blksize = %d"
                                    % blksize)
                            self.options['blksize'] = blksize
                        else:
                            logger.warning("Client %s requested invalid "
                                           "blocksize %d, responding with default"
                                           % (self.key, blksize))
                            self.options['blksize'] = DEF_BLKSIZE

                        logger.debug("Composing and sending OACK packet")
                        self.send_oack()

                    elif len(recvpkt.options.keys()) > 0:
                        logger.warning("Client %s requested unsupported options: %s"
                                % (self.key, recvpkt.options))
                        logger.warning("Responding with negotiation error")
                        self.senderror(self.sock,
                                       TftpErrors.FailedNegotiation,
                                       self.host,
                                       self.port)
                        raise TftpException, "Failed option negotiation"

                    else:
                        logger.debug("Client %s requested no options."
                                % self.key)
                        self.start_download()

                else:
                    logger.error("Requested file %s does not exist." %
                            self.filename)
                    self.senderror(self.sock,
                                   TftpErrors.FileNotFound,
                                   raddress,
                                   rport)
                    raise TftpException, "Requested file not found: %s" % self.filename

            else:
                # We're receiving an RRQ when we're not expecting one.
                logger.error("Received an RRQ in handler %s "
                             "but we're in state %s" % (self.key, self.state))
                self.errors += 1

        # Next packet type
        elif isinstance(recvpkt, TftpPacketACK):
            logger.debug("Received an ACK from the client.")
            if recvpkt.blocknumber == 0 and self.state.state == 'oack':
                logger.debug("Received ACK with 0 blocknumber, starting download")
                self.start_download()
            else:
                if self.state.state == 'dat' or self.state.state == 'fin':
                    if self.blocknumber == recvpkt.blocknumber:
                        logger.debug("Received ACK for block %d"
                                % recvpkt.blocknumber)
                        if self.state.state == 'fin':
                            raise TftpException, "Successful transfer."
                        else:
                            self.send_dat()
                    elif recvpkt.blocknumber < self.blocknumber:
                        logger.warn("Received old ACK for block number %d"
                                % recvpkt.blocknumber)
                    else:
                        logger.warn("Received ACK for block number "
                                    "%d, apparently from the future"
                                    % recvpkt.blocknumber)
                else:
                    logger.error("Received ACK with block number %d "
                                 "while in state %s"
                                 % (recvpkt.blocknumber,
                                    self.state.state))

        elif isinstance(recvpkt, TftpPacketERR):
            logger.error("Received error packet from client: %s" % recvpkt)
            self.state.state = 'err'
            raise TftpException, "Received error from client"

        # Handle other packet types.
        else:
            logger.error("Received packet %s while handling a download"
                    % recvpkt)
            self.senderror(self.sock,
                           TftpErrors.IllegalTftpOp,
                           self.host,
                           self.port)
            raise TftpException, "Invalid packet received during download"

    def start_download(self):
        """This method opens self.filename, stores the resulting file object
        in self.fileobj, and calls send_dat()."""
        self.state.state = 'dat'
        self.fileobj = open(self.filename, "r")
        self.send_dat()

    def send_dat(self, resend=False):
        """This method reads sends a DAT packet based on what is in self.buffer."""
        if not resend:
            blksize = int(self.options['blksize'])
            self.buffer = self.fileobj.read(blksize)
            logger.debug("Read %d bytes into buffer" % len(self.buffer))
            if self.buffer == "" or self.buffer < blksize:
                logger.info("Reached EOF on file %s" % self.filename)
                self.state.state = 'fin'
            self.blocknumber += 1
            if self.blocknumber > 65535:
                logger.debug("Blocknumber rolled over to zero")
                self.blocknumber = 0
        else:
            logger.warn("Resending block number %d" % self.blocknumber)
        dat = TftpPacketDAT()
        dat.data = self.buffer
        dat.blocknumber = self.blocknumber
        logger.debug("Sending DAT packet %d" % self.blocknumber)
        self.sock.sendto(dat.encode().buffer, (self.host, self.port))
        self.timesent = time.time()

    def send_oack(self):
        """This method sends an OACK packet based on current params."""
        logger.debug("Composing and sending OACK packet")
        oack = TftpPacketOACK()
        oack.options = self.options
        self.sock.sendto(oack.encode().buffer,
                         (self.host, self.port))
        self.timesent = time.time()
        self.state.state = 'oack'
                
class TftpClient(TftpSession):
    """This class is an implementation of a tftp client."""
    def __init__(self, host, port, options={}):
        """This constructor returns an instance of TftpClient, taking the
        remote host, the remote port, and the filename to fetch."""
        TftpSession.__init__(self)
        self.host = host
        self.iport = port
        self.options = options
        if self.options.has_key('blksize'):
            size = self.options['blksize']
            tftpassert(types.IntType == type(size), "blksize must be an int")
            if size < MIN_BLKSIZE or size > MAX_BLKSIZE:
                raise TftpException, "Invalid blksize: %d" % size
        else:
            self.options['blksize'] = DEF_BLKSIZE
        # Support other options here? timeout time, retries, etc?
        
        # The remote sending port, to identify the connection.
        self.port = None
        self.sock = None
        
    def gethost(self):
        "Simple getter method."
        return self.__host
    
    def sethost(self, host):
        """Setter method that also sets the address property as a result
        of the host that is set."""
        self.__host = host
        self.address = socket.gethostbyname(host)
        
    host = property(gethost, sethost)

    def download(self, filename, output, packethook=None, timeout=SOCK_TIMEOUT):
        """This method initiates a tftp download from the configured remote
        host, requesting the filename passed. It saves the file to a local
        file specified in the output parameter. If a packethook is provided,
        it must be a function that takes a single parameter, which will be a
        copy of each DAT packet received in the form of a TftpPacketDAT
        object. The timeout parameter may be used to override the default
        SOCK_TIMEOUT setting, which is the amount of time that the client will
        wait for a receive packet to arrive."""
        # Open the output file.
        # FIXME - need to support alternate return formats than files?
        outputfile = open(output, "wb")
        recvpkt = None
        curblock = 0
        dups = {}
        start_time = time.time()
        bytes = 0

        tftp_factory = TftpPacketFactory()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.settimeout(timeout)

        logger.info("Sending tftp download request to %s" % self.host)
        logger.info("    filename -> %s" % filename)
        pkt = TftpPacketRRQ()
        pkt.filename = filename
        pkt.mode = "octet" # FIXME - shouldn't hardcode this
        pkt.options = self.options
        self.sock.sendto(pkt.encode().buffer, (self.host, self.iport))
        self.state.state = 'rrq'
        
        timeouts = 0
        while True:
            try:
                (buffer, (raddress, rport)) = self.sock.recvfrom(MAX_BLKSIZE)
            except socket.timeout, err:
                timeouts += 1
                if timeouts >= TIMEOUT_RETRIES:
                    raise TftpException, "Hit max timeouts, giving up."
                else:
                    logger.warn("Timeout waiting for traffic, retrying...")
                    continue

            recvpkt = tftp_factory.parse(buffer)

            logger.debug("Received %d bytes from %s:%s" 
                         % (len(buffer), raddress, rport))
            
            # Check for known "connection".
            if raddress != self.address:
                logger.warn("Received traffic from %s, expected host %s. Discarding"
                            % (raddress, self.host))
                continue
            if self.port and self.port != rport:
                logger.warn("Received traffic from %s:%s but we're "
                            "connected to %s:%s. Discarding."
                            % (raddress, rport,
                            self.host, self.port))
                continue
            
            if not self.port and self.state.state == 'rrq':
                self.port = rport
                logger.debug("Set remote port for session to %s" % rport)
            
            if isinstance(recvpkt, TftpPacketDAT):
                logger.debug("recvpkt.blocknumber = %d" % recvpkt.blocknumber)
                logger.debug("curblock = %d" % curblock)
                expected_block = curblock + 1
                if expected_block > 65535:
                    logger.debug("block number rollover to 0 again")
                    expected_block = 0
                if recvpkt.blocknumber == expected_block:
                    logger.debug("good, received block %d in sequence" 
                                % recvpkt.blocknumber)
                    curblock = expected_block

                        
                    # ACK the packet, and save the data.
                    logger.info("sending ACK to block %d" % curblock)
                    logger.debug("ip = %s, port = %s" % (self.host, self.port))
                    ackpkt = TftpPacketACK()
                    ackpkt.blocknumber = curblock
                    self.sock.sendto(ackpkt.encode().buffer, (self.host, self.port))
                    
                    logger.debug("writing %d bytes to output file" 
                                % len(recvpkt.data))
                    outputfile.write(recvpkt.data)
                    bytes += len(recvpkt.data)
                    # If there is a packethook defined, call it.
                    if packethook:
                        packethook(recvpkt)
                    # Check for end-of-file, any less than full data packet.
                    if len(recvpkt.data) < self.options['blksize']:
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
                    self.sock.sendto(ackpkt.encode().buffer, (self.host, self.port))

                else:
                    msg = "Whoa! Received block %d but expected %d" % (recvpkt.blocknumber, 
                                                                    curblock+1)
                    logger.error(msg)
                    raise TftpException, msg

            # Check other packet types.
            elif isinstance(recvpkt, TftpPacketOACK):
                if not self.state.state == 'rrq':
                    self.errors += 1
                    logger.error("Received OACK in state %s" % self.state.state)
                    continue
                
                self.state.state = 'oack'
                logger.info("Received OACK from server.")
                if recvpkt.options.keys() > 0:
                    if recvpkt.match_options(self.options):
                        logger.info("Successful negotiation of options")
                        for key in self.options:
                            logger.info("    %s = %s" % (key, self.options[key]))
                        logger.debug("sending ACK to OACK")
                        ackpkt = TftpPacketACK()
                        ackpkt.blocknumber = 0
                        self.sock.sendto(ackpkt.encode().buffer, (self.host, self.port))
                        self.state.state = 'ack'
                    else:
                        logger.error("failed to negotiate options")
                        self.senderror(self.sock, TftpErrors.FailedNegotiation, self.host, self.port)
                        self.state.state = 'err'
                        raise TftpException, "Failed to negotiate options"

            elif isinstance(recvpkt, TftpPacketACK):
                # Umm, we ACK, the server doesn't.
                self.state.state = 'err'
                self.senderror(self.sock, TftpErrors.IllegalTftpOp, self.host, self.port)
                tftpassert(False, "Received ACK from server while in download")

            elif isinstance(recvpkt, TftpPacketERR):
                self.state.state = 'err'
                self.senderror(self.sock, TftpErrors.IllegalTftpOp, self.host, self.port)
                tftpassert(False, "Received ERR from server: " + str(recvpkt))

            elif isinstance(recvpkt, TftpPacketWRQ):
                self.state.state = 'err'
                self.senderror(self.sock, TftpErrors.IllegalTftpOp, self.host, self.port)
                tftpassert(False, "Received WRQ from server: " + str(recvpkt))

            else:
                self.state.state = 'err'
                self.senderror(self.sock, TftpErrors.IllegalTftpOp, self.host, self.port)
                tftpassert(False, "Received unknown packet type from server: "
                        + str(recvpkt))


        # end while

        end_time = time.time()
        duration = end_time - start_time
        outputfile.close()
        logger.info('')
        logger.info("Downloaded %d bytes in %d seconds" % (bytes, duration))
        bps = (bytes * 8.0) / duration
        kbps = bps / 1024.0
        logger.info("Average rate: %.2f kbps" % kbps)
        dupcount = 0
        for key in dups:
            dupcount += dups[key]
        logger.info("Received %d duplicate packets" % dupcount)
