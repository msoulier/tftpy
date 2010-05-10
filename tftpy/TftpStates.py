from TftpShared import *
from TftpPacketTypes import *
from TftpPacketFactory import *
import socket, time, os

###############################################################################
# Utility classes
###############################################################################

class TftpMetrics(object):
    """A class representing metrics of the transfer."""
    def __init__(self):
        # Bytes transferred
        self.bytes = 0
        # Bytes re-sent
        self.resent_bytes = 0
        # Duplicate packets received
        self.dups = {}
        self.dupcount = 0
        # Times
        self.start_time = 0
        self.end_time = 0
        self.duration = 0
        # Rates
        self.bps = 0
        self.kbps = 0
        # Generic errors
        self.errors = 0

    def compute(self):
        # Compute transfer time
        self.duration = self.end_time - self.start_time
        log.debug("TftpMetrics.compute: duration is %s" % self.duration)
        self.bps = (self.bytes * 8.0) / self.duration
        self.kbps = self.bps / 1024.0
        log.debug("TftpMetrics.compute: kbps is %s" % self.kbps)
        for key in self.dups:
            self.dupcount += self.dups[key]

    def add_dup(self, blocknumber):
        """This method adds a dup for a block number to the metrics."""
        log.debug("Recording a dup for block %d" % blocknumber)
        if self.dups.has_key(blocknumber):
            self.dups[blocknumber] += 1
        else:
            self.dups[blocknumber] = 1
        tftpassert(self.dups[blocknumber] < MAX_DUPS,
            "Max duplicates for block %d reached" % blocknumber)

###############################################################################
# Context classes
###############################################################################

class TftpContext(object):
    """The base class of the contexts."""

    def __init__(self, host, port, timeout, dyn_file_func=None):
        """Constructor for the base context, setting shared instance
        variables."""
        self.file_to_transfer = None
        self.fileobj = None
        self.options = None
        self.packethook = None
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.settimeout(timeout)
        self.state = None
        self.next_block = 0
        self.factory = TftpPacketFactory()
        # Note, setting the host will also set self.address, as it's a property.
        self.host = host
        self.port = port
        # The port associated with the TID
        self.tidport = None
        # Metrics
        self.metrics = TftpMetrics()
        # Flag when the transfer is pending completion.
        self.pending_complete = False
        # Time when this context last received any traffic.
        # FIXME: does this belong in metrics?
        self.last_update = 0
        # The last DAT packet we sent, if applicable, to make resending easy.
        self.last_dat_pkt = None
        self.dyn_file_func = dyn_file_func

    def __del__(self):
        """Simple destructor to try to call housekeeping in the end method if
        not called explicitely. Leaking file descriptors is not a good
        thing."""
        self.end()

    def checkTimeout(self, now):
        """Compare current time with last_update time, and raise an exception
        if we're over SOCK_TIMEOUT time."""
        if now - self.last_update > SOCK_TIMEOUT:
            raise TftpException, "Timeout waiting for traffic"

    def start(self):
        raise NotImplementedError, "Abstract method"

    def end(self):
        """Perform session cleanup, since the end method should always be
        called explicitely by the calling code, this works better than the
        destructor."""
        log.debug("in TftpContext.end")
        if not self.fileobj.closed:
            log.debug("self.fileobj is open - closing")
            self.fileobj.close()

    def gethost(self):
        "Simple getter method for use in a property."
        return self.__host

    def sethost(self, host):
        """Setter method that also sets the address property as a result
        of the host that is set."""
        self.__host = host
        self.address = socket.gethostbyname(host)

    host = property(gethost, sethost)

    def setNextBlock(self, block):
        if block > 2 ** 16:
            log.debug("Block number rollover to 0 again")
            block = 0
        self.__eblock = block

    def getNextBlock(self):
        return self.__eblock

    next_block = property(getNextBlock, setNextBlock)

    def cycle(self):
        """Here we wait for a response from the server after sending it
        something, and dispatch appropriate action to that response."""
        # FIXME: This won't work very well in a server context with multiple
        # sessions running.
        for i in range(TIMEOUT_RETRIES):
            log.debug("In cycle, receive attempt %d" % i)
            try:
                (buffer, (raddress, rport)) = self.sock.recvfrom(MAX_BLKSIZE)
            except socket.timeout, err:
                log.warn("Timeout waiting for traffic, retrying...")
                continue
            break
        else:
            raise TftpException, "Hit max timeouts, giving up."

        # Ok, we've received a packet. Log it.
        log.debug("Received %d bytes from %s:%s"
                        % (len(buffer), raddress, rport))
        # And update our last updated time.
        self.last_update = time.time()

        # Decode it.
        recvpkt = self.factory.parse(buffer)

        # Check for known "connection".
        if raddress != self.address:
            log.warn("Received traffic from %s, expected host %s. Discarding"
                        % (raddress, self.host))

        if self.tidport and self.tidport != rport:
            log.warn("Received traffic from %s:%s but we're "
                        "connected to %s:%s. Discarding."
                        % (raddress, rport,
                        self.host, self.tidport))

        # If there is a packethook defined, call it. We unconditionally
        # pass all packets, it's up to the client to screen out different
        # kinds of packets. This way, the client is privy to things like
        # negotiated options.
        if self.packethook:
            self.packethook(recvpkt)

        # And handle it, possibly changing state.
        self.state = self.state.handle(recvpkt, raddress, rport)

class TftpContextServer(TftpContext):
    """The context for the server."""
    def __init__(self, host, port, timeout, root, dyn_file_func=None):
        TftpContext.__init__(self,
                             host,
                             port,
                             timeout,
                             dyn_file_func
                             )
        # At this point we have no idea if this is a download or an upload. We
        # need to let the start state determine that.
        self.state = TftpStateServerStart(self)
        self.root = root
        self.dyn_file_func = dyn_file_func

    def __str__(self):
        return "%s:%s %s" % (self.host, self.port, self.state)

    def start(self, buffer):
        """Start the state cycle. Note that the server context receives an
        initial packet in its start method. Also note that the server does not
        loop on cycle(), as it expects the TftpServer object to manage
        that."""
        log.debug("In TftpContextServer.start")
        self.metrics.start_time = time.time()
        log.debug("Set metrics.start_time to %s" % self.metrics.start_time)
        # And update our last updated time.
        self.last_update = time.time()

        pkt = self.factory.parse(buffer)
        log.debug("TftpContextServer.start() - factory returned a %s" % pkt)

        # Call handle once with the initial packet. This should put us into
        # the download or the upload state.
        self.state = self.state.handle(pkt,
                                       self.host,
                                       self.port)

    def end(self):
        """Finish up the context."""
        TftpContext.end(self)
        self.metrics.end_time = time.time()
        log.debug("Set metrics.end_time to %s" % self.metrics.end_time)
        self.metrics.compute()

class TftpContextClientUpload(TftpContext):
    """The upload context for the client during an upload."""
    def __init__(self,
                 host,
                 port,
                 filename,
                 input,
                 options,
                 packethook,
                 timeout):
        TftpContext.__init__(self,
                             host,
                             port,
                             timeout)
        self.file_to_transfer = filename
        self.options = options
        self.packethook = packethook
        self.fileobj = open(input, "rb")

        log.debug("TftpContextClientUpload.__init__()")
        log.debug("file_to_transfer = %s, options = %s" %
            (self.file_to_transfer, self.options))

    def __str__(self):
        return "%s:%s %s" % (self.host, self.port, self.state)

    def start(self):
        log.info("Sending tftp upload request to %s" % self.host)
        log.info("    filename -> %s" % self.file_to_transfer)
        log.info("    options -> %s" % self.options)

        self.metrics.start_time = time.time()
        log.debug("Set metrics.start_time to %s" % self.metrics.start_time)

        # FIXME: put this in a sendWRQ method?
        pkt = TftpPacketWRQ()
        pkt.filename = self.file_to_transfer
        pkt.mode = "octet" # FIXME - shouldn't hardcode this
        pkt.options = self.options
        self.sock.sendto(pkt.encode().buffer, (self.host, self.port))
        self.next_block = 1

        self.state = TftpStateSentWRQ(self)

        while self.state:
            log.debug("State is %s" % self.state)
            self.cycle()

    def end(self):
        """Finish up the context."""
        TftpContext.end(self)
        self.metrics.end_time = time.time()
        log.debug("Set metrics.end_time to %s" % self.metrics.end_time)
        self.metrics.compute()

class TftpContextClientDownload(TftpContext):
    """The download context for the client during a download."""
    def __init__(self,
                 host,
                 port,
                 filename,
                 output,
                 options,
                 packethook,
                 timeout):
        TftpContext.__init__(self,
                             host,
                             port,
                             timeout)
        # FIXME: should we refactor setting of these params?
        self.file_to_transfer = filename
        self.options = options
        self.packethook = packethook
        # FIXME - need to support alternate return formats than files?
        # File-like objects would be ideal, ala duck-typing.
        self.fileobj = open(output, "wb")

        log.debug("TftpContextClientDownload.__init__()")
        log.debug("file_to_transfer = %s, options = %s" %
            (self.file_to_transfer, self.options))

    def __str__(self):
        return "%s:%s %s" % (self.host, self.port, self.state)

    def start(self):
        """Initiate the download."""
        log.info("Sending tftp download request to %s" % self.host)
        log.info("    filename -> %s" % self.file_to_transfer)
        log.info("    options -> %s" % self.options)

        self.metrics.start_time = time.time()
        log.debug("Set metrics.start_time to %s" % self.metrics.start_time)

        # FIXME: put this in a sendRRQ method?
        pkt = TftpPacketRRQ()
        pkt.filename = self.file_to_transfer
        pkt.mode = "octet" # FIXME - shouldn't hardcode this
        pkt.options = self.options
        self.sock.sendto(pkt.encode().buffer, (self.host, self.port))
        self.next_block = 1

        self.state = TftpStateSentRRQ(self)

        while self.state:
            log.debug("State is %s" % self.state)
            self.cycle()

    def end(self):
        """Finish up the context."""
        TftpContext.end(self)
        self.metrics.end_time = time.time()
        log.debug("Set metrics.end_time to %s" % self.metrics.end_time)
        self.metrics.compute()

###############################################################################
# State classes
###############################################################################

class TftpState(object):
    """The base class for the states."""

    def __init__(self, context):
        """Constructor for setting up common instance variables. The involved
        file object is required, since in tftp there's always a file
        involved."""
        self.context = context

    def handle(self, pkt, raddress, rport):
        """An abstract method for handling a packet. It is expected to return
        a TftpState object, either itself or a new state."""
        raise NotImplementedError, "Abstract method"

    def handleOACK(self, pkt):
        """This method handles an OACK from the server, syncing any accepted
        options."""
        if pkt.options.keys() > 0:
            if pkt.match_options(self.context.options):
                log.info("Successful negotiation of options")
                # Set options to OACK options
                self.context.options = pkt.options
                for key in self.context.options:
                    log.info("    %s = %s" % (key, self.context.options[key]))
            else:
                log.error("Failed to negotiate options")
                raise TftpException, "Failed to negotiate options"
        else:
            raise TftpException, "No options found in OACK"

    def returnSupportedOptions(self, options):
        """This method takes a requested options list from a client, and
        returns the ones that are supported."""
        # We support the options blksize and tsize right now.
        # FIXME - put this somewhere else?
        accepted_options = {}
        for option in options:
            if option == 'blksize':
                # Make sure it's valid.
                if int(options[option]) > MAX_BLKSIZE:
                    log.info("Client requested blksize greater than %d "
                             "setting to maximum" % MAX_BLKSIZE)
                    accepted_options[option] = MAX_BLKSIZE
                elif int(options[option]) < MIN_BLKSIZE:
                    log.info("Client requested blksize less than %d "
                             "setting to minimum" % MIN_BLKSIZE)
                    accepted_options[option] = MIN_BLKSIZE
                else:
                    accepted_options[option] = options[option]
            elif option == 'tsize':
                log.debug("tsize option is set")
                accepted_options['tsize'] = 1
            else:
                log.info("Dropping unsupported option '%s'" % option)
        log.debug("Returning these accepted options: %s" % accepted_options)
        return accepted_options

    def serverInitial(self, pkt, raddress, rport):
        """This method performs initial setup for a server context transfer,
        put here to refactor code out of the TftpStateServerRecvRRQ and
        TftpStateServerRecvWRQ classes, since their initial setup is
        identical. The method returns a boolean, sendoack, to indicate whether
        it is required to send an OACK to the client."""
        options = pkt.options
        sendoack = False
        if not self.context.tidport:
            self.context.tidport = rport
            log.info("Setting tidport to %s" % rport)
        if not options:
            log.debug("Setting default options, blksize")
            # FIXME: put default options elsewhere
            self.context.options = { 'blksize': DEF_BLKSIZE }
        else:
            log.debug("Options requested: %s" % options)
            self.context.options = self.returnSupportedOptions(options)
            sendoack = True

        # FIXME - only octet mode is supported at this time.
        if pkt.mode != 'octet':
            self.sendError(TftpErrors.IllegalTftpOp)
            raise TftpException, \
                "Only octet transfers are supported at this time."

        # test host/port of client end
        if self.context.host != raddress or self.context.port != rport:
            self.sendError(TftpErrors.UnknownTID)
            log.error("Expected traffic from %s:%s but received it "
                            "from %s:%s instead."
                            % (self.context.host,
                               self.context.port,
                               raddress,
                               rport))
            # FIXME: increment an error count?
            # Return same state, we're still waiting for valid traffic.
            return self

        log.debug("Requested filename is %s" % pkt.filename)
        # There are no os.sep's allowed in the filename.
        # FIXME: Should we allow subdirectories?
        if pkt.filename.find(os.sep) >= 0:
            self.sendError(TftpErrors.IllegalTftpOp)
            raise TftpException, "%s found in filename, not permitted" % os.sep

        self.context.file_to_transfer = pkt.filename

        return sendoack

    def sendDAT(self, resend=False):
        """This method sends the next DAT packet based on the data in the
        context. It returns a boolean indicating whether the transfer is
        finished."""
        finished = False
        blocknumber = self.context.next_block
        tftpassert( blocknumber > 0, "There is no block zero!" )
        dat = None
        if resend:
            log.warn("Resending block number %d" % blocknumber)
            dat = self.context.last_dat_pkt
            self.context.metrics.resent_bytes += len(dat.data)
            self.context.metrics.add_dup(dat)
        else:
            blksize = int(self.context.options['blksize'])
            buffer = self.context.fileobj.read(blksize)
            log.debug("Read %d bytes into buffer" % len(buffer))
            if len(buffer) < blksize:
                log.info("Reached EOF on file %s"
                    % self.context.file_to_transfer)
                finished = True
            dat = TftpPacketDAT()
            dat.data = buffer
            dat.blocknumber = blocknumber
        self.context.metrics.bytes += len(dat.data)
        log.debug("Sending DAT packet %d" % dat.blocknumber)
        self.context.sock.sendto(dat.encode().buffer,
                                 (self.context.host, self.context.tidport))
        if self.context.packethook:
            self.context.packethook(dat)
        self.context.last_dat_pkt = dat
        return finished

    def sendACK(self, blocknumber=None):
        """This method sends an ack packet to the block number specified. If
        none is specified, it defaults to the next_block property in the
        parent context."""
        log.debug("In sendACK, passed blocknumber is %s" % blocknumber)
        if blocknumber is None:
            blocknumber = self.context.next_block
        log.info("Sending ack to block %d" % blocknumber)
        ackpkt = TftpPacketACK()
        ackpkt.blocknumber = blocknumber
        self.context.sock.sendto(ackpkt.encode().buffer,
                                 (self.context.host,
                                  self.context.tidport))

    def sendError(self, errorcode):
        """This method uses the socket passed, and uses the errorcode to
        compose and send an error packet."""
        log.debug("In sendError, being asked to send error %d" % errorcode)
        errpkt = TftpPacketERR()
        errpkt.errorcode = errorcode
        self.context.sock.sendto(errpkt.encode().buffer,
                                 (self.context.host,
                                  self.context.tidport))

    def sendOACK(self):
        """This method sends an OACK packet with the options from the current
        context."""
        log.debug("In sendOACK with options %s" % self.context.options)
        pkt = TftpPacketOACK()
        pkt.options = self.context.options
        self.context.sock.sendto(pkt.encode().buffer,
                                 (self.context.host,
                                  self.context.tidport))

    def handleDat(self, pkt):
        """This method handles a DAT packet during a client download, or a
        server upload."""
        log.info("Handling DAT packet - block %d" % pkt.blocknumber)
        log.debug("Expecting block %s" % self.context.next_block)
        if pkt.blocknumber == self.context.next_block:
            log.debug("Good, received block %d in sequence"
                        % pkt.blocknumber)

            self.sendACK()
            self.context.next_block += 1

            log.debug("Writing %d bytes to output file"
                        % len(pkt.data))
            self.context.fileobj.write(pkt.data)
            self.context.metrics.bytes += len(pkt.data)
            # Check for end-of-file, any less than full data packet.
            if len(pkt.data) < int(self.context.options['blksize']):
                log.info("End of file detected")
                return None

        elif pkt.blocknumber < self.context.next_block:
            if pkt.blocknumber == 0:
                log.warn("There is no block zero!")
                self.sendError(TftpErrors.IllegalTftpOp)
                raise TftpException, "There is no block zero!"
            log.warn("Dropping duplicate block %d" % pkt.blocknumber)
            self.context.metrics.add_dup(pkt.blocknumber)
            log.debug("ACKing block %d again, just in case" % pkt.blocknumber)
            self.sendACK(pkt.blocknumber)

        else:
            # FIXME: should we be more tolerant and just discard instead?
            msg = "Whoa! Received future block %d but expected %d" \
                % (pkt.blocknumber, self.context.next_block)
            log.error(msg)
            raise TftpException, msg

        # Default is to ack
        return TftpStateExpectDAT(self.context)

class TftpStateServerRecvRRQ(TftpState):
    """This class represents the state of the TFTP server when it has just
    received an RRQ packet."""
    def handle(self, pkt, raddress, rport):
        "Handle an initial RRQ packet as a server."
        log.debug("In TftpStateServerRecvRRQ.handle")
        sendoack = self.serverInitial(pkt, raddress, rport)
        path = self.context.root + os.sep + self.context.file_to_transfer
        log.info("Opening file %s for reading" % path)
        if os.path.exists(path):
            # Note: Open in binary mode for win32 portability, since win32
            # blows.
            self.context.fileobj = open(path, "rb")
        elif self.context.dyn_file_func:
            log.debug("No such file %s but using dyn_file_func" % path)
            self.context.fileobj = \
                self.context.dyn_file_func(self.context.file_to_transfer)
        else:
            self.sendError(TftpErrors.FileNotFound)
            raise TftpException, "File not found: %s" % path

        # Options negotiation.
        if sendoack:
            # Note, next_block is 0 here since that's the proper
            # acknowledgement to an OACK.
            # FIXME: perhaps we do need a TftpStateExpectOACK class...
            self.sendOACK()
            # Note, self.context.next_block is already 0.
        else:
            self.context.next_block = 1
            log.debug("No requested options, starting send...")
            self.context.pending_complete = self.sendDAT()
        # Note, we expect an ack regardless of whether we sent a DAT or an
        # OACK.
        return TftpStateExpectACK(self.context)

        # Note, we don't have to check any other states in this method, that's
        # up to the caller.

class TftpStateServerRecvWRQ(TftpState):
    """This class represents the state of the TFTP server when it has just
    received a WRQ packet."""
    def handle(self, pkt, raddress, rport):
        "Handle an initial WRQ packet as a server."
        log.debug("In TftpStateServerRecvWRQ.handle")
        sendoack = self.serverInitial(pkt, raddress, rport)
        path = self.context.root + os.sep + self.context.file_to_transfer
        log.info("Opening file %s for writing" % path)
        if os.path.exists(path):
            # FIXME: correct behavior?
            log.warn("File %s exists already, overwriting..." % self.context.file_to_transfer)
        # FIXME: I think we should upload to a temp file and not overwrite the
        # existing file until the file is successfully uploaded.
        self.context.fileobj = open(path, "wb")

        # Options negotiation.
        if sendoack:
            log.debug("Sending OACK to client")
            self.sendOACK()
        else:
            log.debug("No requested options, expecting transfer to begin...")
            self.sendACK()
        # Whether we're sending an oack or not, we're expecting a DAT for
        # block 1
        self.context.next_block = 1
        # We may have sent an OACK, but we're expecting a DAT as the response
        # to either the OACK or an ACK, so lets unconditionally use the
        # TftpStateExpectDAT state.
        return TftpStateExpectDAT(self.context)

        # Note, we don't have to check any other states in this method, that's
        # up to the caller.

class TftpStateServerStart(TftpState):
    """The start state for the server. This is a transitory state since at
    this point we don't know if we're handling an upload or a download. We
    will commit to one of them once we interpret the initial packet."""
    def handle(self, pkt, raddress, rport):
        """Handle a packet we just received."""
        log.debug("In TftpStateServerStart.handle")
        if isinstance(pkt, TftpPacketRRQ):
            log.debug("Handling an RRQ packet")
            return TftpStateServerRecvRRQ(self.context).handle(pkt,
                                                               raddress,
                                                               rport)
        elif isinstance(pkt, TftpPacketWRQ):
            log.debug("Handling a WRQ packet")
            return TftpStateServerRecvWRQ(self.context).handle(pkt,
                                                               raddress,
                                                               rport)
        else:
            self.sendError(TftpErrors.IllegalTftpOp)
            raise TftpException, \
                "Invalid packet to begin up/download: %s" % pkt

class TftpStateExpectACK(TftpState):
    """This class represents the state of the transfer when a DAT was just
    sent, and we are waiting for an ACK from the server. This class is the
    same one used by the client during the upload, and the server during the
    download."""
    def handle(self, pkt, raddress, rport):
        "Handle a packet, hopefully an ACK since we just sent a DAT."
        if isinstance(pkt, TftpPacketACK):
            log.info("Received ACK for packet %d" % pkt.blocknumber)
            # Is this an ack to the one we just sent?
            if self.context.next_block == pkt.blocknumber:
                if self.context.pending_complete:
                    log.info("Received ACK to final DAT, we're done.")
                    return None
                else:
                    log.debug("Good ACK, sending next DAT")
                    self.context.next_block += 1
                    log.debug("Incremented next_block to %d"
                        % (self.context.next_block))
                    self.context.pending_complete = self.sendDAT()

            elif pkt.blocknumber < self.context.next_block:
                self.context.metrics.add_dup(pkt.blocknumber)

            else:
                log.warn("Oooh, time warp. Received ACK to packet we "
                         "didn't send yet. Discarding.")
                self.context.metrics.errors += 1
            return self
        elif isinstance(pkt, TftpPacketERR):
            log.error("Received ERR packet from peer: %s" % str(pkt))
            raise TftpException, \
                "Received ERR packet from peer: %s" % str(pkt)
        else:
            log.warn("Discarding unsupported packet: %s" % str(pkt))
            return self

class TftpStateExpectDAT(TftpState):
    """Just sent an ACK packet. Waiting for DAT."""
    def handle(self, pkt, raddress, rport):
        """Handle the packet in response to an ACK, which should be a DAT."""
        if isinstance(pkt, TftpPacketDAT):
            return self.handleDat(pkt)

        # Every other packet type is a problem.
        elif isinstance(pkt, TftpPacketACK):
            # Umm, we ACK, you don't.
            self.sendError(TftpErrors.IllegalTftpOp)
            raise TftpException, "Received ACK from peer when expecting DAT"

        elif isinstance(pkt, TftpPacketWRQ):
            self.sendError(TftpErrors.IllegalTftpOp)
            raise TftpException, "Received WRQ from peer when expecting DAT"

        elif isinstance(pkt, TftpPacketERR):
            self.sendError(TftpErrors.IllegalTftpOp)
            raise TftpException, "Received ERR from peer: " + str(pkt)

        else:
            self.sendError(TftpErrors.IllegalTftpOp)
            raise TftpException, "Received unknown packet type from peer: " + str(pkt)

class TftpStateSentWRQ(TftpState):
    """Just sent an WRQ packet for an upload."""
    def handle(self, pkt, raddress, rport):
        """Handle a packet we just received."""
        if not self.context.tidport:
            self.context.tidport = rport
            log.debug("Set remote port for session to %s" % rport)

        # If we're going to successfully transfer the file, then we should see
        # either an OACK for accepted options, or an ACK to ignore options.
        if isinstance(pkt, TftpPacketOACK):
            log.info("Received OACK from server")
            try:
                self.handleOACK(pkt)
            except TftpException, err:
                log.error("Failed to negotiate options")
                self.sendError(TftpErrors.FailedNegotiation)
                raise
            else:
                log.debug("Sending first DAT packet")
                self.context.pending_complete = self.sendDAT()
                log.debug("Changing state to TftpStateExpectACK")
                return TftpStateExpectACK(self.context)

        elif isinstance(pkt, TftpPacketACK):
            log.info("Received ACK from server")
            log.debug("Apparently the server ignored our options")
            # The block number should be zero.
            if pkt.blocknumber == 0:
                log.debug("Ack blocknumber is zero as expected")
                log.debug("Sending first DAT packet")
                self.pending_complete = self.context.sendDAT()
                log.debug("Changing state to TftpStateExpectACK")
                return TftpStateExpectACK(self.context)
            else:
                log.warn("Discarding ACK to block %s" % pkt.blocknumber)
                log.debug("Still waiting for valid response from server")
                return self

        elif isinstance(pkt, TftpPacketERR):
            self.sendError(TftpErrors.IllegalTftpOp)
            raise TftpException, "Received ERR from server: " + str(pkt)

        elif isinstance(pkt, TftpPacketRRQ):
            self.sendError(TftpErrors.IllegalTftpOp)
            raise TftpException, "Received RRQ from server while in upload"

        elif isinstance(pkt, TftpPacketDAT):
            self.sendError(TftpErrors.IllegalTftpOp)
            raise TftpException, "Received DAT from server while in upload"

        else:
            self.sendError(TftpErrors.IllegalTftpOp)
            raise TftpException, "Received unknown packet type from server: " + str(pkt)

        # By default, no state change.
        return self

class TftpStateSentRRQ(TftpState):
    """Just sent an RRQ packet."""
    def handle(self, pkt, raddress, rport):
        """Handle the packet in response to an RRQ to the server."""
        if not self.context.tidport:
            self.context.tidport = rport
            log.info("Set remote port for session to %s" % rport)

        # Now check the packet type and dispatch it properly.
        if isinstance(pkt, TftpPacketOACK):
            log.info("Received OACK from server")
            try:
                self.handleOACK(pkt)
            except TftpException, err:
                log.error("Failed to negotiate options: %s" % str(err))
                self.sendError(TftpErrors.FailedNegotiation)
                raise
            else:
                log.debug("Sending ACK to OACK")

                self.sendACK(blocknumber=0)

                log.debug("Changing state to TftpStateExpectDAT")
                return TftpStateExpectDAT(self.context)

        elif isinstance(pkt, TftpPacketDAT):
            # If there are any options set, then the server didn't honour any
            # of them.
            log.info("Received DAT from server")
            if self.context.options:
                log.info("Server ignored options, falling back to defaults")
                self.context.options = { 'blksize': DEF_BLKSIZE }
            return self.handleDat(pkt)

        # Every other packet type is a problem.
        elif isinstance(pkt, TftpPacketACK):
            # Umm, we ACK, the server doesn't.
            self.sendError(TftpErrors.IllegalTftpOp)
            raise TftpException, "Received ACK from server while in download"

        elif isinstance(pkt, TftpPacketWRQ):
            self.sendError(TftpErrors.IllegalTftpOp)
            raise TftpException, "Received WRQ from server while in download"

        elif isinstance(pkt, TftpPacketERR):
            self.sendError(TftpErrors.IllegalTftpOp)
            raise TftpException, "Received ERR from server: " + str(pkt)

        else:
            self.sendError(TftpErrors.IllegalTftpOp)
            raise TftpException, "Received unknown packet type from server: " + str(pkt)

        # By default, no state change.
        return self
