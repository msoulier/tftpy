import multiprocessing
import time
import os
import tempfile
import unittest
import logging
import select
import socket
import sys
import threading
import tftpy
from io import BytesIO
from multiprocessing import Queue
from pathlib import Path
import subprocess
from contextlib import contextmanager
from shutil import rmtree
from unittest.mock import call, patch

from tftpy.TftpContexts import TftpContextClientUpload
from tftpy.TftpPacketFactory import TftpPacketFactory
from tftpy.TftpPacketTypes import TftpPacketDAT, TftpPacketRRQ

log = logging.getLogger("tftpy")
log.setLevel(logging.DEBUG)

# console handler
handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(levelname)s [%(name)s:%(lineno)s] %(message)s")
handler.setFormatter(formatter)
log.addHandler(handler)

# Module-level function (can be pickled)
def start_tftp_server(root_dir, port, ready_queue):
    try:
        import tftpy
        server = tftpy.TftpServer(root_dir)
        ready_queue.put("ready")  # Signal ready
        server.listen('localhost', port)
    except Exception as e:
        ready_queue.put(f"error: {e}")

class TestTftpyClasses(unittest.TestCase):
    def testTftpPacketRRQ(self):
        log.debug("===> Running testcase testTftpPacketRRQ")
        options = {}
        rrq = tftpy.TftpPacketTypes.TftpPacketRRQ()
        rrq.filename = "myfilename"
        rrq.mode = "octet"
        rrq.options = options
        rrq.encode()
        self.assertIsNotNone(rrq.buffer, "Buffer populated")
        rrq.decode()
        self.assertEqual(rrq.filename, "myfilename", "Filename correct")
        self.assertEqual(rrq.mode, "octet", "Mode correct")
        self.assertEqual(rrq.options, options, "Options correct")
        # repeat test with options
        rrq.options = {"blksize": "1024"}
        rrq.filename = "myfilename"
        rrq.mode = "octet"
        rrq.encode()
        self.assertIsNotNone(rrq.buffer, "Buffer populated")
        rrq.decode()
        self.assertEqual(rrq.filename, "myfilename", "Filename correct")
        self.assertEqual(rrq.mode, "octet", "Mode correct")
        self.assertEqual(rrq.options["blksize"], "1024", "blksize correct")

    def testTftpPacketWRQ(self):
        log.debug("===> Running test case testTftpPacketWRQ")
        options = {}
        wrq = tftpy.TftpPacketTypes.TftpPacketWRQ()
        wrq.filename = "myfilename"
        wrq.mode = "octet"
        wrq.options = options
        wrq.encode()
        self.assertIsNotNone(wrq.buffer, "Buffer populated")
        wrq.decode()
        self.assertEqual(wrq.opcode, 2, "Opcode correct")
        self.assertEqual(wrq.filename, "myfilename", "Filename correct")
        self.assertEqual(wrq.mode, "octet", "Mode correct")
        self.assertEqual(wrq.options, options, "Options correct")
        # repeat test with options
        wrq.options = {"blksize": "1024"}
        wrq.filename = "myfilename"
        wrq.mode = "octet"
        wrq.encode()
        self.assertIsNotNone(wrq.buffer, "Buffer populated")
        wrq.decode()
        self.assertEqual(wrq.opcode, 2, "Opcode correct")
        self.assertEqual(wrq.filename, "myfilename", "Filename correct")
        self.assertEqual(wrq.mode, "octet", "Mode correct")
        self.assertEqual(wrq.options["blksize"], "1024", "Blksize correct")

    def testTftpPacketDAT(self):
        log.debug("===> Running testcase testTftpPacketDAT")
        dat = tftpy.TftpPacketTypes.TftpPacketDAT()
        dat.blocknumber = 5
        data = b"this is some data"
        dat.data = data
        dat.encode()
        self.assertIsNotNone(dat.buffer, "Buffer populated")
        dat.decode()
        self.assertEqual(dat.opcode, 3, "DAT opcode is correct")
        self.assertEqual(dat.blocknumber, 5, "Block number is correct")
        self.assertEqual(dat.data, data, "DAT data is correct")

    def testTftpPacketACK(self):
        log.debug("===> Running testcase testTftpPacketACK")
        ack = tftpy.TftpPacketTypes.TftpPacketACK()
        ack.blocknumber = 6
        ack.encode()
        self.assertIsNotNone(ack.buffer, "Buffer populated")
        ack.decode()
        self.assertEqual(ack.opcode, 4, "ACK opcode is correct")
        self.assertEqual(ack.blocknumber, 6, "ACK blocknumber correct")

    def testTftpPacketERR(self):
        log.debug("===> Running testcase testTftpPacketERR")
        err = tftpy.TftpPacketTypes.TftpPacketERR()
        err.errorcode = 4
        err.encode()
        self.assertIsNotNone(err.buffer, "Buffer populated")
        err.decode()
        self.assertEqual(err.opcode, 5, "ERR opcode is correct")
        self.assertEqual(err.errorcode, 4, "ERR errorcode is correct")

    def testTftpPacketOACK(self):
        log.debug("===> Running testcase testTftpPacketOACK")
        oack = tftpy.TftpPacketTypes.TftpPacketOACK()
        # Test that if we make blksize a number, it comes back a string.
        oack.options = {"blksize": 2048}
        oack.encode()
        self.assertIsNotNone(oack.buffer, "Buffer populated")
        oack.decode()
        self.assertEqual(oack.opcode, 6, "OACK opcode is correct")
        self.assertEqual(
            oack.options["blksize"], "2048", "OACK blksize option is correct"
        )
        # Test string to string
        oack.options = {"blksize": "4096"}
        oack.encode()
        self.assertIsNotNone(oack.buffer, "Buffer populated")
        oack.decode()
        self.assertEqual(oack.opcode, 6, "OACK opcode is correct")
        self.assertEqual(
            oack.options["blksize"], "4096", "OACK blksize option is correct"
        )

    def testTftpPacketFactory(self):
        log.debug("===> Running testcase testTftpPacketFactory")
        # Make sure that the correct class is created for the correct opcode.
        classes = {
            1: tftpy.TftpPacketTypes.TftpPacketRRQ,
            2: tftpy.TftpPacketTypes.TftpPacketWRQ,
            3: tftpy.TftpPacketTypes.TftpPacketDAT,
            4: tftpy.TftpPacketTypes.TftpPacketACK,
            5: tftpy.TftpPacketTypes.TftpPacketERR,
            6: tftpy.TftpPacketTypes.TftpPacketOACK,
        }
        factory = tftpy.TftpPacketFactory.TftpPacketFactory()
        for opcode in classes:
            self.assertTrue(
                isinstance(factory._TftpPacketFactory__create(opcode), classes[opcode]),
                "opcode %d returns the correct class" % opcode,
            )
        packet = factory.parse(b'\x00\x04\x00\x00')
        self.assertEqual(packet.opcode, 4)
        with self.assertRaisesRegex(tftpy.TftpShared.TftpException, 'Invalid packet size'):
            factory.parse(b'\x00\x04')


class TftpContextClientUploadCleanupTest(unittest.TestCase):
    """Verify that an upload context only closes resources it owns."""

    def make_context(self, input_obj):
        """Create a context without starting a network transfer."""
        return TftpContextClientUpload(
            host="127.0.0.1",
            port=69,
            filename="remote.bin",
            input=input_obj,
            options={},
            packethook=None,
            timeout=1,
        )

    def test_file_like_input_remains_open(self):
        input_obj = BytesIO(b"upload contents")
        self.addCleanup(input_obj.close)

        context = self.make_context(input_obj)
        # Leaving the context must close the socket, but the caller retains
        # ownership of a supplied file-like object.
        with context:
            pass

        self.assertFalse(input_obj.closed)
        self.assertEqual(input_obj.getvalue(), b"upload contents")
        self.assertEqual(context.sock.fileno(), -1)

    def test_path_input_is_unlocked_and_closed(self):
        with tempfile.TemporaryDirectory() as tempdir:
            input_path = Path(tempdir) / "input.bin"
            input_path.write_bytes(b"upload contents")

            # A path is opened by TftpContextClientUpload, so the context must
            # pair its initial lock with an unlock and close the opened file.
            with patch("tftpy.TftpContexts.lockfile") as lockfile:
                context = self.make_context(input_path)
                opened_file = context.fileobj

                with context:
                    pass

            self.assertTrue(opened_file.closed)
            self.assertEqual(context.sock.fileno(), -1)
            self.assertEqual(
                lockfile.call_args_list,
                [
                    call(opened_file, shared=True, blocking=False),
                    call(opened_file, unlock=True),
                ],
            )


def can_bind(address):
    """Whether a UDP socket can be bound to address on this host."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.bind((address, 0))
        return True
    except OSError:
        return False
    finally:
        sock.close()


# 127.0.0.2 stands in for a VIP or secondary address: it is local, but the
# kernel routes replies to 127.0.0.1 from 127.0.0.1 unless told otherwise.
SECONDARY_IP = "127.0.0.2"


@unittest.skipUnless(can_bind(SECONDARY_IP),
                     f"{SECONDARY_IP} is not a usable local address here")
class TftpServerReplyAddressTest(unittest.TestCase):
    """Verify that the server replies from the address a request was sent to,
    which clients and firewalls on multi-address hosts depend on."""

    def start_server(self, listenip):
        """Run a server on listenip and an ephemeral port in a thread."""
        root = tempfile.mkdtemp()
        self.addCleanup(rmtree, root, ignore_errors=True)
        Path(root, "hello.bin").write_bytes(b"hello")

        server = tftpy.TftpServer(root)
        thread = threading.Thread(
            target=server.listen,
            kwargs={"listenip": listenip, "listenport": 0, "timeout": 1},
            daemon=True,
        )
        thread.start()
        self.assertTrue(server.is_running.wait(5), "server did not start")
        # Cleanups run last-in first-out: stop the server, then join it.
        self.addCleanup(thread.join, 5)
        self.addCleanup(server.stop, now=True)
        return server

    def request_reply_address(self, server):
        """Send an RRQ to SECONDARY_IP from 127.0.0.1, and return the address
        the reply came from along with the parsed reply."""
        client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.addCleanup(client.close)
        client.bind(("127.0.0.1", 0))
        client.settimeout(5)

        rrq = TftpPacketRRQ()
        rrq.filename = "hello.bin"
        rrq.mode = "octet"
        rrq.options = {}
        client.sendto(rrq.encode().buffer, (SECONDARY_IP, server.listenport))
        buffer, (replyip, _) = client.recvfrom(tftpy.MAX_BLKSIZE)
        return replyip, TftpPacketFactory().parse(buffer)

    def test_reply_from_listen_address(self):
        server = self.start_server(SECONDARY_IP)
        replyip, reply = self.request_reply_address(server)
        self.assertIsInstance(reply, TftpPacketDAT)
        self.assertEqual(replyip, SECONDARY_IP)

    @unittest.skipUnless(
        sys.platform == "win32" or (
            hasattr(socket.socket, "recvmsg") and hasattr(socket, "IP_PKTINFO")),
        "this platform cannot report the destination address of a request")
    def test_reply_from_request_destination_with_wildcard_listen(self):
        server = self.start_server("0.0.0.0")
        replyip, reply = self.request_reply_address(server)
        self.assertIsInstance(reply, TftpPacketDAT)
        self.assertEqual(replyip, SECONDARY_IP)

    def test_unbindable_reply_address_falls_back_to_kernel_choice(self):
        # A destination address that cannot be bound, as Windows reports for
        # a broadcast request, must not lose the request.
        original = tftpy.TftpServer._recv_request

        def recv_request(server):
            buffer, raddress, rport, _ = original(server)
            return buffer, raddress, rport, "192.0.2.1"

        with patch.object(tftpy.TftpServer, "_recv_request", recv_request):
            server = self.start_server("0.0.0.0")
            replyip, reply = self.request_reply_address(server)
        self.assertIsInstance(reply, TftpPacketDAT)
        self.assertEqual(replyip, "127.0.0.1")


@unittest.skipUnless(sys.platform == "win32", "Windows only")
@unittest.skipUnless(can_bind(SECONDARY_IP),
                     f"{SECONDARY_IP} is not a usable local address here")
class TftpWinsockTest(unittest.TestCase):
    """Verify the WSARecvMsg-based receiver used on Windows."""

    def make_receiver(self):
        from tftpy import _winsock

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.addCleanup(sock.close)
        sock.bind(("0.0.0.0", 0))
        sock.setblocking(False)
        return sock, _winsock.make_pktinfo_receiver(sock)

    def test_reports_destination_address(self):
        sock, receive = self.make_receiver()
        client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.addCleanup(client.close)
        client.bind(("127.0.0.1", 0))
        client.sendto(b"hello", (SECONDARY_IP, sock.getsockname()[1]))

        select.select([sock], [], [], 5)
        buffer, raddress, rport, localip = receive(tftpy.MAX_BLKSIZE)
        self.assertEqual(buffer, b"hello")
        self.assertEqual((raddress, rport), client.getsockname())
        self.assertEqual(localip, SECONDARY_IP)

    def test_empty_nonblocking_socket_raises_like_recvfrom(self):
        _, receive = self.make_receiver()
        with self.assertRaises(BlockingIOError):
            receive(tftpy.MAX_BLKSIZE)


class TftpyTestCase(unittest.TestCase):
    """Better approaches to defining the server function"""
    
    def setUp(self):
        self.server_port = 9071
        self.server_root = tempfile.mkdtemp()

    def clientServerUploadOptions(
        self, options, input=None, transmitname=None, server_kwargs={}
    ):
        """Fire up a client and a server and do an upload."""
        with multiprocessing.Manager() as manager:
            ready_queue = manager.Queue()
            
            server_process = multiprocessing.Process(
                target=start_tftp_server,
                args=(self.server_root, self.server_port, ready_queue)
            )
            server_process.start()

            try:
                # Wait for ready signal
                msg = ready_queue.get(timeout=5)
                if msg.startswith("error"):
                    self.fail(f"Server failed: {msg}")

                home = os.path.dirname(os.path.abspath(__file__))
                filename = "640KBFILE"
                input_path = os.path.join(home, filename)
                if not input:
                    input = input_path
                if transmitname:
                    filename = transmitname

                client = tftpy.TftpClient("localhost", self.server_port, options)

                client.upload(filename, input)

            finally:
                server_process.terminate()
                server_process.join()

    def clientServerDownloadOptions(
        self,
        options,
        output="/tmp/out",
        cretries=tftpy.DEF_TIMEOUT_RETRIES,
        sretries=tftpy.DEF_TIMEOUT_RETRIES,
        flock=True
    ):
        """Fire up a client and a server and do a download."""
        with multiprocessing.Manager() as manager:
            ready_queue = manager.Queue()
            
            server_process = multiprocessing.Process(
                target=start_tftp_server,
                args=(self.server_root, self.server_port, ready_queue)
            )
            server_process.start()

            try:
                msg = ready_queue.get(timeout=5)
                if msg.startswith("error"):
                    self.fail(f"Server failed: {msg}")

                client = tftpy.TftpClient("localhost", 20001, options)

                client.download("640KBFILE", output, retries=cretries)

            finally:
                server_process.terminate()
                server_process.join()

    @contextmanager
    def dummyServerDir(self):
        tmpdir = tempfile.mkdtemp()
        for dirname in ("foo", "foo-private", "other", "with spaces"):
            os.mkdir(os.path.join(tmpdir, dirname))
            with open(os.path.join(tmpdir, dirname, "bar"), "w") as w:
                w.write("baz")

        try:
            yield tmpdir
        finally:
            rmtree(tmpdir)

    def testClientServerUploadNoOptions(self):
        self.clientServerUploadOptions({})

    def testClientServerUploadFileObj(self):
        fileobj = open("tests/640KBFILE", "rb")
        self.clientServerUploadOptions({}, input=fileobj)

    def testClientServerUploadWithSubdirs(self):
        self.clientServerUploadOptions({}, transmitname="foo/bar/640KBFILE")

    def testClientServerUploadStartingSlash(self):
        self.clientServerUploadOptions({}, transmitname="/foo/bar/640KBFILE")

    def testClientServerUploadOptions(self):
        for blksize in [512, 1024, 2048, 4096]:
            self.clientServerUploadOptions({"blksize": blksize})

#    def customUploadHelper(self, return_func):
#        q = Queue()
#
#        def upload_open(path, context):
#            q.put("called")
#            return return_func(path)
#
#        self.clientServerUploadOptions({}, server_kwargs={"upload_open": upload_open})
#        self.assertEqual(q.get(True, 1), "called")
#
#    def testClientServerUploadCustomOpen(self):
#        self.customUploadHelper(lambda p: open(p, "wb"))
#
#    def testClientServerUploadCustomOpenForbids(self):
#        with self.assertRaisesRegex(tftpy.TftpException, "Access violation"):
#            self.customUploadHelper(lambda p: None)
#
#    def testClientServerUploadTsize(self):
#        self.clientServerUploadOptions(
#            {"tsize": 64 * 1024}, transmitname="/foo/bar/640KBFILE"
#        )
#
#    def testClientServerNoOptionsDelay(self):
#        tftpy.TftpStates.DELAY_BLOCK = 10
#        self.clientServerDownloadOptions({})
#        tftpy.TftpStates.DELAY_BLOCK = 0
#
#    def testServerNoOptions(self):
#        raddress = "127.0.0.2"
#        rport = 10000
#        timeout = 5
#        root = os.path.dirname(os.path.abspath(__file__))
#        # Testing without the dyn_func_file set.
#        serverstate = tftpy.TftpContexts.TftpContextServer(
#            raddress, rport, timeout, root
#        )
#
#        self.assertTrue(isinstance(serverstate, tftpy.TftpContexts.TftpContextServer))
#
#        rrq = tftpy.TftpPacketTypes.TftpPacketRRQ()
#        rrq.filename = "640KBFILE"
#        rrq.mode = "octet"
#        rrq.options = {}
#
#        # Start the download.
#        serverstate.start(rrq.encode().buffer)
#        # At a 512 byte blocksize, this should be 1280 packets exactly.
#        for block in range(1, 1281):
#            # Should be in expectack state.
#            self.assertTrue(
#                isinstance(serverstate.state, tftpy.TftpStates.TftpStateExpectACK)
#            )
#            ack = tftpy.TftpPacketTypes.TftpPacketACK()
#            ack.blocknumber = block % 65536
#            serverstate.state = serverstate.state.handle(ack, raddress, rport)
#
#        # The last DAT packet should be empty, indicating a completed
#        # transfer.
#        ack = tftpy.TftpPacketTypes.TftpPacketACK()
#        ack.blocknumber = 1281 % 65536
#        finalstate = serverstate.state.handle(ack, raddress, rport)
#        self.assertTrue(finalstate is None)
#
#    def testServerTimeoutExpectACK(self):
#        raddress = "127.0.0.2"
#        rport = 10000
#        timeout = 5
#        root = os.path.dirname(os.path.abspath(__file__))
#        # Testing without the dyn_func_file set.
#        serverstate = tftpy.TftpContexts.TftpContextServer(
#            raddress, rport, timeout, root
#        )
#
#        self.assertTrue(isinstance(serverstate, tftpy.TftpContexts.TftpContextServer))
#
#        rrq = tftpy.TftpPacketTypes.TftpPacketRRQ()
#        rrq.filename = "640KBFILE"
#        rrq.mode = "octet"
#        rrq.options = {}
#
#        # Start the download.
#        serverstate.start(rrq.encode().buffer)
#
#        ack = tftpy.TftpPacketTypes.TftpPacketACK()
#        ack.blocknumber = 1
#
#        # Server expects ACK at the beginning of transmission
#        self.assertTrue(
#            isinstance(serverstate.state, tftpy.TftpStates.TftpStateExpectACK)
#        )
#
#        # Receive first ACK for block 1, next block expected is 2
#        serverstate.state = serverstate.state.handle(ack, raddress, rport)
#        self.assertTrue(
#            isinstance(serverstate.state, tftpy.TftpStates.TftpStateExpectACK)
#        )
#        self.assertEqual(serverstate.state.context.next_block, 2)
#
#        # Receive duplicate ACK for block 1, next block expected is still 2
#        serverstate.state = serverstate.state.handle(ack, raddress, rport)
#        self.assertTrue(
#            isinstance(serverstate.state, tftpy.TftpStates.TftpStateExpectACK)
#        )
#        self.assertEqual(serverstate.state.context.next_block, 2)
#
#        # Receive duplicate ACK for block 1 after timeout for resending block 2
#        serverstate.state.context.metrics.last_dat_time -= 10  # Simulate 10 seconds time warp
#        self.assertRaises(
#            tftpy.TftpTimeoutExpectACK, serverstate.state.handle, ack, raddress, rport
#        )
#        self.assertTrue(
#            isinstance(serverstate.state, tftpy.TftpStates.TftpStateExpectACK)
#        )
#
#    def testServerNoOptionsSubdir(self):
#        raddress = "127.0.0.2"
#        rport = 10000
#        timeout = 5
#        root = os.path.dirname(os.path.abspath(__file__))
#        # Testing without the dyn_func_file set.
#        serverstate = tftpy.TftpContexts.TftpContextServer(
#            raddress, rport, timeout, root
#        )
#
#        self.assertTrue(isinstance(serverstate, tftpy.TftpContexts.TftpContextServer))
#
#        rrq = tftpy.TftpPacketTypes.TftpPacketRRQ()
#        rrq.filename = "640KBFILE"
#        rrq.mode = "octet"
#        rrq.options = {}
#
#        # Start the download.
#        serverstate.start(rrq.encode().buffer)
#        # At a 512 byte blocksize, this should be 1280 packets exactly.
#        for block in range(1, 1281):
#            # Should be in expectack state, or None
#            self.assertTrue(
#                isinstance(serverstate.state, tftpy.TftpStates.TftpStateExpectACK)
#            )
#            ack = tftpy.TftpPacketTypes.TftpPacketACK()
#            ack.blocknumber = block % 65536
#            serverstate.state = serverstate.state.handle(ack, raddress, rport)
#
#        # The last DAT packet should be empty, indicating a completed
#        # transfer.
#        ack = tftpy.TftpPacketTypes.TftpPacketACK()
#        ack.blocknumber = 1281 % 65536
#        finalstate = serverstate.state.handle(ack, raddress, rport)
#        self.assertTrue(finalstate is None)
#
#    def testServerInsecurePathAbsolute(self):
#        raddress = "127.0.0.2"
#        rport = 10000
#        timeout = 5
#        with self.dummyServerDir() as d:
#            root = os.path.join(os.path.abspath(d), "foo")
#            serverstate = tftpy.TftpContexts.TftpContextServer(
#                raddress, rport, timeout, root
#            )
#            rrq = tftpy.TftpPacketTypes.TftpPacketRRQ()
#            rrq.filename = os.path.join(os.path.abspath(d), "other/bar")
#            rrq.mode = "octet"
#            rrq.options = {}
#
#            # Start the download.
#            self.assertRaises(
#                tftpy.TftpException, serverstate.start, rrq.encode().buffer
#            )
#
#    def testServerInsecurePathRelative(self):
#        raddress = "127.0.0.2"
#        rport = 10000
#        timeout = 5
#        with self.dummyServerDir() as d:
#            root = os.path.join(os.path.abspath(d), "foo")
#            serverstate = tftpy.TftpContexts.TftpContextServer(
#                raddress, rport, timeout, root
#            )
#            rrq = tftpy.TftpPacketTypes.TftpPacketRRQ()
#            rrq.filename = "../other/bar"
#            rrq.mode = "octet"
#            rrq.options = {}
#
#            # Start the download.
#            self.assertRaises(
#                tftpy.TftpException, serverstate.start, rrq.encode().buffer
#            )
#
#    def testServerInsecurePathRootSibling(self):
#        raddress = "127.0.0.2"
#        rport = 10000
#        timeout = 5
#        with self.dummyServerDir() as d:
#            root = os.path.join(os.path.abspath(d), "foo")
#            serverstate = tftpy.TftpContexts.TftpContextServer(
#                raddress, rport, timeout, root
#            )
#            rrq = tftpy.TftpPacketTypes.TftpPacketRRQ()
#            rrq.filename = root + "-private/bar"
#            rrq.mode = "octet"
#            rrq.options = {}
#
#            # Start the download.
#            self.assertRaises(
#                tftpy.TftpException, serverstate.start, rrq.encode().buffer
#            )
#
#    def testServerSecurePathAbsolute(self):
#        raddress = "127.0.0.2"
#        rport = 10000
#        timeout = 5
#        with self.dummyServerDir() as d:
#            root = os.path.join(os.path.abspath(d), "foo")
#            serverstate = tftpy.TftpContexts.TftpContextServer(
#                raddress, rport, timeout, root
#            )
#            rrq = tftpy.TftpPacketTypes.TftpPacketRRQ()
#            rrq.filename = os.path.join(root, "bar")
#            rrq.mode = "octet"
#            rrq.options = {}
#
#            # Start the download.
#            serverstate.start(rrq.encode().buffer)
#            # Should be in expectack state.
#            self.assertTrue(
#                isinstance(serverstate.state, tftpy.TftpStates.TftpStateExpectACK)
#            )
#
#    def testServerSecurePathRelative(self):
#        raddress = "127.0.0.2"
#        rport = 10000
#        timeout = 5
#        with self.dummyServerDir() as d:
#            root = os.path.join(os.path.abspath(d), "foo")
#            serverstate = tftpy.TftpContexts.TftpContextServer(
#                raddress, rport, timeout, root
#            )
#            rrq = tftpy.TftpPacketTypes.TftpPacketRRQ()
#            rrq.filename = "bar"
#            rrq.mode = "octet"
#            rrq.options = {}
#
#            # Start the download.
#            serverstate.start(rrq.encode().buffer)
#            # Should be in expectack state.
#            self.assertTrue(
#                isinstance(serverstate.state, tftpy.TftpStates.TftpStateExpectACK)
#            )
#
#    def testServerDownloadWithStopNow(self, output="/tmp/out"):
#        log.debug("===> Running testcase testServerDownloadWithStopNow")
#        root = os.path.dirname(os.path.abspath(__file__))
#        server = tftpy.TftpServer(root)
#        client = tftpy.TftpClient("localhost", 20001, {})
#        # Fork a server and run the client in this process.
#        child_pid = os.fork()
#        if child_pid:
#            try:
#                # parent - let the server start
#                stopped_early = False
#                time.sleep(1)
#
#                def delay_hook(pkt):
#                    time.sleep(0.005)  # 5ms
#
#                client.download("640KBFILE", output, delay_hook)
#            except:
#                log.warning("client threw exception as expected")
#                stopped_early = True
#
#            finally:
#                os.kill(child_pid, 15)
#                os.waitpid(child_pid, 0)
#
#            self.assertTrue(stopped_early == True, "Server should not exit early")
#
#        else:
#            import signal
#
#            def handlealarm(signum, frame):
#                server.stop(now=True)
#
#            signal.signal(signal.SIGALRM, handlealarm)
#            signal.alarm(2)
#            try:
#                server.listen("localhost", 20001)
#                log.error("server didn't throw exception")
#            except Exception as err:
#                log.error("server got unexpected exception %s" % err)
#            # Wait until parent kills us
#            while True:
#                time.sleep(1)
#
#    def testServerDownloadWithStopNotNow(self, output="/tmp/out"):
#        log.debug("===> Running testcase testServerDownloadWithStopNotNow")
#        root = os.path.dirname(os.path.abspath(__file__))
#        server = tftpy.TftpServer(root)
#        client = tftpy.TftpClient("localhost", 20001, {})
#        # Fork a server and run the client in this process.
#        child_pid = os.fork()
#        if child_pid:
#            try:
#                stopped_early = True
#                # parent - let the server start
#                time.sleep(1)
#
#                def delay_hook(pkt):
#                    time.sleep(0.005)  # 5ms
#
#                client.download("640KBFILE", output, delay_hook)
#                stopped_early = False
#            except:
#                log.warning("client threw exception as expected")
#
#            finally:
#                os.kill(child_pid, 15)
#                os.waitpid(child_pid, 0)
#
#            self.assertTrue(stopped_early == False, "Server should not exit early")
#
#        else:
#            import signal
#
#            def handlealarm(signum, frame):
#                server.stop(now=False)
#
#            signal.signal(signal.SIGALRM, handlealarm)
#            signal.alarm(2)
#            try:
#                server.listen("localhost", 20001)
#            except Exception as err:
#                log.error("server threw exception %s" % err)
#            # Wait until parent kills us
#            while True:
#                time.sleep(1)
#
#    def testServerDownloadWithDynamicPort(self, output="/tmp/out"):
#        log.debug("===> Running testcase testServerDownloadWithDynamicPort")
#        root = os.path.dirname(os.path.abspath(__file__))
#
#        server = tftpy.TftpServer(root)
#        server_thread = threading.Thread(
#            target=server.listen, kwargs={"listenip": "localhost", "listenport": 0}
#        )
#        server_thread.start()
#
#        try:
#            server.is_running.wait()
#            client = tftpy.TftpClient("localhost", server.listenport, {})
#            time.sleep(1)
#            client.download("640KBFILE", output)
#        finally:
#            server.stop(now=False)
#            server_thread.join()
#
#class TestTftpyMisc(unittest.TestCase):
#    def testDirectoriesWithSpaces(self):
#        """Handle the evil directory names."""
#        root = "/tmp/bad dirname"
#        if not os.path.exists(root):
#            os.mkdir(root)
#        home = os.path.dirname(os.path.abspath(__file__))
#        filename = "640KBFILE"
#        input_path = os.path.join(home, filename)
#        print("input_path is", input_path)
#        server = tftpy.TftpServer(root)
#        client = tftpy.TftpClient("localhost", 20001)
#        # Fork a server and run the client in this process.
#        child_pid = os.fork()
#        if child_pid:
#            # parent - let the server start
#            try:
#                time.sleep(1)
#                client.upload("640KBFILE", input_path)
#            finally:
#                os.kill(child_pid, 15)
#                os.waitpid(child_pid, 0)
#
#        else:
#            server.listen("localhost", 20001)
#
#    def testStdin(self):
#        cdir = os.path.dirname(os.path.abspath(__file__))
#        script = os.path.join(cdir, "stdin.py")
#        command = f"cat tests/640KBFILE | {script}"
#        rv = subprocess.call(command, shell=True)
#        self.assertTrue( rv == 0 )
#
#    def testStdout(self):
#        cdir = os.path.dirname(os.path.abspath(__file__))
#        script = os.path.join(cdir, "stdout.py")
#        command = f"{script} > /tmp/out"
#        rv = subprocess.call(command, shell=True)
#        self.assertTrue( rv == 0 )

if __name__ == '__main__':
    # Important: On Windows, you need this for multiprocessing to work
    if os.name == 'nt':
        multiprocessing.set_start_method('spawn', force=True)
    
    # Run the tests
    unittest.main()
