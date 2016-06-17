"""This module implements the TFTP Server functionality. Instantiate an
instance of the server, and then run the listen() method to listen for client
requests. Logging is performed via a standard logging object set in
TftpShared."""

import socket, os, time
import select, errno
import threading
from errno import EINTR
from TftpShared import *
from TftpPacketTypes import *
from TftpPacketFactory import TftpPacketFactory
from TftpContexts import TftpContextServer

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
    file-like object ready for writing or None if the path is invalid."""

    def __init__(self,
                 tftproot='/tftpboot',
                 dyn_file_func=None,
                 upload_open=None):
        self.listenip = None
        self.listenport = None
        self.sock = None
        # FIXME: What about multiple roots?
        self.root = os.path.abspath(tftproot)
        self.dyn_file_func = dyn_file_func
        self.upload_open = upload_open
        # A dict of sessions, where each session is keyed by a string like
        # ip:tid for the remote end.
        self.sessions = {}
        self.session_keys = {}
        # A threading event to help threads synchronize with the server
        # is_running state.
        self.is_running = threading.Event()

        self.shutdown_gracefully = False
        self.shutdown_immediately = False

        # Poll structure for the listen loop
        try:
            self.poll = select.epoll()
            self.poll_mask = select.EPOLLIN | select.EPOLLERR
            self.poll_mask_in = select.EPOLLIN
            self.poll_mask_err = select.EPOLLERR | select.EPOLLHUP
        except:
            self.poll = select.poll()
            self.poll_mask = select.POLLIN | select.POLLERR
            self.poll_mask_in = select.POLLIN
            self.poll_mask_err = select.POLLERR | select.POLLHUP

        for name in 'dyn_file_func', 'upload_open':
            attr = getattr(self, name)
            if attr and not callable(attr):
                raise TftpException, "%s supplied, but it is not callable." % (
                    name,)
        if os.path.exists(self.root):
            log.debug("tftproot %s does exist", self.root)
            if not os.path.isdir(self.root):
                raise TftpException, "The tftproot must be a directory."
            else:
                log.debug("tftproot %s is a directory", self.root)
                if os.access(self.root, os.R_OK):
                    log.debug("tftproot %s is readable", self.root)
                else:
                    raise TftpException, "The tftproot must be readable"
                if os.access(self.root, os.W_OK):
                    log.debug("tftproot %s is writable", self.root)
                else:
                    log.warning("The tftproot %s is not writable" % self.root)
        else:
            raise TftpException, "The tftproot does not exist."

    def listen(self,
               listenip="",
               listenport=DEF_TFTP_PORT,
               timeout=SOCK_TIMEOUT):
        """Start a server listening on the supplied interface and port. This
        defaults to INADDR_ANY (all interfaces) and UDP port 69. You can also
        supply a different socket timeout value, if desired."""
        tftp_factory = TftpPacketFactory()

        # Don't use new 2.5 ternary operator yet
        # listenip = listenip if listenip else '0.0.0.0'
        if not listenip: listenip = '0.0.0.0'
        log.info("Server requested on ip %s, port %s"
                % (listenip, listenport))
        try:
            # FIXME - sockets should be non-blocking
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.sock.bind((listenip, listenport))
            _, self.listenport = self.sock.getsockname()
        except socket.error, err:
            # Reraise it for now.
            raise

        self.is_running.set()

        self.poll.register(self.sock.fileno(), self.poll_mask)

        log.info("Starting receive loop...")
        while True:
            log.debug("shutdown_immediately is %s", self.shutdown_immediately)
            log.debug("shutdown_gracefully is %s", self.shutdown_gracefully)
            if self.shutdown_immediately:
                log.warn("Shutting down now. Session count: %d" % len(self.sessions))
                self.poll.unregister(self.sock.fileno())
                self.sock.close()
                for key in self.sessions:
                    fd = self.sessions[key].sock.fileno()
                    self.poll.unregister(fd)
                    del self.session_keys[fd]
                    self.sessions[key].end()
                self.sessions = []
                break

            elif self.shutdown_gracefully:
                if not self.sessions:
                    log.warn("In graceful shutdown mode and all sessions complete.")
                    self.poll.unregister(self.sock.fileno())
                    self.sock.close()
                    break

            # Block until some socket has input on it.
            try:
                log.debug("Performing poll with timeout %s", SOCK_TIMEOUT)
                events = self.poll.poll(SOCK_TIMEOUT * 1000)
            except select.error, (err, _):
                if err != errno.EAGAIN and err != errno.EINTR:
                    log.error("poll failed with: %d", err)
                    self.shutdown_immediately = True
                continue
            except IOError, e:
                if e.errno != errno.EINTR:
                    raise
                events = []

            deletion_list = []
            log.debug("Woke up with events: %s", events)

            # Handle the available data, if any. Maybe we timed-out.
            for readysock, event in events:
                if event & self.poll_mask_err:
                    log.error("poll received error or HUP: %d", err)
                    self.shutdown_immediately = True
                    continue
                elif not (event & self.poll_mask_in):
                    log.warn("poll received bad event: %x", event)
                    continue

                # Is the traffic on the main server socket? ie. new session?
                if readysock == self.sock.fileno():
                    log.debug("Data ready on our main socket")
                    buffer, (raddress, rport) = self.sock.recvfrom(MAX_BLKSIZE)

                    log.debug("Read %d bytes", len(buffer))

                    if self.shutdown_gracefully:
                        log.warn("Discarding data on main port, in graceful shutdown mode")
                        continue

                    # Forge a session key based on the client's IP and port,
                    # which should safely work through NAT.
                    key = "%s:%s" % (raddress, rport)

                    if not self.sessions.has_key(key):
                        log.debug("Creating new server context for "
                                     "session key = %s", key)
                        self.sessions[key] = TftpContextServer(raddress,
                                                               rport,
                                                               timeout,
                                                               self.root,
                                                               self.dyn_file_func,
                                                               self.upload_open)
                        try:
                            self.sessions[key].start(buffer)
                            fd = self.sessions[key].sock.fileno()
                            self.poll.register(fd, self.poll_mask)
                            self.session_keys[fd] = key
                        except TftpException, err:
                            deletion_list.append(key)
                            log.error("Fatal exception thrown from "
                                      "session %s: %s" % (key, str(err)))
                    else:
                        log.warn("received traffic on main socket for "
                                 "existing session??")
                    log.info("Currently handling these sessions:")
                    for session_key, session in self.sessions.items():
                        log.info("    %s" % session)

                else:
                    # Must find the owner of this traffic.
                    try:
                        key = self.session_keys[readysock]
                        log.info("Matched input to session key %s" % key)
                        try:
                            self.sessions[key].cycle()
                            if self.sessions[key].state == None:
                                log.info("Successful transfer.")
                                deletion_list.append(key)
                        except TftpException, err:
                            deletion_list.append(key)
                            log.error("Fatal exception thrown from "
                                      "session %s: %s"
                                      % (key, str(err)))
                        # Break out of for loop since we found the correct
                        # session.
                        break
                    except KeyError:
                        log.error("Can't find the owner for this packet. "
                                  "Discarding.")

            log.debug("Looping on all sessions to check for timeouts")
            now = time.time()
            for key in self.sessions:
                try:
                    self.sessions[key].checkTimeout(now)
                except TftpTimeout, err:
                    log.error(str(err))
                    self.sessions[key].retry_count += 1
                    if self.sessions[key].retry_count >= TIMEOUT_RETRIES:
                        log.debug("hit max retries on %s, giving up",
                            self.sessions[key])
                        deletion_list.append(key)
                    else:
                        log.debug("resending on session %s", self.sessions[key])
                        self.sessions[key].state.resendLast()

            log.debug("Iterating deletion list.")
            for key in deletion_list:
                log.info('')
                log.info("Session %s complete" % key)
                if self.sessions.has_key(key):
                    log.debug("Gathering up metrics from session before deleting")
                    fd = self.sessions[key].sock.fileno()
                    self.poll.unregister(fd)
                    del self.session_keys[fd]
                    self.sessions[key].end()
                    metrics = self.sessions[key].metrics
                    if metrics.duration == 0:
                        log.info("Duration too short, rate undetermined")
                    else:
                        log.info("Transferred %d bytes in %.2f seconds"
                            % (metrics.bytes, metrics.duration))
                        log.info("Average rate: %.2f kbps" % metrics.kbps)
                    log.info("%.2f bytes in resent data" % metrics.resent_bytes)
                    log.info("%d duplicate packets" % metrics.dupcount)
                    log.debug("Deleting session %s", key)
                    del self.sessions[key]
                    log.debug("Session list is now %s", self.sessions)
                else:
                    log.warn("Strange, session %s is not on the deletion list"
                        % key)

        self.is_running.clear()

        log.debug("server returning from while loop")
        self.shutdown_gracefully = self.shutdown_immediately = False

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
