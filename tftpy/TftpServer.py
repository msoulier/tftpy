# vim: ts=4 sw=4 et ai:
"""This module implements the TFTP Server functionality. Instantiate an
instance of the server, and then run the listen() method to listen for client
requests. Logging is performed via a standard logging object set in
TftpShared."""


import logging
import os
import select
import socket
import struct
import threading
import time
from errno import EINTR

from .TftpContexts import TftpContextServer
from .TftpPacketFactory import TftpPacketFactory
from .TftpPacketTypes import *
from .TftpShared import *

log = logging.getLogger("tftpy.TftpServer")


class TftpServer(TftpSession):
    """This class implements a tftp server object. Run the listen() method to
    listen for client requests.

    tftproot is the path to the tftproot directory to serve files from and/or
    write them to.

    dyn_file_func is a callable that takes a requested download
    path that is not present on the file system and must return either a
    file-like object to read from or None if the path should appear as not
    found. This permits the serving of dynamic content.

    upload_open is a callable that is triggered on every upload with the
    requested destination path and server context. It must either return a
    file-like object ready for writing or None if the path is invalid.

    flock is a boolean to tell the server whether to use advisory locking
    on any real files being read or written in the upload/download."""

    def __init__(self, tftproot="/tftpboot",
                 dyn_file_func=None, upload_open=None, flock=True):
        self.listenip = None
        self.listenport = None
        self.sock = None
        # The address replies are sent from when the destination of a request
        # cannot be learned: the bound address, or "" for a wildcard bind.
        self.replyip = ""
        # A callable receiving (buffer, raddress, rport, localip) when the
        # platform can report each request's destination address, else None.
        self._recv_pktinfo = None
        # FIXME: What about multiple roots?
        self.root = os.path.abspath(tftproot)
        self.dyn_file_func = dyn_file_func
        self.upload_open = upload_open
        # A dict of sessions, where each session is keyed by a string like
        # ip:tid for the remote end.
        self.sessions = {}
        # A threading event to help threads synchronize with the server
        # is_running state.
        self.is_running = threading.Event()

        self.shutdown_gracefully = False
        self.shutdown_immediately = False

        for name in "dyn_file_func", "upload_open":
            attr = getattr(self, name)
            if attr and not callable(attr):
                raise TftpException(
                    f"{name} supplied, but it is not callable.")
        if os.path.exists(self.root):
            log.debug("tftproot %s does exist", self.root)
            if not os.path.isdir(self.root):
                raise TftpException("The tftproot must be a directory.")
            else:
                log.debug("tftproot %s is a directory" % self.root)
                if os.access(self.root, os.R_OK):
                    log.debug("tftproot %s is readable" % self.root)
                else:
                    raise TftpException("The tftproot must be readable")
                if os.access(self.root, os.W_OK):
                    log.debug("tftproot %s is writable" % self.root)
                else:
                    log.warning("The tftproot %s is not writable" % self.root)
        else:
            raise TftpException("The tftproot does not exist.")

    def listen(
        self,
        listenip="",
        listenport=DEF_TFTP_PORT,
        timeout=SOCK_TIMEOUT,
        retries=DEF_TIMEOUT_RETRIES,
    ):
        """Start a server listening on the supplied interface and port. This
        defaults to INADDR_ANY (all interfaces) and UDP port 69. You can also
        supply a different socket timeout value, if desired.

        Replies are sent from the address the client's request was sent to,
        so a host with several addresses (eg. VIPs) answers from the right
        one. With a specific listenip that is listenip itself; with the
        wildcard address it is learned per request via IP_PKTINFO where the
        platform supports it, and left to the kernel's routing otherwise."""
        tftp_factory = TftpPacketFactory()

        # Don't use new 2.5 ternary operator yet
        # listenip = listenip if listenip else '0.0.0.0'
        if not listenip:
            listenip = "0.0.0.0"
        log.info(f"Server requested on ip {listenip}, port {listenport}")
        try:
            # FIXME - sockets should be non-blocking
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.sock.bind((listenip, listenport))
            self.sock.setblocking(0)
            boundip, self.listenport = self.sock.getsockname()
        except OSError as err:
            # Reraise it for now.
            raise err
        self.listenip = listenip

        self._recv_pktinfo = None
        if boundip == "0.0.0.0":
            self.replyip = ""
            self._recv_pktinfo = self._enable_pktinfo()
            if self._recv_pktinfo is None:
                log.info("Cannot learn the destination address of requests "
                         "on this platform; replies may come from a different "
                         "local address than the one the client used")
        else:
            self.replyip = boundip

        self.is_running.set()

        log.info("Starting receive loop...")
        while True:
            log.debug("shutdown_immediately is %s" % self.shutdown_immediately)
            log.debug("shutdown_gracefully is %s" % self.shutdown_gracefully)
            if self.shutdown_immediately:
                log.info("Shutting down now. Session count: %d" %
                         len(self.sessions))
                self.sock.close()
                for key in self.sessions:
                    log.warning("Forcefully closed session with %s" %
                                self.sessions[key].host)
                    self.sessions[key].end()
                self.sessions = {}
                break

            elif self.shutdown_gracefully:
                if not self.sessions:
                    log.info("In graceful shutdown mode and all "
                             "sessions complete.")
                    self.sock.close()
                    break

            # Build the inputlist array of sockets to select() on.
            inputlist = [self.sock]
            for key in self.sessions:
                inputlist.append(self.sessions[key].sock)

            # Block until some socket has input on it.
            log.debug("Performing select on this inputlist: %s", inputlist)
            try:
                readyinput, readyoutput, readyspecial = select.select(
                    inputlist, [], [], timeout
                )
            except OSError as err:
                if err[0] == EINTR:
                    # Interrupted system call
                    log.debug("Interrupted syscall, retrying")
                    continue
                else:
                    raise

            deletion_list = []

            # Handle the available data, if any. Maybe we timed-out.
            for readysock in readyinput:
                # Is the traffic on the main server socket? ie. new session?
                if readysock == self.sock:
                    log.debug("Data ready on our main socket")
                    buffer, raddress, rport, localip = self._recv_request()

                    log.debug("Read %d bytes sent to %s", len(buffer),
                              localip or "an unknown local address")

                    if self.shutdown_gracefully:
                        log.warning(
                            "Discarding data on main port, in graceful shutdown mode"
                        )
                        continue

                    # Forge a session key based on the client's IP and port,
                    # which should safely work through NAT.
                    key = f"{raddress}:{rport}"

                    if key not in self.sessions:
                        log.debug("Creating new server context for session key = %s" % key)
                        self.sessions[key] = TftpContextServer(
                            raddress,
                            rport,
                            timeout,
                            self.root,
                            self.dyn_file_func,
                            self.upload_open,
                            retries=retries,
                            localip=localip,
                        )
                        try:
                            self.sessions[key].start(buffer)
                        except TftpTimeoutExpectACK:
                            self.sessions[key].timeout_expectACK = True
                        except TftpException as err:
                            deletion_list.append(key)
                            log.error(
                                "Fatal exception thrown from session %s: %s"
                                % (key, str(err))
                            )
                    else:
                        log.warning(
                            "received traffic on main socket for existing session??"
                        )
                    log.info("Currently handling these sessions:")
                    for session_key, session in list(self.sessions.items()):
                        log.info("    %s" % session)

                else:
                    # Must find the owner of this traffic.
                    for key in self.sessions:
                        if readysock == self.sessions[key].sock:
                            log.debug("Matched input to session key %s" % key)
                            self.sessions[key].timeout_expectACK = False
                            try:
                                self.sessions[key].cycle()
                                if self.sessions[key].state is None:
                                    log.info("Successful transfer.")
                                    deletion_list.append(key)
                            except TftpTimeoutExpectACK:
                                self.sessions[key].timeout_expectACK = True
                            except TftpException as err:
                                deletion_list.append(key)
                                log.error(
                                    "Fatal exception thrown from session %s: %s"
                                    % (key, str(err))
                                )
                            # Break out of for loop since we found the correct
                            # session.
                            break
                    else:
                        log.error(
                            "Can't find the owner for this packet. Discarding.")

            log.debug("Looping on all sessions to check for timeouts")
            now = time.time()
            for key in self.sessions:
                try:
                    self.sessions[key].checkTimeout(now)
                except TftpTimeout as err:
                    log.error(str(err))
                    self.sessions[key].retry_count += 1
                    if self.sessions[key].retry_count >= self.sessions[key].retries:
                        log.debug(
                            "hit max retries on %s, giving up" % self.sessions[key]
                        )
                        deletion_list.append(key)
                    else:
                        log.debug("resending on session %s" %
                                  self.sessions[key])
                        self.sessions[key].state.resendLast()

            log.debug("Iterating deletion list.")
            for key in deletion_list:
                log.info("")
                log.info("Session %s complete" % key)
                if key in self.sessions:
                    log.debug(
                        "Gathering up metrics from session before deleting")
                    self.sessions[key].end()
                    metrics = self.sessions[key].metrics
                    if metrics.duration == 0:
                        log.info("Duration too short, rate undetermined")
                    else:
                        log.info(
                            "Transferred %d bytes in %.2f seconds"
                            % (metrics.bytes, metrics.duration)
                        )
                        log.info("Average rate: %.2f kbps" % metrics.kbps)
                    log.info("%.2f bytes in resent data" %
                             metrics.resent_bytes)
                    log.info("%d duplicate packets" % metrics.dupcount)
                    log.debug("Deleting session %s" % key)
                    del self.sessions[key]
                    log.debug("Session list is now %s" % self.sessions)
                else:
                    log.warning(
                        "Strange, session %s is not on the deletion list" % key)

        self.is_running.clear()

        log.debug("server returning from while loop")
        self.shutdown_gracefully = self.shutdown_immediately = False

    def _enable_pktinfo(self):
        """Ask the kernel to report the destination address of each datagram
        on the main socket. Returns a callable that receives one datagram as
        (buffer, raddress, rport, localip), or None if that is unsupported."""
        if not hasattr(self.sock, "recvmsg") or not hasattr(socket, "IP_PKTINFO"):
            return None
        try:
            self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_PKTINFO, 1)
        except OSError as err:
            log.debug("Could not enable IP_PKTINFO: %s", err)
            return None
        return self._recvmsg_pktinfo

    def _recvmsg_pktinfo(self, bufsize):
        """Receive one datagram with recvmsg and read its destination address
        from the IP_PKTINFO ancillary data."""
        # struct in_pktinfo { int ipi_ifindex; struct in_addr ipi_spec_dst;
        # struct in_addr ipi_addr; }. ipi_spec_dst is the local address the
        # datagram was received on; unlike ipi_addr it is never a broadcast
        # address, so a reply socket can always be bound to it.
        buffer, ancdata, _, (raddress, rport) = self.sock.recvmsg(
            bufsize, socket.CMSG_SPACE(12))
        localip = ""
        for level, ctype, data in ancdata:
            if (level == socket.IPPROTO_IP and ctype == socket.IP_PKTINFO
                    and len(data) >= 12):
                _, spec_dst, _ = struct.unpack("i4s4s", data[:12])
                localip = socket.inet_ntoa(spec_dst)
        return buffer, raddress, rport, localip

    def _recv_request(self):
        """Receive one datagram on the main socket. Returns (buffer, raddress,
        rport, localip), where localip is the address to reply from, or ""
        to leave that to the kernel."""
        if self._recv_pktinfo is not None:
            buffer, raddress, rport, localip = self._recv_pktinfo(MAX_BLKSIZE)
            return buffer, raddress, rport, localip or self.replyip
        buffer, (raddress, rport) = self.sock.recvfrom(MAX_BLKSIZE)
        return buffer, raddress, rport, self.replyip

    def stop(self, now=False):
        """Stop the server gracefully. Do not take any new transfers,
        but complete the existing ones. If force is True, drop everything
        and stop. Note, immediately will not interrupt the select loop, it
        will happen when the server returns on ready data, or a timeout.
        ie. SOCK_TIMEOUT"""
        if now:
            self.shutdown_immediately = True
        else:
            self.shutdown_gracefully = True
