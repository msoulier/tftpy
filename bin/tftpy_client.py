#!/usr/bin/env python

import sys
from optparse import OptionParser
from tftpy import *

def main():
    usage=""
    parser = OptionParser(usage=usage)
    parser.add_option('-t',
                      '--test',
                      action='store_true',
                      dest='test',
                      help='run test case(s)',
                      default=False)
    parser.add_option('-H',
                      '--host',
                      action='store',
                      dest='host',
                      help='remote host or ip address')
    parser.add_option('-p',
                      '--port',
                      action='store',
                      dest='port',
                      help='remote port to use (default: 69)',
                      default=69)
    parser.add_option('-f',
                      '--filename',
                      action='store',
                      dest='filename',
                      help='filename to fetch')
    parser.add_option('-b',
                      '--blocksize',
                      action='store',
                      dest='blocksize',
                      help='udp packet size to use (default: 512)',
                      default=512)
    parser.add_option('-o',
                      '--output',
                      action='store',
                      dest='output',
                      help='output file (default: out)',
                      default='out')
    options, args = parser.parse_args()
    if options.test:
        options.host = "216.191.234.113"
        options.port = 20001
        options.filename = 'ipp510main.bin'
        options.output = 'ipp510main.bin'
    if not options.host or not options.filename:
        parser.print_help()
        sys.exit(1)

    class Progress(object):
        def __init__(self, out):
            self.progress = 0
            self.out = out
        def progresshook(self, pkt):
            self.progress += len(pkt.data)
            self.out("Downloaded %d bytes" % self.progress)

    progresshook = Progress(logger.info).progresshook

    tclient = TftpClient(options.host,
                         options.port,
                         options.blocksize)
    tclient.download(options.filename,
                     options.output,
                     progresshook)

if __name__ == '__main__':
    main()
