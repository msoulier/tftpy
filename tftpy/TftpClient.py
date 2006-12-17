import socket, time, types
from TftpShared import *
from TftpPacketFactory import *

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
