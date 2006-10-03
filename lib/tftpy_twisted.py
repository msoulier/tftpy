#!/usr/bin/python

from twisted.internet import reactor, protocol

class TFTPProtocol(protocol.DatagramProtocol):
    pass

class TFTPProtocolFactory(protocol.ClientFactory):
    protocol = TFTPProtocol

def main():
    host = '216.191.234.113'
    port = 20001

    reactor.listenUDP(port, TFTPProtocolFactory())
    reactor.run()

if __name__ == '__main__':
    main()
