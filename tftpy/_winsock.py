# vim: ts=4 sw=4 et ai:
"""Windows support for learning the destination address of a datagram.

CPython has no socket.recvmsg on Windows, so the IP_PKTINFO ancillary data
that says which local address a request was sent to cannot be read through
the socket module there. This module calls Winsock's WSARecvMsg through
ctypes instead. It is only imported on Windows, by TftpServer."""


import ctypes
import socket
import struct
from ctypes import wintypes

# From ws2ipdef.h. The socket module does not export it on Windows in older
# Python versions (3.9 lacks it).
IP_PKTINFO = getattr(socket, "IP_PKTINFO", 19)

SIO_GET_EXTENSION_FUNCTION_POINTER = 0xC8000006

# SOCKET is a UINT_PTR.
SOCKET = ctypes.c_size_t


class GUID(ctypes.Structure):
    _fields_ = [
        ("Data1", wintypes.DWORD),
        ("Data2", wintypes.WORD),
        ("Data3", wintypes.WORD),
        ("Data4", ctypes.c_ubyte * 8),
    ]


# WSARecvMsg is not exported by ws2_32.dll; its address is looked up at
# runtime by this GUID.
WSAID_WSARECVMSG = GUID(
    0xF689D7C8, 0x6F1F, 0x436B,
    (ctypes.c_ubyte * 8)(0x8A, 0x53, 0xE5, 0x4F, 0xE3, 0x51, 0xC3, 0x22),
)


class WSABUF(ctypes.Structure):
    _fields_ = [("len", wintypes.ULONG), ("buf", ctypes.c_void_p)]


class WSAMSG(ctypes.Structure):
    _fields_ = [
        ("name", ctypes.c_void_p),
        ("namelen", ctypes.c_int),
        ("lpBuffers", ctypes.POINTER(WSABUF)),
        ("dwBufferCount", wintypes.ULONG),
        ("Control", WSABUF),
        ("dwFlags", wintypes.ULONG),
    ]


class WSACMSGHDR(ctypes.Structure):
    _fields_ = [
        ("cmsg_len", ctypes.c_size_t),
        ("cmsg_level", ctypes.c_int),
        ("cmsg_type", ctypes.c_int),
    ]


LPFN_WSARECVMSG = ctypes.WINFUNCTYPE(
    ctypes.c_int,
    SOCKET,
    ctypes.POINTER(WSAMSG),
    ctypes.POINTER(wintypes.DWORD),
    ctypes.c_void_p,
    ctypes.c_void_p,
)

_ws2_32 = ctypes.WinDLL("ws2_32")
_ws2_32.WSAIoctl.argtypes = [
    SOCKET, wintypes.DWORD, ctypes.c_void_p, wintypes.DWORD,
    ctypes.c_void_p, wintypes.DWORD, ctypes.POINTER(wintypes.DWORD),
    ctypes.c_void_p, ctypes.c_void_p,
]
_ws2_32.WSAIoctl.restype = ctypes.c_int
_ws2_32.WSAGetLastError.restype = ctypes.c_int

# Control messages and their data are aligned to the pointer size
# (WSA_CMSGHDR_ALIGN and WSA_CMSGDATA_ALIGN in ws2def.h).
_ALIGN = ctypes.sizeof(ctypes.c_void_p)
_CMSG_HDR_SIZE = ctypes.sizeof(WSACMSGHDR)

# Windows IN_PKTINFO is { IN_ADDR ipi_addr; ULONG ipi_ifindex; }. Unlike
# the Linux in_pktinfo it has no ipi_spec_dst, so for a broadcast request
# ipi_addr is the broadcast address.
_IN_PKTINFO = "=4sI"
_IN_PKTINFO_SIZE = struct.calcsize(_IN_PKTINFO)

# Room for the IP_PKTINFO message plus one more, should the socket have
# other options enabled.
_CONTROL_SIZE = 2 * (_CMSG_HDR_SIZE + _ALIGN + _IN_PKTINFO_SIZE + _ALIGN)

# A SOCKADDR_IN is 16 bytes; leave room for anything larger.
_NAME_SIZE = 128


def _align(length):
    return (length + _ALIGN - 1) & ~(_ALIGN - 1)


def _last_error():
    return ctypes.WinError(_ws2_32.WSAGetLastError())


def _find_pktinfo(control, length):
    """Return the destination address from the IP_PKTINFO control message
    in the first length bytes of control, or "" if there is none."""
    offset = 0
    while offset + _CMSG_HDR_SIZE <= length:
        header = WSACMSGHDR.from_buffer_copy(control, offset)
        if header.cmsg_len < _CMSG_HDR_SIZE:
            break
        data = offset + _align(_CMSG_HDR_SIZE)
        if (header.cmsg_level == socket.IPPROTO_IP
                and header.cmsg_type == IP_PKTINFO
                and header.cmsg_len >= _align(_CMSG_HDR_SIZE) + _IN_PKTINFO_SIZE):
            address, _ = struct.unpack_from(_IN_PKTINFO, control, data)
            return socket.inet_ntoa(address)
        offset += _align(header.cmsg_len)
    return ""


def make_pktinfo_receiver(sock):
    """Enable IP_PKTINFO on sock, a bound AF_INET datagram socket, and return
    a function that receives one datagram from it as
    (buffer, raddress, rport, localip), where localip is the address the
    datagram was sent to, or "" if it carried no IP_PKTINFO. Raises OSError
    if Winsock refuses either step; the receive function raises OSError
    like socket.recvfrom does."""
    sock.setsockopt(socket.IPPROTO_IP, IP_PKTINFO, 1)

    function = ctypes.c_void_p()
    returned = wintypes.DWORD()
    guid = GUID.from_buffer_copy(WSAID_WSARECVMSG)
    if _ws2_32.WSAIoctl(
            sock.fileno(), SIO_GET_EXTENSION_FUNCTION_POINTER,
            ctypes.byref(guid), ctypes.sizeof(guid),
            ctypes.byref(function), ctypes.sizeof(function),
            ctypes.byref(returned), None, None) != 0:
        raise _last_error()
    wsarecvmsg = LPFN_WSARECVMSG(function.value)

    def receive(bufsize):
        data = ctypes.create_string_buffer(bufsize)
        name = ctypes.create_string_buffer(_NAME_SIZE)
        control = ctypes.create_string_buffer(_CONTROL_SIZE)
        buffers = WSABUF(bufsize, ctypes.cast(data, ctypes.c_void_p))
        message = WSAMSG(
            ctypes.cast(name, ctypes.c_void_p), _NAME_SIZE,
            ctypes.pointer(buffers), 1,
            WSABUF(_CONTROL_SIZE, ctypes.cast(control, ctypes.c_void_p)), 0,
        )
        received = wintypes.DWORD()
        if wsarecvmsg(sock.fileno(), ctypes.byref(message),
                      ctypes.byref(received), None, None) != 0:
            raise _last_error()

        # SOCKADDR_IN: sin_family, then sin_port and sin_addr in network
        # byte order.
        rport, raddress = struct.unpack_from("!H4s", name.raw, 2)
        localip = _find_pktinfo(control.raw, message.Control.len)
        return (data.raw[:received.value], socket.inet_ntoa(raddress),
                rport, localip)

    return receive
