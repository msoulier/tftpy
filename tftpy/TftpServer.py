# vim: ts=4 sw=4 et ai:
# -*- coding: utf8 -*-
"""This module implements the TFTP Server functionality. Instantiate an
instance of the server, and then run the listen() method to listen for client
requests. Logging is performed via a standard logging object set in
TftpShared."""


import grp
import logging
import os
import pwd
import select
import socket
import threading
import time
from errno import EINTR, EPERM, EADDRINUSE
from .TftpShared import *
from .TftpPacketTypes import *
from .TftpPacketFactory import TftpPacketFactory
from .TftpContexts import TftpContextServer

log = logging.getLogger(__name__)


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

    drop_privileges is a tuple containing a uid/user name and gid/group name
    that the process should run as if the process is running with root privs
    and the user would like to drop these privileges after binding a privilegeed
    port

    paranoid is a bool that specifies whether privileges should be permanently
    or temporarily dropped. If True, they will be permanenty dropped using
    setreuid()/setregid(), if False seteuid()/setegid() will be used. This flag
    is only here so that unit tests can succeed since using setre[gu]id() will
    break when executed twice in a process as the process no longer has the
    privs required to perform any set[re][ug]id() calls"""

    def __init__(self,
                 tftproot='/tftpboot',
                 drop_privileges=(None, None),
                 paranoid=False,
                 dyn_file_func=None,
                 upload_open=None):
        self.listenip = None
        self.listenport = None
        self.sock = None
        # Validation of privilege drop parameters is deferred
        self._drop_group = None
        self._drop_user = None
        self._paranoid = paranoid
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

        for name in 'dyn_file_func', 'upload_open':
            attr = getattr(self, name)
            if attr and not callable(attr):
                raise TftpException("{} supplied, but it is not callable.".format(name))
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

        if filter(None, drop_privileges):
            # Only invoke privilege dropping related logic if specfied
            self._normalize_priv_drop(
                drop_privileges)
            # Privilege dropping is requested, normalize the user/group params

    def listen(self, listenip="", listenport=DEF_TFTP_PORT,
               timeout=SOCK_TIMEOUT):
        """Start a server listening on the supplied interface and port. This
        defaults to INADDR_ANY (all interfaces) and UDP port 69. You can also
        supply a different socket timeout value, if desired."""
        tftp_factory = TftpPacketFactory()

        # Don't use new 2.5 ternary operator yet
        # listenip = listenip if listenip else '0.0.0.0'
        if not listenip:
            listenip = '0.0.0.0'
        log.info("Server requested on ip %s, port %s" % (listenip, listenport))

        try:
            # FIXME - sockets should be non-blocking
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.sock.bind((listenip, listenport))
            _, self.listenport = self.sock.getsockname()
        except socket.error as err:
            errno, errmsg = err
            if errno == EPERM:
                raise TftpException(
                    "Permission denied, unable to bind {}:{}'".format(
                        listenip,
                        listenport))
            elif errno == EADDRINUSE:
                raise TftpException(
                    "Address in use, unable to bind {}:{}'".format(
                        listenip,
                        listenport))
            else:
                raise TftpException(
                    'Socket error {}, unable to bind {}:{}'.format(
                        os.strerror(errno),
                        listenip,
                        listenport))

        try:
            if filter(None, (self._drop_group, self._drop_user)):
                self._do_drop_privileges()
        except Exception as err:
            log.error(str(err))
            raise

        self.is_running.set()

        log.info("Starting receive loop...")
        while True:
            log.debug("shutdown_immediately is %s" % self.shutdown_immediately)
            log.debug("shutdown_gracefully is %s" % self.shutdown_gracefully)
            if self.shutdown_immediately:
                log.warning(
                    "Shutting down now. Session count: %d" % len(self.sessions))
                self.sock.close()
                for key in self.sessions:
                    self.sessions[key].end()
                self.sessions = []
                break

            elif self.shutdown_gracefully:
                if not self.sessions:
                    log.warning(
                        "In graceful shutdown mode and all sessions complete.")
                    self.sock.close()
                    break

            # Build the inputlist array of sockets to select() on.
            inputlist = []
            inputlist.append(self.sock)
            for key in self.sessions:
                inputlist.append(self.sessions[key].sock)

            # Block until some socket has input on it.
            log.debug("Performing select on this inputlist: %s", inputlist)
            try:
                readyinput, readyoutput, readyspecial = select.select(
                    inputlist, [], [], SOCK_TIMEOUT)
            except select.error as err:
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
                    buffer, (raddress, rport) = self.sock.recvfrom(MAX_BLKSIZE)

                    log.debug("Read %d bytes", len(buffer))

                    if self.shutdown_gracefully:
                        log.warning("Discarding data on main port, "
                                    "in graceful shutdown mode")
                        continue

                    # Forge a session key based on the client's IP and port,
                    # which should safely work through NAT.
                    key = "%s:%s" % (raddress, rport)

                    if key not in self.sessions:
                        log.debug("Creating new server context for "
                                  "session key = %s" % key)
                        self.sessions[key] = TftpContextServer(
                            raddress,
                            rport,
                            timeout,
                            self.root,
                            self.dyn_file_func,
                            self.upload_open)
                        try:
                            self.sessions[key].start(buffer)
                        except TftpException as err:
                            deletion_list.append(key)
                            log.error("Fatal exception thrown from "
                                      "session %s: %s" % (key, str(err)))
                    else:
                        log.warning("received traffic on main socket for "
                                    "existing session??")
                    log.info("Currently handling these sessions:")
                    for session_key, session in list(self.sessions.items()):
                        log.info("    %s" % session)

                else:
                    # Must find the owner of this traffic.
                    for key in self.sessions:
                        if readysock == self.sessions[key].sock:
                            log.debug("Matched input to session key %s" % key)
                            try:
                                self.sessions[key].cycle()
                                if self.sessions[key].state is None:
                                    log.info("Successful transfer.")
                                    deletion_list.append(key)
                            except TftpException as err:
                                deletion_list.append(key)
                                log.error("Fatal exception thrown from "
                                          "session %s: %s"
                                          % (key, str(err)))
                            # Break out of for loop since we found the correct
                            # session.
                            break
                    else:
                        log.error("Can't find the owner for this packet. "
                                  "Discarding.")

            log.debug("Looping on all sessions to check for timeouts")
            now = time.time()
            for key in self.sessions:
                try:
                    self.sessions[key].checkTimeout(now)
                except TftpTimeout as err:
                    log.error(str(err))
                    self.sessions[key].retry_count += 1
                    if self.sessions[key].retry_count >= TIMEOUT_RETRIES:
                        log.debug("hit max retries on %s, giving up" % (
                            self.sessions[key]))
                        deletion_list.append(key)
                    else:
                        log.debug("resending on session %s" % self.sessions[key])
                        self.sessions[key].state.resendLast()

            log.debug("Iterating deletion list.")
            for key in deletion_list:
                log.info('')
                log.info("Session %s complete" % key)
                if key in self.sessions:
                    log.debug("Gathering up metrics from session before deleting")
                    self.sessions[key].end()
                    metrics = self.sessions[key].metrics
                    if metrics.duration == 0:
                        log.info("Duration too short, rate undetermined")
                    else:
                        log.info("Transferred %d bytes in %.2f seconds" % (
                            metrics.bytes, metrics.duration))
                        log.info("Average rate: %.2f kbps" % metrics.kbps)
                    log.info("%.2f bytes in resent data" % metrics.resent_bytes)
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

    def _do_drop_privileges(self):
        """Drop user and/or group privileges, called after bind()

        Filesystem access controls are based on the effective userid so all
        that is necessary is seteuid()/setegid() to *temporarily* drop privs.
        However, the process can always perform an os.seteuid(0);os.setegid(0)
        and revert back to root. This is a danger if there is some logic flaw
        or internal flaw in the Python engine that allows a user to execute
        arbitrary code in the process since they will be able to reclaim full
        root privileges. Very unlikely, but possible

        A more secure way to do this would be to *permanently* drop privileges
        with setregid()/setreuid() but this breaks unit tests since the process
        can't reclaim root, which it needs to do to perform more than one priv
        dropping test case, all in the same process. As a workaround, the default
        is paranoid mode and the unit tests set pranoid=False so that multiple
        tests in the same process can switch back and forth from root
        """

        # See function docstring for explanation of this block
        if self._paranoid is True:
            dropgid = os.setregid
            dropgid_args = (self._drop_group, self._drop_group)
            dropuid = os.setreuid
            dropuid_args = (self._drop_user, self._drop_user)
        else:
            dropgid = os.setegid
            dropgid_args = (self._drop_group, )
            dropuid = os.seteuid
            dropuid_args = (self._drop_user, )

        log.info('Dropping privileges from root (paranoid mode %s' % (
            'disabled' if self._paranoid is False else 'enabled'))
        os.setgroups([])
        if self._drop_group is not None:
            if dropgid(*dropgid_args):
                raise OSError('setegid() failed')
            log.info('Dropped group to gid=%d' % self._drop_group)
        else:
            log.info('User elected to not drop group ID')
        if self._drop_user is not None:
            if dropuid(*dropuid_args):
                raise OSError('seteuid() faiiled')
            log.info('Dropped user to uid=%d' % self._drop_user)
        else:
            log.info('User elected to not drop user ID')

        uid, gid = os.getuid(), os.getgid()
        euid, egid = os.geteuid(), os.getegid()
        log.info('Serving TFTP as uid=%d,euid=%d,gid=%d,egid=%d, ' % (
            uid, euid, gid, egid))
        log.info('Filesystem access checks will be checked using euid')

    def _normalize_priv_drop(self, privs):
        """Normalize and sanity check for privilege dropping"""

        def normalize_group(group):
            """Given a GID or group name, return a validated system GID"""
            if group is None:
                return None
            try:
                group = int(group)
            except ValueError:
                pass
            groupname = groupid = None
            if isinstance(group, basestring):
                """Get the numeric GID"""
                groupname = group
                try:
                    groupid = grp.getgrnam(groupname).gr_gid
                except KeyError:
                    log.error('Group name "%s" does not exist' % group_name)
            elif isinstance(group, int):
                """Validate a numeric GID"""
                groupid = group
                try:
                    groupname = grp.getgrgid(groupid).gr_name
                except KeyError:
                    log.error('Group ID #%d does not exist' % groupid)
            else:
                raise TypeError('Expected int or basestring for system group')
            if None in (groupname, groupid):
                raise ValueError('Invalid system group, unable to resolve')

            return groupid

        def normalize_user(user):
            """Given a UID or user name, return a validated system UID"""
            if user is None:
                return None
            try:
                user = int(user)
            except ValueError:
                pass
            username = userid = None
            if isinstance(user, basestring):
                # Get the numeric UID from a username
                username = user
                try:
                    userid = pwd.getpwnam(username).pw_uid
                except KeyError:
                    log.error('User name "%s" does not exist' % username)
            elif isinstance(user, int):
                # Validate a numeric ID
                userid = user
                try:
                    username = pwd.getpwuid(userid).pw_name
                except KeyError:
                    log.error('User ID #%d does not exist' % userid)
            else:
                raise TypeError('Expected int or basestring for system user')
            if None in (username, userid):
                raise ValueError('Invalid system user, unable to resolve')
            return userid

        def assert_droppable():
            uid = os.getuid()
            if uid != 0:
                log.error('Requested to drop permissions as non-root user!')
                # Should this be a TftpException?
                raise RuntimeError(
                    'Unable to drop permissions as non-root user %d' % uid)

            if os.name != 'posix':
                log.error('Requested to drop privileges on unsupported system!')
                # Should this be a TftpException?
                raise RuntimeError(
                    'Unable to drop privileges, posix systems only')

        if not isinstance(privs, (list, tuple)):
            raise TypeError(
                'drop_privileges should be a list or tuple')

        if len(privs) != 2:
            raise ValueError('drop_privileges should contain two elements')

        assert_droppable()

        filtered = list(filter(None, privs))  # Sanitize only non-None

        if list(filter(lambda v: not isinstance(v, (basestring, int)), filtered)):
            print(filtered)
            log.error('drop_privileges must contain only strings or integers')
            raise ValueError('Invalid ')

        self._drop_user = normalize_user(privs[0])
        self._drop_group = normalize_group(privs[1])

