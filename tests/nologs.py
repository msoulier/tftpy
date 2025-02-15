#!/usr/bin/env python

import time
import tftpy
import os

def clientServerDownloadOptions(
    output="/tmp/out",
    cretries=tftpy.DEF_TIMEOUT_RETRIES,
    sretries=tftpy.DEF_TIMEOUT_RETRIES,
    flock=True
):
    """Fire up a client and a server and do a download."""
    root = os.path.dirname(os.path.abspath(__file__))
    server = tftpy.TftpServer(root, flock=flock)
    client = tftpy.TftpClient("localhost", 20001, {})
    # Fork a server and run the client in this process.
    child_pid = os.fork()
    if child_pid:
        # parent - let the server start
        try:
            time.sleep(1)
            client.download("640KBFILE", output, retries=cretries)
        finally:
            os.kill(child_pid, 15)
            os.waitpid(child_pid, 0)

    else:
        server.listen("localhost", 20001, retries=sretries)

def main():
    clientServerDownloadOptions()

main()
