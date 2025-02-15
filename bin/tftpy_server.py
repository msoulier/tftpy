#!/usr/bin/env python
# vim: ts=4 sw=4 et ai:
# -*- coding: utf8 -*-

import logging
import sys
from argparse import ArgumentParser

import tftpy

log = logging.getLogger("tftpy")
log.setLevel(logging.INFO)

# console handler
handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
default_formatter = logging.Formatter("[%(asctime)s] %(message)s")
handler.setFormatter(default_formatter)
log.addHandler(handler)


def main():
    usage = ""
    parser = ArgumentParser(usage=usage)
    parser.add_argument(
        "-i",
        "--ip",
        type="string",
        help="ip address to bind to (default: INADDR_ANY)",
        default="",
    )
    parser.add_argument(
        "-p",
        "--port",
        type="int",
        help="local port to use (default: 69)",
        default=69,
    )
    parser.add_argument(
        "-r",
        "--root",
        type="string",
        help="path to serve from",
        default=None,
    )
    parser.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        default=False,
        help="Do not log unless it is critical",
    )
    parser.add_argument(
        "-d",
        "--debug",
        action="store_true",
        default=False,
        help="upgrade logging from info to debug",
    )
    parser.add_argument(
        "-n",
        "--no-lock",
        action="store_false",
        dest="flock",
        default=True,
        help="disable advisory locking on files"
    )
    options = parser.parse_args()

    if options.debug:
        log.setLevel(logging.DEBUG)
        # increase the verbosity of the formatter
        debug_formatter = logging.Formatter(
            "[%(asctime)s%(msecs)03d] %(levelname)s [%(name)s:%(lineno)s] %(message)s"
        )
        handler.setFormatter(debug_formatter)
    elif options.quiet:
        log.setLevel(logging.WARNING)

    if not options.root:
        parser.print_help()
        sys.exit(1)

    server = tftpy.TftpServer(options.root, flock=options.flock)
    try:
        server.listen(options.ip, options.port)
    except tftpy.TftpException as err:
        sys.stderr.write("%s\n" % str(err))
        sys.exit(1)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
