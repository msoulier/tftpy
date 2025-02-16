#!/usr/bin/env python

import time
import tftpy
import os
import sys

def clientServerUploadOptions(options, filename, input, transmitname=None, server_kwargs=None):
    """Fire up a client and a server and do an upload."""
    root = "/tmp"
    home = os.path.dirname(os.path.abspath(__file__))
    if transmitname:
        filename = transmitname
    server_kwargs = server_kwargs or {}
    server = tftpy.TftpServer(root, **server_kwargs)
    client = tftpy.TftpClient("localhost", 20001, options)
    # Fork a server and run the client in this process.
    child_pid = os.fork()
    if child_pid:
        # parent - let the server start
        try:
            time.sleep(1)
            client.upload(filename, input)
        finally:
            os.kill(child_pid, 15)
            os.waitpid(child_pid, 0)

    else:
        server.listen("localhost", 20001)

def main():
    clientServerUploadOptions({}, "stdin", input=sys.stdin.buffer)

main()
