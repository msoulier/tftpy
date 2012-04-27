"""Unit tests for tftpy."""

import unittest
import logging
import tftpy
import os
import time
import tempfile
import shutil

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
        rrq.options = { 'blksize': '1024' }
        rrq.filename = 'myfilename'
        rrq.mode = 'octet'
        rrq.encode()
        self.assert_(rrq.buffer != None, "Buffer populated")
        rrq.decode()
        self.assertEqual(rrq.filename, "myfilename", "Filename correct")
        self.assertEqual(rrq.mode, "octet", "Mode correct")
        self.assertEqual(rrq.options['blksize'], '1024', "Blksize correct")

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
        wrq.options = { 'blksize': '1024' }
        wrq.filename = 'myfilename'
        wrq.mode = 'octet'
        wrq.encode()
        self.assert_(wrq.buffer != None, "Buffer populated")
        wrq.decode()
        self.assertEqual(wrq.opcode, 2, "Opcode correct")
        self.assertEqual(wrq.filename, "myfilename", "Filename correct")
        self.assertEqual(wrq.mode, "octet", "Mode correct")
        self.assertEqual(wrq.options['blksize'], '1024', "Blksize correct")


    def testTftpPacketDAT(self):
        log.debug("===> Running testcase testTftpPacketDAT")
        dat = tftpy.TftpPacketDAT()
        dat.blocknumber = 5
        data = "this is some data"
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
                         '2048',
                         "OACK blksize option is correct")
        # Test string to string
        oack.options = { 'blksize': '4096' }
        oack.encode()
        self.assert_(oack.buffer != None, "Buffer populated")
        oack.decode()
        self.assertEqual(oack.opcode, 6, "OACK opcode is correct")
        self.assertEqual(oack.options['blksize'],
                         '4096',
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

    def clientServerUploadOptions(self, options, transmitname=None):
        """Fire up a client and a server and do an upload."""
        root = '/tmp'
        home = os.path.dirname(os.path.abspath(__file__))
        filename = '100KBFILE'
        input_path = os.path.join(home, filename)
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
                              input_path)
            finally:
                os.kill(child_pid, 15)
                os.waitpid(child_pid, 0)

        else:
            server.listen('localhost', 20001)

    def clientServerDownloadOptions(self, options):
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
                client.download('100KBFILE',
                                '/tmp/out')
            finally:
                os.kill(child_pid, 15)
                os.waitpid(child_pid, 0)

        else:
            server.listen('localhost', 20001)

    def testClientServerNoOptions(self):
        self.clientServerDownloadOptions({})

    def testClientServerBlksize(self):
        for blksize in [512, 1024, 2048, 4096]:
            self.clientServerDownloadOptions({'blksize': blksize})

    def testClientServerUploadNoOptions(self):
        self.clientServerUploadOptions({})

    def testClientServerUploadWithSubdirs(self):
        self.clientServerUploadOptions({}, transmitname='foo/bar/100KBFILE')

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
        vfs = tftpy.TftpVfsCompat(os.path.dirname(os.path.abspath(__file__)))
        # Testing without the dyn_func_file set.
        serverstate = tftpy.TftpContextServer(raddress,
                                              rport,
                                              timeout,
                                              vfs)

        self.assertTrue( isinstance(serverstate,
                                    tftpy.TftpContextServer) )

        rrq = tftpy.TftpPacketRRQ()
        rrq.filename = '100KBFILE'
        rrq.mode = 'octet'
        rrq.options = {}

        # Start the download.
        serverstate.start(rrq.encode().buffer)
        # At a 512 byte blocksize, this should be 200 packets exactly.
        for block in range(1, 201):
            # Should be in expectack state.
            self.assertTrue( isinstance(serverstate.state,
                                        tftpy.TftpStateExpectACK) )
            ack = tftpy.TftpPacketACK()
            ack.blocknumber = block
            serverstate.state = serverstate.state.handle(ack, raddress, rport)

        # The last DAT packet should be empty, indicating a completed
        # transfer.
        ack = tftpy.TftpPacketACK()
        ack.blocknumber = 201
        finalstate = serverstate.state.handle(ack, raddress, rport)
        self.assertTrue( finalstate is None )

    def testServerNoOptionsSubdir(self):
        raddress = '127.0.0.2'
        rport = 10000
        timeout = 5
        vfs = tftpy.TftpVfsCompat(os.path.dirname(os.path.abspath(__file__)))
        # Testing without the dyn_func_file set.
        serverstate = tftpy.TftpContextServer(raddress,
                                              rport,
                                              timeout,
                                              vfs)

        self.assertTrue( isinstance(serverstate,
                                    tftpy.TftpContextServer) )

        rrq = tftpy.TftpPacketRRQ()
        rrq.filename = 'foo/100KBFILE'
        rrq.mode = 'octet'
        rrq.options = {}

        # Start the download.
        serverstate.start(rrq.encode().buffer)
        # At a 512 byte blocksize, this should be 200 packets exactly.
        for block in range(1, 201):
            # Should be in expectack state.
            self.assertTrue( isinstance(serverstate.state,
                                        tftpy.TftpStateExpectACK) )
            ack = tftpy.TftpPacketACK()
            ack.blocknumber = block
            serverstate.state = serverstate.state.handle(ack, raddress, rport)

        # The last DAT packet should be empty, indicating a completed
        # transfer.
        ack = tftpy.TftpPacketACK()
        ack.blocknumber = 201
        finalstate = serverstate.state.handle(ack, raddress, rport)
        self.assertTrue( finalstate is None )

    def testServerInsecurePath(self):
        raddress = '127.0.0.2'
        rport = 10000
        timeout = 5
        vfs = tftpy.TftpVfsCompat(os.path.dirname(os.path.abspath(__file__)))
        serverstate = tftpy.TftpContextServer(raddress,
                                              rport,
                                              timeout,
                                              vfs)
        rrq = tftpy.TftpPacketRRQ()
        rrq.filename = '../setup.py'
        rrq.mode = 'octet'
        rrq.options = {}

        # Start the download.
        self.assertRaisesRegexp(tftpy.TftpException, "bad file path",
                serverstate.start, rrq.encode().buffer)

    def testServerSecurePath(self):
        raddress = '127.0.0.2'
        rport = 10000
        timeout = 5
        vfs = tftpy.TftpVfsCompat(os.path.dirname(os.path.abspath(__file__)))
        serverstate = tftpy.TftpContextServer(raddress,
                                              rport,
                                              timeout,
                                              vfs)
        rrq = tftpy.TftpPacketRRQ()
        rrq.filename = '100KBFILE'
        rrq.mode = 'octet'
        rrq.options = {}

        # Start the download.
        serverstate.start(rrq.encode().buffer)
        # Should be in expectack state.
        self.assertTrue(isinstance(serverstate.state,
                                    tftpy.TftpStateExpectACK))

class TestTftpyVfsReadOnlyDynFileFunc(unittest.TestCase):
    def testRead(self):
        state = {'called':False}
        the_path = 'a path'
        def dyn_func(path):
            state['called'] = True
            return path
        vfs = tftpy.TftpVfsReadOnlyDynFileFunc(dyn_func)
        ret = vfs.open_read(the_path)
        self.assertEqual(the_path, ret)
        self.assert_(state['called'])

    def testWrite(self):
        state = {'called':False}
        the_path = 'a-path'
        def dyn_func(path):
            state['called'] = True
            return path
        vfs = tftpy.TftpVfsReadOnlyDynFileFunc(dyn_func)
        ret = vfs.open_write(the_path)
        self.assertEqual(None, ret)
        self.assert_(not state['called'])

class TestTftpyVfsNative(unittest.TestCase):
    def setUp(self):
        self.write_root = tempfile.mkdtemp()
    def tearDown(self):
        shutil.rmtree(self.write_root, ignore_errors=True)

    def testReadExisting(self):
        # Copy file to the temporary tftp root
        root = os.path.dirname(os.path.abspath(__file__))
        the_path = '100KBFILE'
        shutil.copy(os.path.join(root, the_path), self.write_root)

        vfs = tftpy.TftpVfsNative(self.write_root)
        fp = vfs.open_read(the_path)
        self.assert_(fp is not None)
        try:
            orig_fp = open(os.path.join(self.write_root, the_path), 'rb')
            try:
                self.assertEqual(orig_fp.read(), fp.read())
            finally:
                orig_fp.close()
        finally:
            fp.close()

    def testReadNonExistent(self):
        # The temporary tftp root is empty
        the_path = '100KBFILE'

        vfs = tftpy.TftpVfsNative(self.write_root)
        fp = vfs.open_read(the_path)
        self.assert_(fp is None)

    def testNonExistentRoot(self):
        non_existent_root = os.path.join(self.write_root, 'non-existent')
        self.assertRaisesRegexp(tftpy.TftpException, 'tftproot does not exist',
                tftpy.TftpVfsNative, non_existent_root)

    def testWriteSubdir(self):
        """Write a test string and read it back."""
        the_dir = 'a-path'
        the_fn = os.path.join(the_dir, 'a-file')
        data = 'test string'
        vfs = tftpy.TftpVfsNative(self.write_root)
        fp = vfs.open_write(the_fn)
        self.assert_(fp is not None)
        fp.write(data)
        fp.close()
        self.assert_(os.path.exists(os.path.join(self.write_root, the_dir)))
        self.assert_(os.path.isdir(os.path.join(self.write_root, the_dir)))
        self.assert_(os.path.exists(os.path.join(self.write_root, the_fn)))

    def testUnsafeRead(self):
        the_path = os.path.join(os.path.pardir, '100KBFILE')
        vfs = tftpy.TftpVfsNative(self.write_root)
        self.assertRaisesRegexp(tftpy.TftpException, "bad file path",
                vfs.open_read, the_path)

class TestTftpyVfsStack(unittest.TestCase):
    def setUp(self):
        self.vfs = tftpy.TftpVfsStack()

    def testReadEmpty(self):
        self.assert_(self.vfs.open_read('path') is None)

    def testWriteEmpty(self):
        self.assert_(self.vfs.open_write('path') is None)

    class MockVfsAccept(object):
        def __init__(self):
            self.read_fp = object()
            self.write_fp = object()
            self.path = None
        def open_read(self, path):
            self.path = path
            return self.read_fp
        def open_write(self, path):
            self.path = path
            return self.write_fp

    class MockVfsReject(object):
        def __init__(self):
            self.path = None
        def open_read(self, path):
            self.path = path
            return None
        def open_write(self, path):
            self.path = path
            return None

    def testReadRoot(self):
        fs1 = self.MockVfsAccept()
        self.vfs.mount(fs1, '/')
        ret = self.vfs.open_read('path')
        self.assert_(ret is fs1.read_fp)
        self.assertEqual('/path', fs1.path)

    def testWriteRoot(self):
        fs1 = self.MockVfsAccept()
        self.vfs.mount(fs1, '/')
        ret = self.vfs.open_write('path')
        self.assert_(ret is fs1.write_fp)
        self.assertEqual('/path', fs1.path)

    def testFirstRoot(self):
        """Return first valid match"""
        fs1 = self.MockVfsReject()
        fs2 = self.MockVfsAccept()
        fs3 = self.MockVfsAccept()
        self.vfs.mount(fs1, '/')
        self.vfs.mount(fs2, '/')
        self.vfs.mount(fs3, '/')
        ret = self.vfs.open_read('path')
        self.assert_(ret is fs2.read_fp)
        self.assert_(ret is not fs3.read_fp)
        self.assertEqual('/path', fs1.path)
        self.assertEqual('/path', fs2.path)
        self.assertEqual(None, fs3.path)

    def testIterateSubPaths(self):
        """Visit all providers that have a matching base path."""
        fs1 = self.MockVfsReject()
        fs2 = self.MockVfsReject()
        fs3 = self.MockVfsReject()
        self.vfs.mount(fs1, '/base')
        self.vfs.mount(fs2, '/base/somewhere')
        self.vfs.mount(fs3, '/not-relevant')
        ret = self.vfs.open_read('/base/somewhere/path')
        self.assert_(ret is None)
        self.assertEqual('/somewhere/path', fs1.path)
        self.assertEqual('/path', fs2.path)
        self.assertEqual(None, fs3.path)

if __name__ == '__main__':
    unittest.main()
