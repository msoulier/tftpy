import time, types
from TftpShared import *
from TftpPacketFactory import *
from TftpStates import TftpContextClientDownload

class TftpClient(TftpSession):
    """This class is an implementation of a tftp client. Once instantiated, a
    download can be initiated via the download() method."""
    def __init__(self, host, port, options={}):
        """This constructor returns an instance of TftpClient, taking the
        remote host, the remote port, and the filename to fetch."""
        TftpSession.__init__(self)
        self.context = None
        self.host = host
        self.iport = port
        self.filename = None
        self.options = options
        self.blocknumber = 0
        self.fileobj = None
        self.timesent = 0
        self.buffer = None
        self.bytes = 0
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
        "Simple getter method for use in a property."
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
        # We're downloading.
        self.context = TftpContextClientDownload(self.host,
                                                 self.iport,
                                                 filename,
                                                 output,
                                                 self.options,
                                                 packethook,
                                                 timeout)
        self.context.start()
        # Download happens here
        self.context.end()

        metrics = self.context.metrics

        # FIXME: Should we output this? Shouldn't we let the client control
        # output? This should be in the sample client, but not in the download
        # call.
        if metrics.duration == 0:
            logger.info("Duration too short, rate undetermined")
        else:
            logger.info('')
            logger.info("Downloaded %d bytes in %d seconds" % (metrics.bytes, metrics.duration))
            logger.info("Average rate: %.2f kbps" % metrics.kbps)
        logger.info("Received %d duplicate packets" % metrics.dupcount)

    def upload(self, filename, input, packethook=None, timeout=SOCK_TIMEOUT):
        # Open the input file.
        self.fileobj = open(input, "rb")
        recvpkt = None
        curblock = 0
        start_time = time.time()
        self.bytes = 0

        tftp_factory = TftpPacketFactory()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.settimeout(timeout)

        self.filename = filename

        self.send_wrq()
        self.state.state = 'wrq'

        timeouts = 0
        while True:
            try:
                (buffer, (raddress, rport)) = self.sock.recvfrom(MAX_BLKSIZE)
            except socket.timeout, err:
                timeouts += 1
                if timeouts >= TIMEOUT_RETRIES:
                    raise TftpException, "Hit max timeouts, giving up."
                else:
                    if self.state.state == 'dat' or self.state.state == 'fin':
                        logger.debug("Timing out on DAT. Need to resend.")
                        self.send_dat(packethook,resend=True)
                    elif self.state.state == 'wrq':
                        logger.debug("Timing out on WRQ.")
                        self.send_wrq(resend=True)
                    else:
                        tftpassert(False,
                                   "Timing out in unsupported state %s" %
                                   self.state.state)
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

            if not self.port and self.state.state == 'wrq':
                self.port = rport
                logger.debug("Set remote port for session to %s" % rport)

            # Next packet type
            if isinstance(recvpkt, TftpPacketACK):
                logger.debug("Received an ACK from the server.")
                # tftp on wrt54gl seems to answer with an ack to a wrq regardless
                # if we sent options.
                if recvpkt.blocknumber == 0 and self.state.state in ('oack','wrq'):
                    logger.debug("Received ACK with 0 blocknumber, starting upload")
                    self.state.state = 'dat'
                    self.send_dat(packethook)
                else:
                    if self.state.state == 'dat' or self.state.state == 'fin':
                        if self.blocknumber == recvpkt.blocknumber:
                            logger.info("Received ACK for block %d"
                                    % recvpkt.blocknumber)
                            if self.state.state == 'fin':
                                break
                            else:
                                self.send_dat(packethook)
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

            # Check other packet types.
            elif isinstance(recvpkt, TftpPacketOACK):
                if not self.state.state == 'wrq':
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
                        self.state.state = 'dat'
                        self.send_dat(packethook)
                    else:
                        logger.error("failed to negotiate options")
                        self.senderror(self.sock, TftpErrors.FailedNegotiation, self.host, self.port)
                        self.state.state = 'err'
                        raise TftpException, "Failed to negotiate options"

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
        self.fileobj.close()

        end_time = time.time()
        duration = end_time - start_time
        if duration == 0:
            logger.info("Duration too short, rate undetermined")
        else:
            logger.info('')
            logger.info("Uploaded %d bytes in %d seconds" % (self.bytes, duration))
            bps = (self.bytes * 8.0) / duration
            kbps = bps / 1024.0
            logger.info("Average rate: %.2f kbps" % kbps)

    def send_dat(self, packethook, resend=False):
        """This method reads and sends a DAT packet based on what is in self.buffer."""
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
            self.bytes += len(self.buffer)
        else:
            logger.warn("Resending block number %d" % self.blocknumber)
        dat = TftpPacketDAT()
        dat.data = self.buffer
        dat.blocknumber = self.blocknumber
        logger.debug("Sending DAT packet %d" % self.blocknumber)
        self.sock.sendto(dat.encode().buffer, (self.host, self.port))
        self.timesent = time.time()
        if packethook:
            packethook(dat)

    def send_wrq(self, resend=False):
        """This method sends a wrq"""
        logger.info("Sending tftp upload request to %s" % self.host)
        logger.info("    filename -> %s" % self.filename)

        wrq = TftpPacketWRQ()
        wrq.filename = self.filename
        wrq.mode = "octet" # FIXME - shouldn't hardcode this
        wrq.options = self.options
        self.sock.sendto(wrq.encode().buffer, (self.host, self.iport))
