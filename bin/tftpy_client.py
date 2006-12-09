#!/usr/bin/env python

import sys, logging, os
from optparse import OptionParser
import tftpy

def main():
    usage=""
    parser = OptionParser(usage=usage)
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
    # FIXME - default should be same as --filename
    parser.add_option('-o',
                      '--output',
                      action='store',
                      dest='output',
                      help='output file (default: same as requested filename)')
    parser.add_option('-d',
                      '--debug',
                      action='store_true',
                      dest='debug',
                      default=False,
                      help='upgrade logging from info to debug')
    options, args = parser.parse_args()
    if not options.host or not options.filename:
        parser.print_help()
        sys.exit(1)

    if not options.output:
        options.output = os.path.basename(options.filename)

    class Progress(object):
        def __init__(self, out):
            self.progress = 0
            self.out = out
        def progresshook(self, pkt):
            self.progress += len(pkt.data)
            self.out("Downloaded %d bytes" % self.progress)
        
    if options.debug:
        tftpy.setLogLevel(logging.DEBUG)
    else:
        tftpy.setLogLevel(logging.INFO)

    progresshook = Progress(tftpy.logger.info).progresshook

    tftp_options = {}
    if options.blocksize:
        tftp_options['blksize'] = int(options.blocksize)

    tclient = tftpy.TftpClient(options.host,
                               int(options.port),
                               tftp_options)

    tclient.download(options.filename,
                     options.output,
                     progresshook)

if __name__ == '__main__':
    main()
