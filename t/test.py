"""Unit tests for tftpy."""

import unittest
import logging
import tftpy
import os
import time
import sys

log = tftpy.log

class TestTftpyClasses(unittest.TestCase):

    def setUp(self):
        tftpy.setLogLevel(logging.DEBUG)

    def testTftpPacketRRQ(self):
        log.debug("===> Running testcase testTftpPacketRRQ")
        options = {}
        rrq = tftpy.TftpPacketRRQ()
        rrq.filename = 'myfilename'
        rrq.mode = 'octet'
        rrq.options = options
        rrq.encode()
        self.assert_(rrq.buffer != None, "Buffer populated")
        rrq.decode()
        self.assertEqual(rrq.filename, "myfilename", "Filename correct")
        self.assertEqual(rrq.mode, "octet", "Mode correct")
        self.assertEqual(rrq.options, options, "Options correct")
        # repeat test with options
        rrq.options = { 'blksize': 1024 }
        rrq.filename = 'myfilename'
        rrq.mode = 'octet'
        rrq.encode()
        self.assert_(rrq.buffer != None, "Buffer populated")
        rrq.decode()
        self.assertEqual(rrq.filename, "myfilename", "Filename correct")
        self.assertEqual(rrq.mode, "octet", "Mode correct")
        self.assertEqual(rrq.options['blksize'], 1024, "Blksize correct")

    def testTftpPacketWRQ(self):
        log.debug("===> Running test case testTftpPacketWRQ")
        options = {}
        wrq = tftpy.TftpPacketWRQ()
        wrq.filename = 'myfilename'
        wrq.mode = 'octet'
        wrq.options = options
        wrq.encode()
        self.assert_(wrq.buffer != None, "Buffer populated")
        wrq.decode()
        self.assertEqual(wrq.opcode, 2, "Opcode correct")
        self.assertEqual(wrq.filename, "myfilename", "Filename correct")
        self.assertEqual(wrq.mode, "octet", "Mode correct")
        self.assertEqual(wrq.options, options, "Options correct")
        # repeat test with options
        wrq.options = { 'blksize': 1024 }
        wrq.filename = 'myfilename'
        wrq.mode = 'octet'
        wrq.encode()
        self.assert_(wrq.buffer != None, "Buffer populated")
        wrq.decode()
        self.assertEqual(wrq.opcode, 2, "Opcode correct")
        self.assertEqual(wrq.filename, "myfilename", "Filename correct")
        self.assertEqual(wrq.mode, "octet", "Mode correct")
        self.assertEqual(wrq.options['blksize'], 1024, "Blksize correct")


    def testTftpPacketDAT(self):
        log.debug("===> Running testcase testTftpPacketDAT")
        dat = tftpy.TftpPacketDAT()
        dat.blocknumber = 5
        if sys.version < '3':
            data = "this is some data"
        else:
            data = b"this is some data"
        dat.data = data
        dat.encode()
        self.assert_(dat.buffer != None, "Buffer populated")
        dat.decode()
        self.assertEqual(dat.opcode, 3, "DAT opcode is correct")
        self.assertEqual(dat.blocknumber, 5, "Block number is correct")
        self.assertEqual(dat.data, data, "DAT data is correct")

    def testTftpPacketACK(self):
        log.debug("===> Running testcase testTftpPacketACK")
        ack = tftpy.TftpPacketACK()
        ack.blocknumber = 6
        ack.encode()
        self.assert_(ack.buffer != None, "Buffer populated")
        ack.decode()
        self.assertEqual(ack.opcode, 4, "ACK opcode is correct")
        self.assertEqual(ack.blocknumber, 6, "ACK blocknumber correct")

    def testTftpPacketERR(self):
        log.debug("===> Running testcase testTftpPacketERR")
        err = tftpy.TftpPacketERR()
        err.errorcode = 4
        err.encode()
        self.assert_(err.buffer != None, "Buffer populated")
        err.decode()
        self.assertEqual(err.opcode, 5, "ERR opcode is correct")
        self.assertEqual(err.errorcode, 4, "ERR errorcode is correct")

    def testTftpPacketOACK(self):
        log.debug("===> Running testcase testTftpPacketOACK")
        oack = tftpy.TftpPacketOACK()
        # Test that if we make blksize a number, it comes back a string.
        oack.options = { 'blksize': 2048 }
        oack.encode()
        self.assert_(oack.buffer != None, "Buffer populated")
        oack.decode()
        self.assertEqual(oack.opcode, 6, "OACK opcode is correct")
        self.assertEqual(oack.options['blksize'],
                         2048,
                         "OACK blksize option is correct")
        # Test string to string
        oack.options = { 'blksize': 4096 }
        oack.encode()
        self.assert_(oack.buffer != None, "Buffer populated")
        oack.decode()
        self.assertEqual(oack.opcode, 6, "OACK opcode is correct")
        self.assertEqual(oack.options['blksize'],
                         4096,
                         "OACK blksize option is correct")
        
    def testTftpPacketFactory(self):
        log.debug("===> Running testcase testTftpPacketFactory")
        # Make sure that the correct class is created for the correct opcode.
        classes = {
            1: tftpy.TftpPacketRRQ,
            2: tftpy.TftpPacketWRQ,
            3: tftpy.TftpPacketDAT,
            4: tftpy.TftpPacketACK,
            5: tftpy.TftpPacketERR,
            6: tftpy.TftpPacketOACK
            }
        factory = tftpy.TftpPacketFactory()
        for opcode in classes:
            self.assert_(isinstance(factory._TftpPacketFactory__create(opcode),
                                    classes[opcode]),
                                    "opcode %d returns the correct class" % opcode)

class TestTftpyState(unittest.TestCase):

    def setUp(self):
        tftpy.setLogLevel(logging.DEBUG)

    def clientServerUploadOptions(self, options, input=None, transmitname=None):
        """Fire up a client and a server and do an upload."""
        root = '/tmp'
        home = os.path.dirname(os.path.abspath(__file__))
        filename = '640KBFILE'
        input_path = os.path.join(home, filename)
        if not input:
            input = input_path
        if transmitname:
            filename = transmitname
        server = tftpy.TftpServer(root)
        client = tftpy.TftpClient('localhost',
                                  20001,
                                  options)
        # Fork a server and run the client in this process.
        child_pid = os.fork()
        if child_pid:
            # parent - let the server start
            try:
                time.sleep(1)
                client.upload(filename,
                              input)
            finally:
                os.kill(child_pid, 15)
                os.waitpid(child_pid, 0)

        else:
            server.listen('localhost', 20001)

    def clientServerDownloadOptions(self, options, output='/tmp/out'):
        """Fire up a client and a server and do a download."""
        root = os.path.dirname(os.path.abspath(__file__))
        server = tftpy.TftpServer(root)
        client = tftpy.TftpClient('localhost',
                                  20001,
                                  options)
        # Fork a server and run the client in this process.
        child_pid = os.fork()
        if child_pid:
            # parent - let the server start
            try:
                time.sleep(1)
                client.download('640KBFILE',
                                output)
            finally:
                os.kill(child_pid, 15)
                os.waitpid(child_pid, 0)

        else:
            server.listen('localhost', 20001)

    def testClientServerNoOptions(self):
        self.clientServerDownloadOptions({})

    def testClientFileObject(self):
        if sys.version < '3':
            output = open('/tmp/out', 'w')
        else:
            output = open('/tmp/out', 'wb')
        self.clientServerDownloadOptions({}, output)

    def testClientServerBlksize(self):
        for blksize in [512, 1024, 2048, 4096]:
            self.clientServerDownloadOptions({'blksize': blksize})

    def testClientServerUploadNoOptions(self):
        self.clientServerUploadOptions({})

    def testClientServerUploadFileObj(self):
        if sys.version < '3':
            fileobj = open('t/640KBFILE', 'r')
        else:
            fileobj = open('t/640KBFILE', 'rb')
        self.clientServerUploadOptions({}, input=fileobj)

    def testClientServerUploadWithSubdirs(self):
        self.clientServerUploadOptions({}, transmitname='foo/bar/640KBFILE')

    def testClientServerUploadStartingSlash(self):
        self.clientServerUploadOptions({}, transmitname='/foo/bar/640KBFILE')

    def testClientServerUploadOptions(self):
        for blksize in [512, 1024, 2048, 4096]:
            self.clientServerUploadOptions({'blksize': blksize})

    def testClientServerNoOptionsDelay(self):
        tftpy.TftpStates.DELAY_BLOCK = 10
        self.clientServerDownloadOptions({})
        tftpy.TftpStates.DELAY_BLOCK = 0

    def testServerNoOptions(self):
        raddress = '127.0.0.2'
        rport = 10000
        timeout = 5
        root = os.path.dirname(os.path.abspath(__file__))
        # Testing without the dyn_func_file set.
        serverstate = tftpy.TftpContextServer(raddress,
                                              rport,
                                              timeout,
                                              root)

        self.assertTrue( isinstance(serverstate,
                                    tftpy.TftpContextServer) )

        rrq = tftpy.TftpPacketRRQ()
        rrq.filename = '640KBFILE'
        rrq.mode = 'octet'
        rrq.options = {}

        # Start the download.
        serverstate.start(rrq.encode().buffer)
        # At a 512 byte blocksize, this should be 1280 packets exactly.
        for block in range(1, 1281):
            # Should be in expectack state.
            self.assertTrue( isinstance(serverstate.state,
                                        tftpy.TftpStateExpectACK) )
            ack = tftpy.TftpPacketACK()
            ack.blocknumber = block % 65536
            serverstate.state = serverstate.state.handle(ack, raddress, rport)

        # The last DAT packet should be empty, indicating a completed
        # transfer.
        ack = tftpy.TftpPacketACK()
        ack.blocknumber = 1281 % 65536
        finalstate = serverstate.state.handle(ack, raddress, rport)
        self.assertTrue( finalstate is None )

    def testServerNoOptionsSubdir(self):
        raddress = '127.0.0.2'
        rport = 10000
        timeout = 5
        root = os.path.dirname(os.path.abspath(__file__))
        # Testing without the dyn_func_file set.
        serverstate = tftpy.TftpContextServer(raddress,
                                              rport,
                                              timeout,
                                              root)

        self.assertTrue( isinstance(serverstate,
                                    tftpy.TftpContextServer) )

        rrq = tftpy.TftpPacketRRQ()
        rrq.filename = '640KBFILE'
        rrq.mode = 'octet'
        rrq.options = {}

        # Start the download.
        serverstate.start(rrq.encode().buffer)
        # At a 512 byte blocksize, this should be 1280 packets exactly.
        for block in range(1, 1281):
            # Should be in expectack state, or None
            self.assertTrue( isinstance(serverstate.state,
                                        tftpy.TftpStateExpectACK) )
            ack = tftpy.TftpPacketACK()
            ack.blocknumber = block % 65536
            serverstate.state = serverstate.state.handle(ack, raddress, rport)

        # The last DAT packet should be empty, indicating a completed
        # transfer.
        ack = tftpy.TftpPacketACK()
        ack.blocknumber = 1281 % 65536
        finalstate = serverstate.state.handle(ack, raddress, rport)
        self.assertTrue( finalstate is None )

    def testServerInsecurePath(self):
        raddress = '127.0.0.2'
        rport = 10000
        timeout = 5
        root = os.path.dirname(os.path.abspath(__file__))
        serverstate = tftpy.TftpContextServer(raddress,
                                              rport,
                                              timeout,
                                              root)
        rrq = tftpy.TftpPacketRRQ()
        rrq.filename = '../setup.py'
        rrq.mode = 'octet'
        rrq.options = {}

        # Start the download.
        self.assertRaises(tftpy.TftpException,
                serverstate.start, rrq.encode().buffer)

    def testServerSecurePath(self):
        raddress = '127.0.0.2'
        rport = 10000
        timeout = 5
        root = os.path.dirname(os.path.abspath(__file__))
        serverstate = tftpy.TftpContextServer(raddress,
                                              rport,
                                              timeout,
                                              root)
        rrq = tftpy.TftpPacketRRQ()
        rrq.filename = '640KBFILE'
        rrq.mode = 'octet'
        rrq.options = {}

        # Start the download.
        serverstate.start(rrq.encode().buffer)
        # Should be in expectack state.
        self.assertTrue(isinstance(serverstate.state,
                                    tftpy.TftpStateExpectACK))

    def testServerDownloadWithStopNow(self, output='/tmp/out'):
        log.debug("===> Running testcase testServerDownloadWithStopNow")
        root = os.path.dirname(os.path.abspath(__file__))
        server = tftpy.TftpServer(root)
        client = tftpy.TftpClient('localhost',
                                  20001,
                                  {})
        # Fork a server and run the client in this process.
        child_pid = os.fork()
        if child_pid:
            # parent - let the server start
            stopped_early = False
            try:
                time.sleep(1)
                client.download('640KBFILE',
                                output)
            except:
                log.warn("client threw exception as expected")
                stopped_early = True

            finally:
                os.kill(child_pid, 15)
                os.waitpid(child_pid, 0)

            self.assertTrue( stopped_early == True )

        else:
            import signal
            def handlealarm(signum, frame):
                server.stop(now=True)
            signal.signal(signal.SIGALRM, handlealarm)
            signal.alarm(2)
            try:
                server.listen('localhost', 20001)
            except Exception as err:
                self.assertTrue( err[0] == 4 )

    def testServerDownloadWithStopNotNow(self, output='/tmp/out'):
        log.debug("===> Running testcase testServerDownloadWithStopNotNow")
        root = os.path.dirname(os.path.abspath(__file__))
        server = tftpy.TftpServer(root)
        client = tftpy.TftpClient('localhost',
                                  20001,
                                  {})
        # Fork a server and run the client in this process.
        child_pid = os.fork()
        if child_pid:
            # parent - let the server start
            stopped_early = False
            try:
                time.sleep(1)
                client.download('640KBFILE',
                                output)
            except:
                log.warn("client threw exception as expected")
                stopped_early = True

            finally:
                os.kill(child_pid, 15)
                os.waitpid(child_pid, 0)

            self.assertTrue( stopped_early == False )

        else:
            import signal
            def handlealarm(signum, frame):
                server.stop(now=False)
            signal.signal(signal.SIGALRM, handlealarm)
            signal.alarm(2)
            try:
                server.listen('localhost', 20001)
            except Exception:
                self.assertTrue( False, "Server should not exit early" )

if __name__ == '__main__':
    unittest.main()
