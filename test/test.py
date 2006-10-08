"""Unit tests for tftpy."""

import unittest
import tftpy

class TestTftpy(unittest.TestCase):

    def setUp(self):
        pass

    def testTftpPacketRRQ(self):
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

if __name__ == '__main__':
    unittest.main()
