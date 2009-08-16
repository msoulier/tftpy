#!/usr/bin/env python

import sys, logging, os
from optparse import OptionParser
import tftpy

def main():
    usage=""
    parser = OptionParser(usage=usage)
    parser.add_option('-i',
                      '--ip',
                      type='string',
                      help='ip address to bind to (default: INADDR_ANY)',
                      default="")
    parser.add_option('-p',
                      '--port',
                      type='int',
                      help='local port to use (default: 69)',
                      default=69)
    parser.add_option('-r',
                      '--root',
                      type='string',
                      help='path to serve from',
                      default=None)
    parser.add_option('-d',
                      '--debug',
                      action='store_true',
                      default=False,
                      help='upgrade logging from info to debug')
    options, args = parser.parse_args()

    if options.debug:
        tftpy.setLogLevel(logging.DEBUG)
    else:
        tftpy.setLogLevel(logging.INFO)

    if not options.root:
        parser.print_help()
        sys.exit(1)

    server = tftpy.TftpServer(options.root)
    try:
        server.listen(options.ip, options.port)
    except tftpy.TftpException, err:
        sys.stderr.write("%s\n" % str(err))
        sys.exit(1)
    except KeyboardInterrupt:
        pass

if __name__ == '__main__':
    main()
