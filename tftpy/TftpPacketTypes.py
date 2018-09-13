# vim: ts=4 sw=4 et ai:
# -*- coding: utf8 -*-
"""This module implements the packet types of TFTP itself, and the
corresponding encode and decode methods for them."""


import struct
import sys
import logging
from .TftpShared import *

log = logging.getLogger('tftpy.TftpPacketTypes')

class TftpSession(object):
    """This class is the base class for the tftp client and server. Any shared
    code should be in this class."""
    # FIXME: do we need this anymore?
    pass

class TftpPacketWithOptions(object):
    """This class exists to permit some TftpPacket subclasses to share code
    regarding options handling. It does not inherit from TftpPacket, as the
    goal is just to share code here, and not cause diamond inheritance."""

    def __init__(self):
        self.options = {}

    # Always use unicode strings, except at the encode/decode barrier.
    # Simpler to keep things clear.
    def setoptions(self, options):
        log.debug("in TftpPacketWithOptions.setoptions")
        log.debug("options: %s", options)
        myoptions = {}
        for key in options:
            newkey = key
            if isinstance(key, bytes):
                newkey = newkey.decode('ascii')
            newval = options[key]
            if isinstance(newval, bytes):
                newval = newval.decode('ascii')
            myoptions[newkey] = newval
            log.debug("populated myoptions with %s = %s", newkey, myoptions[newkey])

        log.debug("setting options hash to: %s", myoptions)
        self._options = myoptions

    def getoptions(self):
        log.debug("in TftpPacketWithOptions.getoptions")
        return self._options

    # Set up getter and setter on options to ensure that they are the proper
    # type. They should always be strings, but we don't need to force the
    # client to necessarily enter strings if we can avoid it.
    options = property(getoptions, setoptions)

    def decode_options(self, buffer):
        """This method decodes the section of the buffer that contains an
        unknown number of options. It returns a dictionary of option names and
        values."""
        fmt = b"!"
        options = {}

        log.debug("decode_options: buffer is: %s", repr(buffer))
        log.debug("size of buffer is %d bytes", len(buffer))
        if len(buffer) == 0:
            log.debug("size of buffer is zero, returning empty hash")
            return {}

        # Count the nulls in the buffer. Each one terminates a string.
        log.debug("about to iterate options buffer counting nulls")
        length = 0
        for i in range(len(buffer)):
            if ord(buffer[i:i+1]) == 0:
                log.debug("found a null at length %d", length)
                if length > 0:
                    fmt += b"%dsx" % length
                    length = -1
                else:
                    raise TftpException("Invalid options in buffer")
            length += 1

        log.debug("about to unpack, fmt is: %s", fmt)
        mystruct = struct.unpack(fmt, buffer)

        tftpassert(len(mystruct) % 2 == 0,
                   "packet with odd number of option/value pairs")

        for i in range(0, len(mystruct), 2):
            key = mystruct[i].decode('ascii')
            val = mystruct[i+1].decode('ascii')
            log.debug("setting option %s to %s", key, val)
            log.debug("types are %s and %s", type(key), type(val))
            options[key] = val

        return options

class TftpPacket(object):
    """This class is the parent class of all tftp packet classes. It is an
    abstract class, providing an interface, and should not be instantiated
    directly."""
    def __init__(self):
        self.opcode = 0
        self.buffer = None

    def encode(self):
        """The encode method of a TftpPacket takes keyword arguments specific
        to the type of packet, and packs an appropriate buffer in network-byte
        order suitable for sending over the wire.

        This is an abstract method."""
        raise NotImplementedError("Abstract method")

    def decode(self):
        """The decode method of a TftpPacket takes a buffer off of the wire in
        network-byte order, and decodes it, populating internal properties as
        appropriate. This can only be done once the first 2-byte opcode has
        already been decoded, but the data section does include the entire
        datagram.

        This is an abstract method."""
        raise NotImplementedError("Abstract method")

class TftpPacketInitial(TftpPacket, TftpPacketWithOptions):
    """This class is a common parent class for the RRQ and WRQ packets, as
    they share quite a bit of code."""
    def __init__(self):
        TftpPacket.__init__(self)
        TftpPacketWithOptions.__init__(self)
        self.filename = None
        self.mode = None

    def encode(self):
        """Encode the packet's buffer from the instance variables."""
        tftpassert(self.filename, "filename required in initial packet")
        tftpassert(self.mode, "mode required in initial packet")
        # Make sure filename and mode are bytestrings.
        filename = self.filename
        mode = self.mode
        if not isinstance(filename, bytes):
            filename = filename.encode('ascii')
        if not isinstance(self.mode, bytes):
            mode = mode.encode('ascii')

        ptype = None
        if self.opcode == 1: ptype = "RRQ"
        else:                ptype = "WRQ"
        log.debug("Encoding %s packet, filename = %s, mode = %s",
            ptype, filename, mode)
        for key in self.options:
            log.debug("    Option %s = %s", key, self.options[key])

        fmt = b"!H"
        fmt += b"%dsx" % len(filename)
        if mode == b"octet":
            fmt += b"5sx"
        else:
            raise AssertionError("Unsupported mode: %s" % mode)
        # Add options. Note that the options list must be bytes.
        options_list = []
        if len(list(self.options.keys())) > 0:
            log.debug("there are options to encode")
            for key in self.options:
                # Populate the option name
                name = key
                if not isinstance(name, bytes):
                    name = name.encode('ascii')
                options_list.append(name)
                fmt += b"%dsx" % len(name)
                # Populate the option value
                value = self.options[key]
                # Work with all strings.
                if isinstance(value, int):
                    value = str(value)
                if not isinstance(value, bytes):
                    value = value.encode('ascii')
                options_list.append(value)
                fmt += b"%dsx" % len(value)

        log.debug("fmt is %s", fmt)
        log.debug("options_list is %s", options_list)
        log.debug("size of struct is %d", struct.calcsize(fmt))
        
        self.buffer = struct.pack(fmt,
                                  self.opcode,
                                  filename,
                                  mode,
                                  *options_list)

        log.debug("buffer is %s", repr(self.buffer))
        return self

    def decode(self):
        tftpassert(self.buffer, "Can't decode, buffer is empty")

        # FIXME - this shares a lot of code with decode_options
        nulls = 0
        fmt = b""
        nulls = length = tlength = 0
        log.debug("in decode: about to iterate buffer counting nulls")
        subbuf = self.buffer[2:]
        for i in range(len(subbuf)):
            if ord(subbuf[i:i+1]) == 0:
                nulls += 1
                log.debug("found a null at length %d, now have %d", length, nulls)
                fmt += b"%dsx" % length
                length = -1
                # At 2 nulls, we want to mark that position for decoding.
                if nulls == 2:
                    break
            length += 1
            tlength += 1

        log.debug("hopefully found end of mode at length %d", tlength)
        # length should now be the end of the mode.
        tftpassert(nulls == 2, "malformed packet")
        shortbuf = subbuf[:tlength+1]
        log.debug("about to unpack buffer with fmt: %s", fmt)
        log.debug("unpacking buffer: %s", repr(shortbuf))
        mystruct = struct.unpack(fmt, shortbuf)

        tftpassert(len(mystruct) == 2, "malformed packet")
        self.filename = mystruct[0].decode('ascii')
        self.mode = mystruct[1].decode('ascii').lower() # force lc - bug 17
        log.debug("set filename to %s", self.filename)
        log.debug("set mode to %s", self.mode)

        self.options = self.decode_options(subbuf[tlength+1:])
        log.debug("options dict is now %s", self.options)
        return self

class TftpPacketRRQ(TftpPacketInitial):
    """
::

            2 bytes    string   1 byte     string   1 byte
            -----------------------------------------------
    RRQ/  | 01/02 |  Filename  |   0  |    Mode    |   0  |
    WRQ     -----------------------------------------------
    """
    def __init__(self):
        TftpPacketInitial.__init__(self)
        self.opcode = 1

    def __str__(self):
        s = 'RRQ packet: filename = %s' % self.filename
        s += ' mode = %s' % self.mode
        if self.options:
            s += '\n    options = %s' % self.options
        return s

class TftpPacketWRQ(TftpPacketInitial):
    """
::

            2 bytes    string   1 byte     string   1 byte
            -----------------------------------------------
    RRQ/  | 01/02 |  Filename  |   0  |    Mode    |   0  |
    WRQ     -----------------------------------------------
    """
    def __init__(self):
        TftpPacketInitial.__init__(self)
        self.opcode = 2

    def __str__(self):
        s = 'WRQ packet: filename = %s' % self.filename
        s += ' mode = %s' % self.mode
        if self.options:
            s += '\n    options = %s' % self.options
        return s

class TftpPacketDAT(TftpPacket):
    """
::

            2 bytes    2 bytes       n bytes
            ---------------------------------
    DATA  | 03    |   Block #  |    Data    |
            ---------------------------------
    """
    def __init__(self):
        TftpPacket.__init__(self)
        self.opcode = 3
        self.blocknumber = 0
        self.data = None

    def __str__(self):
        s = 'DAT packet: block %s' % self.blocknumber
        if self.data:
            s += '\n    data: %d bytes' % len(self.data)
        return s

    def encode(self):
        """Encode the DAT packet. This method populates self.buffer, and
        returns self for easy method chaining."""
        if len(self.data) == 0:
            log.debug("Encoding an empty DAT packet")
        data = self.data
        if not isinstance(self.data, bytes):
            data = self.data.encode('ascii')
        fmt = b"!HH%ds" % len(data)
        self.buffer = struct.pack(fmt,
                                  self.opcode,
                                  self.blocknumber,
                                  data)
        return self

    def decode(self):
        """Decode self.buffer into instance variables. It returns self for
        easy method chaining."""
        # We know the first 2 bytes are the opcode. The second two are the
        # block number.
        (self.blocknumber,) = struct.unpack(str("!H"), self.buffer[2:4])
        log.debug("decoding DAT packet, block number %d", self.blocknumber)
        log.debug("should be %d bytes in the packet total", len(self.buffer))
        # Everything else is data.
        self.data = self.buffer[4:]
        log.debug("found %d bytes of data", len(self.data))
        return self

class TftpPacketACK(TftpPacket):
    """
::

            2 bytes    2 bytes
            -------------------
    ACK   | 04    |   Block #  |
            --------------------
    """
    def __init__(self):
        TftpPacket.__init__(self)
        self.opcode = 4
        self.blocknumber = 0

    def __str__(self):
        return 'ACK packet: block %d' % self.blocknumber

    def encode(self):
        log.debug("encoding ACK: opcode = %d, block = %d",
            self.opcode, self.blocknumber)
        self.buffer = struct.pack(str("!HH"), self.opcode, self.blocknumber)
        return self

    def decode(self):
        if len(self.buffer) > 4:
            log.debug("detected TFTP ACK but request is too large, will truncate")
            log.debug("buffer was: %s", repr(self.buffer))
            self.buffer = self.buffer[0:4]
        self.opcode, self.blocknumber = struct.unpack(str("!HH"), self.buffer)
        log.debug("decoded ACK packet: opcode = %d, block = %d",
            self.opcode, self.blocknumber)
        return self

class TftpPacketERR(TftpPacket):
    """
::

            2 bytes  2 bytes        string    1 byte
            ----------------------------------------
    ERROR | 05    |  ErrorCode |   ErrMsg   |   0  |
            ----------------------------------------

    Error Codes

    Value     Meaning

    0         Not defined, see error message (if any).
    1         File not found.
    2         Access violation.
    3         Disk full or allocation exceeded.
    4         Illegal TFTP operation.
    5         Unknown transfer ID.
    6         File already exists.
    7         No such user.
    8         Failed to negotiate options
    """
    def __init__(self):
        TftpPacket.__init__(self)
        self.opcode = 5
        self.errorcode = 0
        # FIXME: We don't encode the errmsg...
        self.errmsg = None
        # FIXME - integrate in TftpErrors references?
        self.errmsgs = {
            1: b"File not found",
            2: b"Access violation",
            3: b"Disk full or allocation exceeded",
            4: b"Illegal TFTP operation",
            5: b"Unknown transfer ID",
            6: b"File already exists",
            7: b"No such user",
            8: b"Failed to negotiate options"
            }

    def __str__(self):
        s = 'ERR packet: errorcode = %d' % self.errorcode
        s += '\n    msg = %s' % self.errmsgs.get(self.errorcode, '')
        return s

    def encode(self):
        """Encode the DAT packet based on instance variables, populating
        self.buffer, returning self."""
        fmt = b"!HH%dsx" % len(self.errmsgs[self.errorcode])
        log.debug("encoding ERR packet with fmt %s", fmt)
        self.buffer = struct.pack(fmt,
                                  self.opcode,
                                  self.errorcode,
                                  self.errmsgs[self.errorcode])
        return self

    def decode(self):
        "Decode self.buffer, populating instance variables and return self."
        buflen = len(self.buffer)
        tftpassert(buflen >= 4, "malformed ERR packet, too short")
        log.debug("Decoding ERR packet, length %s bytes", buflen)
        if buflen == 4:
            log.debug("Allowing this affront to the RFC of a 4-byte packet")
            fmt = b"!HH"
            log.debug("Decoding ERR packet with fmt: %s", fmt)
            self.opcode, self.errorcode = struct.unpack(fmt,
                                                        self.buffer)
        else:
            log.debug("Good ERR packet > 4 bytes")
            fmt = b"!HH%dsx" % (len(self.buffer) - 5)
            log.debug("Decoding ERR packet with fmt: %s", fmt)
            self.opcode, self.errorcode, self.errmsg = struct.unpack(fmt,
                                                                     self.buffer)
        log.error("ERR packet - errorcode: %d, message: %s"
                     % (self.errorcode, self.errmsg))
        return self

class TftpPacketOACK(TftpPacket, TftpPacketWithOptions):
    """
::

    +-------+---~~---+---+---~~---+---+---~~---+---+---~~---+---+
    |  opc  |  opt1  | 0 | value1 | 0 |  optN  | 0 | valueN | 0 |
    +-------+---~~---+---+---~~---+---+---~~---+---+---~~---+---+
    """
    def __init__(self):
        TftpPacket.__init__(self)
        TftpPacketWithOptions.__init__(self)
        self.opcode = 6

    def __str__(self):
        return 'OACK packet:\n    options = %s' % self.options

    def encode(self):
        fmt = b"!H" # opcode
        options_list = []
        log.debug("in TftpPacketOACK.encode")
        for key in self.options:
            value = self.options[key]
            if isinstance(value, int):
                value = str(value)
            if not isinstance(key, bytes):
                key = key.encode('ascii')
            if not isinstance(value, bytes):
                value = value.encode('ascii')
            log.debug("looping on option key %s", key)
            log.debug("value is %s", value)
            fmt += b"%dsx" % len(key)
            fmt += b"%dsx" % len(value)
            options_list.append(key)
            options_list.append(value)
        self.buffer = struct.pack(fmt, self.opcode, *options_list)
        return self

    def decode(self):
        self.options = self.decode_options(self.buffer[2:])
        return self

    def match_options(self, options):
        """This method takes a set of options, and tries to match them with
        its own. It can accept some changes in those options from the server as
        part of a negotiation. Changed or unchanged, it will return a dict of
        the options so that the session can update itself to the negotiated
        options."""
        for name in self.options:
            if name in options:
                if name == 'blksize':
                    # We can accept anything between the min and max values.
                    size = int(self.options[name])
                    if size >= MIN_BLKSIZE and size <= MAX_BLKSIZE:
                        log.debug("negotiated blksize of %d bytes", size)
                        options['blksize'] = size
                    else:
                        raise TftpException("blksize %s option outside allowed range" % size)
                elif name == 'tsize':
                    size = int(self.options[name])
                    if size < 0:
                        raise TftpException("Negative file sizes not supported")
                else:
                    raise TftpException("Unsupported option: %s" % name)
        return True
