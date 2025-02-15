#!/usr/bin/env python
# vim: ts=4 sw=4 et ai:
# -*- coding: utf8 -*-

import logging
import os
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
        "-H",
        "--host",
        help="remote host or ip address",
    )
    parser.add_argument(
        "-p",
        "--port",
        help="remote port to use (default: 69)",
        default=69,
    )
    parser.add_argument(
        "-f",
        "--filename",
        help="filename to fetch (deprecated, use download)",
    )
    parser.add_argument(
        "-D",
        "--download",
        help="filename to download",
    )
    parser.add_argument(
        "-u",
        "--upload",
        help="filename to upload",
    )
    parser.add_argument(
        "-b",
        "--blksize",
        help="udp packet size to use (default: 512)",
    )
    parser.add_argument(
        "-o",
        "--output",
        help="output file, - for stdout (default: same as download)",
    )
    parser.add_argument(
        "-i",
        "--input",
        help="input file, - for stdin (default: same as upload)",
    )
    parser.add_argument(
        "-d",
        "--debug",
        action="store_true",
        default=False,
        help="upgrade logging from info to debug",
    )
    parser.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        default=False,
        help="downgrade logging from info to warning",
    )
    parser.add_argument(
        "-t",
        "--tsize",
        action="store_true",
        default=False,
        help="ask client to send tsize option in download",
    )
    parser.add_argument(
        "-l",
        "--localip",
        action="store",
        dest="localip",
        default="",
        help="local IP for client to bind to (ie. interface)",
    )
    parser.add_argument(
        "-n",
        "--no-lock",
        action="store_false",
        dest="flock",
        default=True,
        help="run without advisory locking on files"
    )
    options = parser.parse_args()
    # Handle legacy --filename argument.
    if options.filename:
        options.download = options.filename
    if not options.host or (not options.download and not options.upload):
        sys.stderr.write(
            "Both the --host and --filename options are required.\n")
        parser.print_help()
        sys.exit(1)

    if options.debug and options.quiet:
        sys.stderr.write(
            "The --debug and --quiet options are mutually exclusive.\n")
        parser.print_help()
        sys.exit(1)

    class Progress:
        def __init__(self, out):
            self.progress = 0
            self.out = out

        def progresshook(self, pkt):
            if isinstance(pkt, tftpy.TftpPacketTypes.TftpPacketDAT):
                self.progress += len(pkt.data)
                self.out("Transferred %d bytes" % self.progress)
            elif isinstance(pkt, tftpy.TftpPacketTypes.TftpPacketOACK):
                self.out("Received OACK, options are: %s" % pkt.options)

    if options.debug:
        log.setLevel(logging.DEBUG)
        # increase the verbosity of the formatter
        debug_formatter = logging.Formatter(
            "[%(asctime)s%(msecs)03d] %(levelname)s [%(name)s:%(lineno)s] %(message)s"
        )
        handler.setFormatter(debug_formatter)
    elif options.quiet:
        log.setLevel(logging.WARNING)

    progresshook = Progress(log.info).progresshook

    tftp_options = {}
    if options.blksize:
        tftp_options["blksize"] = int(options.blksize)
    if options.tsize:
        tftp_options["tsize"] = 0

    tclient = tftpy.TftpClient(
        options.host,
        int(options.port),
        tftp_options,
        options.localip,
        flock=options.flock
    )
    try:
        if options.download:
            if not options.output:
                options.output = os.path.basename(options.download)
            tclient.download(
                options.download,
                options.output,
                progresshook,
            )
        elif options.upload:
            if not options.input:
                options.input = os.path.basename(options.upload)
            tclient.upload(
                options.upload,
                options.input,
                progresshook,
            )
    except tftpy.TftpException as err:
        sys.stderr.write("%s\n" % str(err))
        sys.exit(1)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
