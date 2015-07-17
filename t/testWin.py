"""Unit tests for tftpy."""

import unittest
import logging
import tftpy
import os
import time
import threading

log = tftpy.log


class TestTftpyState(unittest.TestCase):

    t_path = os.path.dirname(os.path.abspath(__file__))
    t_640KB = os.path.join(t_path, "640KBFILE")
    t_out = os.path.join(t_path, "out.tmp")

    def setUp(self):
        tftpy.setLogLevel(logging.DEBUG)

    def tearDown(self):
        if os.path.exists(self.t_out):
            os.remove(self.t_out)

    def _clientServerUploadOptions(self, options, upload_file=None):
        """Fire up a server and a client and do a upload."""
        input_path = self.t_640KB
        if not upload_file:
            upload_file = input_path

        server = tftpy.TftpServer(self.t_path)
        client = tftpy.TftpClient('localhost', 20001, options)
        server_thread = threading.Thread(group=None, target=server.listen,
                                         kwargs={'listenip': 'localhost',
                                                 'listenport': 20001,
                                                 'timeout': 10})
        server_thread.start()
        server.is_running.wait()
        try:
            time.sleep(1)
            client.upload("out.tmp", upload_file)
        finally:
            server.stop(now=False)
            server_thread.join()

    def _clientServerDownloadOptions(self, options, output='/tmp/out'):
        """Fire up a server and a client and do a download."""
        if isinstance(output, basestring) and not os.path.exists(output):
            output = self.t_out
        server = tftpy.TftpServer(self.t_path)
        client = tftpy.TftpClient('localhost', 20001, options)
        server_thread = threading.Thread(group=None, target=server.listen,
                                         kwargs={'listenip': 'localhost',
                                                 'listenport': 20001,
                                                 'timeout': 10})
        server_thread.start()
        server.is_running.wait()
        try:
            time.sleep(1)
            client.download('640KBFILE', output)
        finally:
            server.stop(now=False)
            server_thread.join()

    def testClientServerUploadNoOptions(self):
        self._clientServerUploadOptions({})

    def testClientServerUploadFileObj(self):
        with open(self.t_640KB, 'r') as f:
            self._clientServerUploadOptions({}, upload_file=f)

    def testClientServerUploadOptions(self):
        for blksize in [512, 1024, 2048, 4096]:
            self._clientServerUploadOptions({'blksize': blksize})

    def testClientServerNoOptions(self):
        self._clientServerDownloadOptions({})

    def testClientFileObject(self):
        with open(self.t_out, 'wb') as f:
            self._clientServerDownloadOptions({}, f)

    def testClientServerBlksize(self):
        for blksize in [512, 1024, 2048, 4096]:
            self._clientServerDownloadOptions({'blksize': blksize})

    def testClientServerNoOptionsDelay(self):
        tftpy.TftpStates.DELAY_BLOCK = 10
        self._clientServerDownloadOptions({})
        tftpy.TftpStates.DELAY_BLOCK = 0

    def testServerDownloadWithDynamicPort(self):
        server = tftpy.TftpServer(self.t_path)
        server_thread = threading.Thread(target=server.listen,
                                         kwargs={'listenip': 'localhost',
                                                 'listenport': 0})
        server_thread.start()
        server.is_running.wait()
        log.debug("> Tftp Server Listening at {}:{}".format(server.listenip,
                                                            server.listenport))
        client = tftpy.TftpClient('localhost', server.listenport, {})
        try:
            time.sleep(1)
            client.download('640KBFILE', self.t_out)
        finally:
            server.stop(now=False)
            server_thread.join()

if __name__ == '__main__':
    unittest.main()
