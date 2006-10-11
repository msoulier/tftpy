"""Unit tests for tftpy."""

import unittest
import logging
import tftpy

class TestTftpy(unittest.TestCase):

    def setUp(self):
        tftpy.setLogLevel(logging.INFO)

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

    def testTftpPacketWRQ(self):
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

    def testTftpPacketDAT(self):
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
        ack = tftpy.TftpPacketACK()
        ack.blocknumber = 6
        ack.encode()
        self.assert_(ack.buffer != None, "Buffer populated")
        ack.decode()
        self.assertEqual(ack.opcode, 4, "ACK opcode is correct")
        self.assertEqual(ack.blocknumber, 6, "ACK blocknumber correct")

    def testTftpPacketERR(self):
        pass

    def testTftpPacketOACK(self):
        pass

if __name__ == '__main__':
    unittest.main()
