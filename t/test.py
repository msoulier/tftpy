"""Unit tests for tftpy."""
# vim: ts=4 sw=4 et ai:
# -*- coding: utf8 -*-

import logging
import os
import threading
import time
import unittest
from contextlib import contextmanager
from errno import EINTR
from multiprocessing import Queue
from shutil import rmtree
from tempfile import mkdtemp

import tftpy

log = logging.getLogger("tftpy")
log.setLevel(logging.DEBUG)

# console handler
handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(levelname)s [%(name)s:%(lineno)s] %(message)s")
handler.setFormatter(formatter)
log.addHandler(handler)


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


class TestTftpyState(unittest.TestCase):
    def clientServerUploadOptions(
        self, options, input=None, transmitname=None, server_kwargs=None
    ):
        """Fire up a client and a server and do an upload."""
        root = "/tmp"
        home = os.path.dirname(os.path.abspath(__file__))
        filename = "640KBFILE"
        input_path = os.path.join(home, filename)
        if not input:
            input = input_path
        if transmitname:
            filename = transmitname
        server_kwargs = server_kwargs or {}
        server = tftpy.TftpServer(root, **server_kwargs)
        client = tftpy.TftpClient("localhost", 20001, options)
        # Fork a server and run the client in this process.
        child_pid = os.fork()
        if child_pid:
            # parent - let the server start
            try:
                time.sleep(1)
                client.upload(filename, input)
            finally:
                os.kill(child_pid, 15)
                os.waitpid(child_pid, 0)

        else:
            server.listen("localhost", 20001)

    def clientServerDownloadOptions(
        self,
        options,
        output="/tmp/out",
        cretries=tftpy.DEF_TIMEOUT_RETRIES,
        sretries=tftpy.DEF_TIMEOUT_RETRIES,
    ):
        """Fire up a client and a server and do a download."""
        root = os.path.dirname(os.path.abspath(__file__))
        server = tftpy.TftpServer(root)
        client = tftpy.TftpClient("localhost", 20001, options)
        # Fork a server and run the client in this process.
        child_pid = os.fork()
        if child_pid:
            # parent - let the server start
            try:
                time.sleep(1)
                client.download("640KBFILE", output, retries=cretries)
            finally:
                os.kill(child_pid, 15)
                os.waitpid(child_pid, 0)

        else:
            server.listen("localhost", 20001, retries=sretries)

    @contextmanager
    def dummyServerDir(self):
        tmpdir = mkdtemp()
        for dirname in ("foo", "foo-private", "other", "with spaces"):
            os.mkdir(os.path.join(tmpdir, dirname))
            with open(os.path.join(tmpdir, dirname, "bar"), "w") as w:
                w.write("baz")

        try:
            yield tmpdir
        finally:
            rmtree(tmpdir)

    def testClientServerNoOptions(self):
        self.clientServerDownloadOptions({})

    def testClientServerNoOptionsRetries(self):
        self.clientServerDownloadOptions({}, cretries=5, sretries=5)

    def testClientServerTsizeOptions(self):
        self.clientServerDownloadOptions({"tsize": 64 * 1024})

    def testClientFileObject(self):
        output = open("/tmp/out", "wb")
        self.clientServerDownloadOptions({}, output)

    def testClientServerBlksize(self):
        for blksize in [512, 1024, 2048, 4096]:
            self.clientServerDownloadOptions({"blksize": blksize})

    def testClientServerUploadNoOptions(self):
        self.clientServerUploadOptions({})

    def testClientServerUploadFileObj(self):
        fileobj = open("t/640KBFILE", "rb")
        self.clientServerUploadOptions({}, input=fileobj)

    def testClientServerUploadWithSubdirs(self):
        self.clientServerUploadOptions({}, transmitname="foo/bar/640KBFILE")

    def testClientServerUploadStartingSlash(self):
        self.clientServerUploadOptions({}, transmitname="/foo/bar/640KBFILE")

    def testClientServerUploadOptions(self):
        for blksize in [512, 1024, 2048, 4096]:
            self.clientServerUploadOptions({"blksize": blksize})

    def customUploadHelper(self, return_func):
        q = Queue()

        def upload_open(path, context):
            q.put("called")
            return return_func(path)

        self.clientServerUploadOptions({}, server_kwargs={"upload_open": upload_open})
        self.assertEqual(q.get(True, 1), "called")

    def testClientServerUploadCustomOpen(self):
        self.customUploadHelper(lambda p: open(p, "wb"))

    def testClientServerUploadCustomOpenForbids(self):
        with self.assertRaisesRegex(tftpy.TftpException, "Access violation"):
            self.customUploadHelper(lambda p: None)

    def testClientServerUploadTsize(self):
        self.clientServerUploadOptions(
            {"tsize": 64 * 1024}, transmitname="/foo/bar/640KBFILE"
        )

    def testClientServerNoOptionsDelay(self):
        tftpy.TftpStates.DELAY_BLOCK = 10
        self.clientServerDownloadOptions({})
        tftpy.TftpStates.DELAY_BLOCK = 0

    def testServerNoOptions(self):
        raddress = "127.0.0.2"
        rport = 10000
        timeout = 5
        root = os.path.dirname(os.path.abspath(__file__))
        # Testing without the dyn_func_file set.
        serverstate = tftpy.TftpContexts.TftpContextServer(
            raddress, rport, timeout, root
        )

        self.assertTrue(isinstance(serverstate, tftpy.TftpContexts.TftpContextServer))

        rrq = tftpy.TftpPacketTypes.TftpPacketRRQ()
        rrq.filename = "640KBFILE"
        rrq.mode = "octet"
        rrq.options = {}

        # Start the download.
        serverstate.start(rrq.encode().buffer)
        # At a 512 byte blocksize, this should be 1280 packets exactly.
        for block in range(1, 1281):
            # Should be in expectack state.
            self.assertTrue(
                isinstance(serverstate.state, tftpy.TftpStates.TftpStateExpectACK)
            )
            ack = tftpy.TftpPacketTypes.TftpPacketACK()
            ack.blocknumber = block % 65536
            serverstate.state = serverstate.state.handle(ack, raddress, rport)

        # The last DAT packet should be empty, indicating a completed
        # transfer.
        ack = tftpy.TftpPacketTypes.TftpPacketACK()
        ack.blocknumber = 1281 % 65536
        finalstate = serverstate.state.handle(ack, raddress, rport)
        self.assertTrue(finalstate is None)

    def testServerTimeoutExpectACK(self):
        raddress = "127.0.0.2"
        rport = 10000
        timeout = 5
        root = os.path.dirname(os.path.abspath(__file__))
        # Testing without the dyn_func_file set.
        serverstate = tftpy.TftpContexts.TftpContextServer(
            raddress, rport, timeout, root
        )

        self.assertTrue(isinstance(serverstate, tftpy.TftpContexts.TftpContextServer))

        rrq = tftpy.TftpPacketTypes.TftpPacketRRQ()
        rrq.filename = "640KBFILE"
        rrq.mode = "octet"
        rrq.options = {}

        # Start the download.
        serverstate.start(rrq.encode().buffer)

        ack = tftpy.TftpPacketTypes.TftpPacketACK()
        ack.blocknumber = 1

        # Server expects ACK at the beginning of transmission
        self.assertTrue(
            isinstance(serverstate.state, tftpy.TftpStates.TftpStateExpectACK)
        )

        # Receive first ACK for block 1, next block expected is 2
        serverstate.state = serverstate.state.handle(ack, raddress, rport)
        self.assertTrue(
            isinstance(serverstate.state, tftpy.TftpStates.TftpStateExpectACK)
        )
        self.assertEqual(serverstate.state.context.next_block, 2)

        # Receive duplicate ACK for block 1, next block expected is still 2
        serverstate.state = serverstate.state.handle(ack, raddress, rport)
        self.assertTrue(
            isinstance(serverstate.state, tftpy.TftpStates.TftpStateExpectACK)
        )
        self.assertEqual(serverstate.state.context.next_block, 2)

        # Receive duplicate ACK for block 1 after timeout for resending block 2
        serverstate.state.context.metrics.last_dat_time -= 10  # Simulate 10 seconds time warp
        self.assertRaises(
            tftpy.TftpTimeoutExpectACK, serverstate.state.handle, ack, raddress, rport
        )
        self.assertTrue(
            isinstance(serverstate.state, tftpy.TftpStates.TftpStateExpectACK)
        )

    def testServerNoOptionsSubdir(self):
        raddress = "127.0.0.2"
        rport = 10000
        timeout = 5
        root = os.path.dirname(os.path.abspath(__file__))
        # Testing without the dyn_func_file set.
        serverstate = tftpy.TftpContexts.TftpContextServer(
            raddress, rport, timeout, root
        )

        self.assertTrue(isinstance(serverstate, tftpy.TftpContexts.TftpContextServer))

        rrq = tftpy.TftpPacketTypes.TftpPacketRRQ()
        rrq.filename = "640KBFILE"
        rrq.mode = "octet"
        rrq.options = {}

        # Start the download.
        serverstate.start(rrq.encode().buffer)
        # At a 512 byte blocksize, this should be 1280 packets exactly.
        for block in range(1, 1281):
            # Should be in expectack state, or None
            self.assertTrue(
                isinstance(serverstate.state, tftpy.TftpStates.TftpStateExpectACK)
            )
            ack = tftpy.TftpPacketTypes.TftpPacketACK()
            ack.blocknumber = block % 65536
            serverstate.state = serverstate.state.handle(ack, raddress, rport)

        # The last DAT packet should be empty, indicating a completed
        # transfer.
        ack = tftpy.TftpPacketTypes.TftpPacketACK()
        ack.blocknumber = 1281 % 65536
        finalstate = serverstate.state.handle(ack, raddress, rport)
        self.assertTrue(finalstate is None)

    def testServerInsecurePathAbsolute(self):
        raddress = "127.0.0.2"
        rport = 10000
        timeout = 5
        with self.dummyServerDir() as d:
            root = os.path.join(os.path.abspath(d), "foo")
            serverstate = tftpy.TftpContexts.TftpContextServer(
                raddress, rport, timeout, root
            )
            rrq = tftpy.TftpPacketTypes.TftpPacketRRQ()
            rrq.filename = os.path.join(os.path.abspath(d), "other/bar")
            rrq.mode = "octet"
            rrq.options = {}

            # Start the download.
            self.assertRaises(
                tftpy.TftpException, serverstate.start, rrq.encode().buffer
            )

    def testServerInsecurePathRelative(self):
        raddress = "127.0.0.2"
        rport = 10000
        timeout = 5
        with self.dummyServerDir() as d:
            root = os.path.join(os.path.abspath(d), "foo")
            serverstate = tftpy.TftpContexts.TftpContextServer(
                raddress, rport, timeout, root
            )
            rrq = tftpy.TftpPacketTypes.TftpPacketRRQ()
            rrq.filename = "../other/bar"
            rrq.mode = "octet"
            rrq.options = {}

            # Start the download.
            with self.assertRaisesRegex(tftpy.TftpException, 'bad file path'):
                serverstate.start(rrq.encode().buffer)

    def testServerInsecurePathRootSibling(self):
        raddress = "127.0.0.2"
        rport = 10000
        timeout = 5
        with self.dummyServerDir() as d:
            root = os.path.join(os.path.abspath(d), "foo")
            serverstate = tftpy.TftpContexts.TftpContextServer(
                raddress, rport, timeout, root
            )
            rrq = tftpy.TftpPacketTypes.TftpPacketRRQ()
            rrq.filename = root + "-private/bar"
            rrq.mode = "octet"
            rrq.options = {}

            # Start the download.
            with self.assertRaisesRegex(tftpy.TftpException, 'bad file path'):
                serverstate.start(rrq.encode().buffer)

    def testServerSecurePathAbsolute(self):
        raddress = "127.0.0.2"
        rport = 10000
        timeout = 5
        with self.dummyServerDir() as d:
            root = os.path.join(os.path.abspath(d), "foo")
            serverstate = tftpy.TftpContexts.TftpContextServer(
                raddress, rport, timeout, root
            )
            rrq = tftpy.TftpPacketTypes.TftpPacketRRQ()
            rrq.filename = os.path.join(root, "bar")
            rrq.mode = "octet"
            rrq.options = {}

            # Start the download.
            serverstate.start(rrq.encode().buffer)
            # Should be in expectack state.
            self.assertTrue(
                isinstance(serverstate.state, tftpy.TftpStates.TftpStateExpectACK)
            )

    def testServerSecurePathRelative(self):
        raddress = "127.0.0.2"
        rport = 10000
        timeout = 5
        with self.dummyServerDir() as d:
            root = os.path.join(os.path.abspath(d), "foo")
            serverstate = tftpy.TftpContexts.TftpContextServer(
                raddress, rport, timeout, root
            )
            rrq = tftpy.TftpPacketTypes.TftpPacketRRQ()
            rrq.filename = "bar"
            rrq.mode = "octet"
            rrq.options = {}

            # Start the download.
            serverstate.start(rrq.encode().buffer)
            # Should be in expectack state.
            self.assertTrue(
                isinstance(serverstate.state, tftpy.TftpStates.TftpStateExpectACK)
            )

    def testServerPathRoot(self):
        raddress = "127.0.0.2"
        rport = 10000
        timeout = 5
        with self.dummyServerDir() as d:
            root = '/'
            serverstate = tftpy.TftpContexts.TftpContextServer(
                raddress, rport, timeout, root
            )
            rrq = tftpy.TftpPacketTypes.TftpPacketRRQ()
            rrq.filename = os.path.join(os.path.abspath(d), "foo", "bar")
            rrq.mode = "octet"
            rrq.options = {}

            # Start the download.
            serverstate.start(rrq.encode().buffer)
            # Should be in expectack state.
            self.assertTrue(
                isinstance(serverstate.state, tftpy.TftpStates.TftpStateExpectACK)
            )

    def testServerDownloadWithStopNow(self, output="/tmp/out"):
        log.debug("===> Running testcase testServerDownloadWithStopNow")
        root = os.path.dirname(os.path.abspath(__file__))
        server = tftpy.TftpServer(root)
        client = tftpy.TftpClient("localhost", 20001, {})
        # Fork a server and run the client in this process.
        child_pid = os.fork()
        if child_pid:
            try:
                # parent - let the server start
                stopped_early = False
                time.sleep(1)

                def delay_hook(pkt):
                    time.sleep(0.005)  # 5ms

                client.download("640KBFILE", output, delay_hook)
            except:
                log.warning("client threw exception as expected")
                stopped_early = True

            finally:
                os.kill(child_pid, 15)
                os.waitpid(child_pid, 0)

            self.assertTrue(stopped_early == True, "Server should not exit early")

        else:
            import signal

            def handlealarm(signum, frame):
                server.stop(now=True)

            signal.signal(signal.SIGALRM, handlealarm)
            signal.alarm(2)
            try:
                server.listen("localhost", 20001)
                log.error("server didn't throw exception")
            except Exception as err:
                log.error("server got unexpected exception %s" % err)
            # Wait until parent kills us
            while True:
                time.sleep(1)

    def testServerDownloadWithStopNotNow(self, output="/tmp/out"):
        log.debug("===> Running testcase testServerDownloadWithStopNotNow")
        root = os.path.dirname(os.path.abspath(__file__))
        server = tftpy.TftpServer(root)
        client = tftpy.TftpClient("localhost", 20001, {})
        # Fork a server and run the client in this process.
        child_pid = os.fork()
        if child_pid:
            try:
                stopped_early = True
                # parent - let the server start
                time.sleep(1)

                def delay_hook(pkt):
                    time.sleep(0.005)  # 5ms

                client.download("640KBFILE", output, delay_hook)
                stopped_early = False
            except:
                log.warning("client threw exception as expected")

            finally:
                os.kill(child_pid, 15)
                os.waitpid(child_pid, 0)

            self.assertTrue(stopped_early == False, "Server should not exit early")

        else:
            import signal

            def handlealarm(signum, frame):
                server.stop(now=False)

            signal.signal(signal.SIGALRM, handlealarm)
            signal.alarm(2)
            try:
                server.listen("localhost", 20001)
            except Exception as err:
                log.error("server threw exception %s" % err)
            # Wait until parent kills us
            while True:
                time.sleep(1)

    def testServerDownloadWithDynamicPort(self, output="/tmp/out"):
        log.debug("===> Running testcase testServerDownloadWithDynamicPort")
        root = os.path.dirname(os.path.abspath(__file__))

        server = tftpy.TftpServer(root)
        server_thread = threading.Thread(
            target=server.listen, kwargs={"listenip": "localhost", "listenport": 0}
        )
        server_thread.start()

        try:
            server.is_running.wait()
            client = tftpy.TftpClient("localhost", server.listenport, {})
            time.sleep(1)
            client.download("640KBFILE", output)
        finally:
            server.stop(now=False)
            server_thread.join()

class TestTftpyMisc(unittest.TestCase):
    def testDirectoriesWithSpaces(self):
        """Handle the evil directory names."""
        root = "/tmp/bad dirname"
        if not os.path.exists(root):
            os.mkdir(root)
        home = os.path.dirname(os.path.abspath(__file__))
        filename = "640KBFILE"
        input_path = os.path.join(home, filename)
        print("input_path is", input_path)
        server = tftpy.TftpServer(root)
        client = tftpy.TftpClient("localhost", 20001)
        # Fork a server and run the client in this process.
        child_pid = os.fork()
        if child_pid:
            # parent - let the server start
            try:
                time.sleep(1)
                client.upload("640KBFILE", input_path)
            finally:
                os.kill(child_pid, 15)
                os.waitpid(child_pid, 0)

        else:
            server.listen("localhost", 20001)

if __name__ == "__main__":
    unittest.main()
