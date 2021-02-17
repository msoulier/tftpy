import sys

def binary_stdin():
    """
    Get a file object for reading binary bytes from stdin instead of text.
    Compatible with Py2/3, POSIX & win32.
    Credits: https://stackoverflow.com/a/38939320/531179 (CC BY-SA 3.0)
    """
    if hasattr(sys.stdin, 'buffer'): # Py3+
        return sys.stdin.buffer
    else:
        if sys.platform == 'win32':
            import os, msvcrt
            msvcrt.setmode(sys.stdin.fileno(), os.O_BINARY)
        return sys.stdin
