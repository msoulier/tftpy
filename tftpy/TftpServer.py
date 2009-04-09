import socket, os, re, time, random
from TftpShared import *
from TftpPacketTypes import *
from TftpPacketFactory import *

class TftpServer(TftpSession):
    """This class implements a tftp server object."""

    def __init__(self, tftproot='/tftpboot'):
        """Class constructor. It takes a single optional argument, which is
        the path to the tftproot directory to serve files from and/or write
        them to."""
        self.listenip = None
        self.listenport = None
        self.sock = None
        self.root = os.path.abspath(tftproot)
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

        # Don't use new 2.5 ternary operator yet
        # listenip = listenip if listenip else '0.0.0.0'
        if not listenip: listenip = '0.0.0.0'
        logger.info("Server requested on ip %s, port %s"
                % (listenip, listenport))
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
                                                                       'rrq',
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
        self.options = { 'blksize': DEF_BLKSIZE }
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

            # test host/port of client end
            if self.host != raddress or self.port != rport:
                self.senderror(self.sock,
                               TftpErrors.UnknownTID,
                               raddress,
                               rport)
                logger.error("Expected traffic from %s:%s but received it "
                             "from %s:%s instead."
                             % (self.host, self.port, raddress, rport))
                self.errors += 1
                return

            if self.state.state == 'rrq':
                logger.debug("Received RRQ. Composing response.")
                self.filename = self.root + os.sep + recvpkt.filename
                logger.debug("The path to the desired file is %s" %
                        self.filename)
                self.filename = os.path.abspath(self.filename)
                logger.debug("The absolute path is %s" % self.filename)
                # Security check. Make sure it's prefixed by the tftproot.
                if self.filename.find(self.root) == 0:
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
                        # Delete the option now that it's handled.
                        del recvpkt.options['blksize']
                        if blksize >= MIN_BLKSIZE and blksize <= MAX_BLKSIZE:
                            logger.info("Client requested blksize = %d"
                                    % blksize)
                            self.options['blksize'] = blksize
                        else:
                            logger.warning("Client %s requested invalid "
                                           "blocksize %d, responding with default"
                                           % (self.key, blksize))
                            self.options['blksize'] = DEF_BLKSIZE

                    if recvpkt.options.has_key('tsize'):
                        logger.info('RRQ includes tsize option')
                        self.options['tsize'] = os.stat(self.filename).st_size
                        # Delete the option now that it's handled.
                        del recvpkt.options['tsize']

                    if len(recvpkt.options.keys()) > 0:
                        logger.warning("Client %s requested unsupported options: %s"
                                       % (self.key, recvpkt.options))

                    if self.options:
                        logger.info("Options requested, sending OACK")
                        self.send_oack()
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
                        # Don't resend a DAT due to an old ACK. Fixes the
                        # sorceror's apprentice problem.
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
        self.fileobj = open(self.filename, "rb")
        self.send_dat()

    def send_dat(self, resend=False):
        """This method reads sends a DAT packet based on what is in self.buffer."""
        if not resend:
            blksize = int(self.options['blksize'])
            self.buffer = self.fileobj.read(blksize)
            logger.debug("Read %d bytes into buffer" % len(self.buffer))
            if len(self.buffer) < blksize:
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

    # FIXME - should these be factored-out into the session class?
    def send_oack(self):
        """This method sends an OACK packet based on current params."""
        logger.debug("Composing and sending OACK packet")
        oack = TftpPacketOACK()
        oack.options = self.options
        self.sock.sendto(oack.encode().buffer,
                         (self.host, self.port))
        self.timesent = time.time()
        self.state.state = 'oack'
