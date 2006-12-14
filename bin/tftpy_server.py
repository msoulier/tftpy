#!/usr/bin/env python

import sys, logging, os
from optparse import OptionParser
import tftpy

def main():
    usage=""
    parser = OptionParser(usage=usage)
    parser.add_option('-i',
                      '--ip',
                      action='store',
                      type='string',
                      dest='ip',
                      help='ip address to bind to (default: INADDR_ANY)',
                      default="")
    parser.add_option('-p',
                      '--port',
                      action='store',
                      type='int',
                      dest='port',
                      help='local port to use (default: 69)',
                      default=69)
    parser.add_option('-r',
                      '--root',
                      action='store',
                      type='string',
                      dest='root',
                      help='path to serve from (default: /tftpboot)',
                      default="/tftpboot")
    parser.add_option('-d',
                      '--debug',
                      action='store_true',
                      dest='debug',
                      default=False,
                      help='upgrade logging from info to debug')
    options, args = parser.parse_args()

    if options.debug:
        tftpy.setLogLevel(logging.DEBUG)
    else:
        tftpy.setLogLevel(logging.INFO)

    server = tftpy.TftpServer(options.root)
    server.listen(options.ip, options.port)

if __name__ == '__main__':
    main()
