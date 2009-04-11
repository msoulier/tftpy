from TftpShared import *
from TftpPacketTypes import *
from TftpPacketFactory import *
import socket, time

###############################################################################
# Utility classes
###############################################################################

class TftpMetrics(object):
    """A class representing metrics of the transfer."""
    def __init__(self):
        # Bytes transferred
        self.bytes = 0
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

    def compute(self):
        # Compute transfer time
        self.duration = self.end_time - self.start_time
        logger.debug("TftpMetrics.compute: duration is %s" % self.duration)
        self.bps = (self.bytes * 8.0) / self.duration
        self.kbps = self.bps / 1024.0
        logger.debug("TftpMetrics.compute: kbps is %s" % self.kbps)
        for key in self.dups:
            dupcount += self.dups[key]

###############################################################################
# Context classes
###############################################################################

class TftpContext(object):
    """The base class of the contexts."""
    def __init__(self, host, port):
        """Constructor for the base context, setting shared instance
        variables."""
        self.factory = TftpPacketFactory()
        self.host = host
        self.port = port
        # The port associated with the TID
        self.tidport = None
        # Metrics
        self.metrics = TftpMetrics()

    def start(self):
        return NotImplementedError, "Abstract method"

    def end(self):
        return NotImplementedError, "Abstract method"
        
    def gethost(self):
        "Simple getter method for use in a property."
        return self.__host
    
    def sethost(self, host):
        """Setter method that also sets the address property as a result
        of the host that is set."""
        self.__host = host
        self.address = socket.gethostbyname(host)
        
    host = property(gethost, sethost)

    def sendAck(self, blocknumber):
        """This method sends an ack packet to the block number specified."""
        logger.info("sending ack to block %d" % blocknumber)
        ackpkt = TftpPacketACK()
        ackpkt.blocknumber = blocknumber
        self.sock.sendto(ackpkt.encode().buffer, (self.host, self.port))

    def senderror(self, errorcode):
        """This method uses the socket passed, and uses the errorcode to
        compose and send an error packet."""
        logger.debug("In senderror, being asked to send error %d" % errorcode)
        errpkt = TftpPacketERR()
        errpkt.errorcode = errorcode
        sock.sendto(errpkt.encode().buffer, (self.host, self.tidport))

class TftpContextServerDownload(TftpContext):
    """The download context for the server during a download."""
    pass

class TftpContextClientDownload(TftpContext):
    """The download context for the client during a download."""
    def __init__(self, host, port, filename, output, options, packethook, timeout):
        TftpContext.__init__(self, host, port)
        # FIXME - need to support alternate return formats than files?
        # File-like objects would be ideal, ala duck-typing.
        self.requested_file = filename
        self.fileobj = open(output, "wb")
        self.options = options
        self.packethook = packethook
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.settimeout(timeout)

        self.state = None
        self.expected_block = 0

        ############################
        # Logging
        ############################
        logger.debug("TftpContextClientDownload.__init__()")
        logger.debug("requested_file = %s, options = %s" %
            (self.requested_file, self.options))

    def setExpectedBlock(self, block):
        if block > 2 ** 16:
            logger.debug("block number rollover to 0 again")
            block = 0
        self.__eblock = block

    def getExpectedBlock(self):
        return self.__eblock

    expected_block = property(getExpectedBlock, setExpectedBlock)

    def start(self):
        """Initiate the download."""
        logger.info("sending tftp download request to %s" % self.host)
        logger.info("    filename -> %s" % self.requested_file)

        self.metrics.start_time = time.time()
        logger.debug("set metrics.start_time to %s" % self.metrics.start_time)

        # FIXME: put this in a sendRRQ method?
        pkt = TftpPacketRRQ()
        pkt.filename = self.requested_file
        pkt.mode = "octet" # FIXME - shouldn't hardcode this
        pkt.options = self.options
        self.sock.sendto(pkt.encode().buffer, (self.host, self.port))
        self.expected_block = 1

        self.state = TftpStateSentRRQ(self)

        try:
            while self.state:
                logger.debug("state is %s" % self.state)
                self.cycle()
        finally:
            self.fileobj.close()

    def end(self):
        """Finish up the context."""
        self.metrics.end_time = time.time()
        logger.debug("set metrics.end_time to %s" % self.metrics.end_time)
        self.metrics.compute()

    def cycle(self):
        """Here we wait for a response from the server after sending it
        something, and dispatch appropriate action to that response."""
        for i in range(TIMEOUT_RETRIES):
            logger.debug("in cycle, receive attempt %d" % i)
            try:
                (buffer, (raddress, rport)) = self.sock.recvfrom(MAX_BLKSIZE)
            except socket.timeout, err:
                logger.warn("Timeout waiting for traffic, retrying...")
                continue
            break
        else:
            raise TftpException, "Hit max timeouts, giving up."

        # Ok, we've received a packet. Log it.
        logger.debug("Received %d bytes from %s:%s" 
                        % (len(buffer), raddress, rport))

        # Decode it.
        recvpkt = self.factory.parse(buffer)

        # Check for known "connection".
        if raddress != self.address:
            logger.warn("Received traffic from %s, expected host %s. Discarding"
                        % (raddress, self.host))

        if self.port and self.port != rport:
            logger.warn("Received traffic from %s:%s but we're "
                        "connected to %s:%s. Discarding."
                        % (raddress, rport,
                        self.host, self.port))

        # If there is a packethook defined, call it. We unconditionally
        # pass all packets, it's up to the client to screen out different
        # kinds of packets. This way, the client is privy to things like
        # negotiated options.
        if self.packethook:
            self.packethook(recvpkt)

        # And handle it, possibly changing state.
        self.state = self.state.handle(recvpkt, raddress, rport)

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

class TftpStateDownload(TftpState):
    """A class holding common code for download states."""
    def handleDat(self, pkt):
        """This method handles a DAT packet during a download."""
        logger.info("handling DAT packet - block %d" % pkt.blocknumber)
        logger.debug("expecting block %s" % self.context.expected_block)
        if pkt.blocknumber == self.context.expected_block:
            logger.debug("good, received block %d in sequence" 
                        % pkt.blocknumber)
                
            self.context.sendAck(pkt.blocknumber)
            self.context.expected_block += 1

            logger.debug("writing %d bytes to output file" 
                        % len(pkt.data))
            self.context.fileobj.write(pkt.data)
            self.context.metrics.bytes += len(pkt.data)
            # Check for end-of-file, any less than full data packet.
            if len(pkt.data) < int(self.context.options['blksize']):
                logger.info("end of file detected")
                return None

        elif pkt.blocknumber < self.context.expected_block:
            logger.warn("dropping duplicate block %d" % pkt.blocknumber)
            if self.context.metrics.dups.has_key(pkt.blocknumber):
                self.context.metrics.dups[pkt.blocknumber] += 1
            else:
                self.context.metrics.dups[pkt.blocknumber] = 1
            tftpassert(self.context.metrics.dups[pkt.blocknumber] < MAX_DUPS,
                    "Max duplicates for block %d reached" % pkt.blocknumber)
            # FIXME: double-check sorceror's apprentice problem!
            logger.debug("ACKing block %d again, just in case" % pkt.blocknumber)
            self.context.sendAck(pkt.blocknumber)

        else:
            # FIXME: should we be more tolerant and just discard instead?
            msg = "Whoa! Received future block %d but expected %d" \
                % (pkt.blocknumber, self.context.expected_block)
            logger.error(msg)
            raise TftpException, msg

        # Default is to ack
        return TftpStateSentACK(self.context)

class TftpStateSentRRQ(TftpStateDownload):
    """Just sent an RRQ packet."""

    def handle(self, pkt, raddress, rport):
        """Handle the packet in response to an RRQ to the server."""
        if not self.context.tidport:
            self.context.tidport = rport
            logger.debug("Set remote port for session to %s" % rport)

        # Now check the packet type and dispatch it properly.
        if isinstance(pkt, TftpPacketOACK):
            logger.info("Received OACK from server.")
            if pkt.options.keys() > 0:
                if pkt.match_options(self.options):
                    logger.info("Successful negotiation of options")
                    # Set options to OACK options
                    self.options = pkt.options
                    for key in self.options:
                        logger.info("    %s = %s" % (key, self.options[key]))
                    logger.debug("sending ACK to OACK")

                    self.context.sendAck(blocknumber=0)

                    logger.debug("Changing state to TftpStateSentACK")
                    return TftpStateSentACK(self.context)
                else:
                    logger.error("failed to negotiate options")
                    self.senderror(self.sock, TftpErrors.FailedNegotiation, self.host, self.port)
                    raise TftpException, "Failed to negotiate options"

        elif isinstance(pkt, TftpPacketDAT):
            return self.handleDat(pkt)

        # Every other packet type is a problem.
        elif isinstance(recvpkt, TftpPacketACK):
            # Umm, we ACK, the server doesn't.
            self.senderror(self.sock, TftpErrors.IllegalTftpOp)
            raise TftpException, "Received ACK from server while in download"

        elif isinstance(recvpkt, TftpPacketWRQ):
            self.senderror(self.sock, TftpErrors.IllegalTftpOp)
            raise TftpException, "Received WRQ from server while in download"

        elif isinstance(recvpkt, TftpPacketERR):
            self.senderror(self.sock, TftpErrors.IllegalTftpOp)
            raise TftpException, "Received ERR from server: " + str(recvpkt)

        else:
            self.senderror(self.sock, TftpErrors.IllegalTftpOp)
            raise TftpException, "Received unknown packet type from server: " + str(recvpkt)

        # By default, no state change.
        return self

class TftpStateSentACK(TftpStateDownload):
    """Just sent an ACK packet. Waiting for DAT."""
    def handle(self, pkt, raddress, rport):
        """Handle the packet in response to an ACK, which should be a DAT."""
        if isinstance(pkt, TftpPacketDAT):
            return self.handleDat(pkt)

        # Every other packet type is a problem.
        elif isinstance(recvpkt, TftpPacketACK):
            # Umm, we ACK, the server doesn't.
            self.senderror(self.sock, TftpErrors.IllegalTftpOp)
            raise TftpException, "Received ACK from server while in download"

        elif isinstance(recvpkt, TftpPacketWRQ):
            self.senderror(self.sock, TftpErrors.IllegalTftpOp)
            raise TftpException, "Received WRQ from server while in download"

        elif isinstance(recvpkt, TftpPacketERR):
            self.senderror(self.sock, TftpErrors.IllegalTftpOp)
            raise TftpException, "Received ERR from server: " + str(recvpkt)

        else:
            self.senderror(self.sock, TftpErrors.IllegalTftpOp)
            raise TftpException, "Received unknown packet type from server: " + str(recvpkt)
