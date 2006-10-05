"""Disclaimer: This is just a placeholder. I do not yet support Twisted
Python."""

from twisted.internet import reactor, protocol

class TFTPProtocol(protocol.DatagramProtocol):
    pass

class TFTPProtocolFactory(protocol.ClientFactory):
    protocol = TFTPProtocol

def main():
    reactor.listenUDP(port, TFTPProtocolFactory())
    reactor.run()

if __name__ == '__main__':
    main()
