
import struct
import socket

from zope.interface import implements
from twisted.application import service
from twisted.application import internet
from twisted.internet import protocol

from axiom.item import Item
from axiom.attributes import text, integer, reference, inmemory

from squeal.isqueal import *

class DiscoveryService(Item, service.Service):

    implements(IDiscoveryService)

    parent = inmemory()
    listen = integer()
    hostname = text()
    protocol = inmemory()
    running = inmemory()

    def __init__(self, config, store):
        listen = config.getint("DiscoveryService", "listen")
        hostname = unicode(config.get("DiscoveryService", "hostname"))
        Item.__init__(self, store=store, listen=listen, hostname=hostname)

    def activate(self):
        self.protocol = DiscoveryProtocol(self)

    def startService(self):
        internet.UDPServer(self.listen, self.protocol).setServiceParent(self.parent)
        return service.Service.startService(self)

class Datagram(object):

    @classmethod
    def decode(self, data):
        if data[0] == 'd':
            return ClientDiscoveryDatagram(data)
        else:
            raise NotImplementedError

class ClientDiscoveryDatagram(Datagram):

    device = None
    firmware = None
    client = None

    def __init__(self, data):
        s = struct.unpack('!cxBB8x6B', data)
        assert  s[0] == 'd'
        self.device = s[1]
        self.firmware = hex(s[2])
        self.client = ":".join(["%02x" % (x,) for x in s[3:]])

    def __repr__(self):
        return "<%s device=%r firmware=%r client=%r>" % (self.__class__.__name__, self.device, self.firmware, self.client)

class DiscoveryResponseDatagram(Datagram):

    def __init__(self, hostname, port):
        hostname = hostname[:16].encode("UTF-8")
        hostname += (16 - len(hostname)) * '\x00'
        self.packet = struct.pack('!c16s', 'D', hostname)

class DiscoveryProtocol(protocol.DatagramProtocol):

    def __init__(self, service):
        self.service = service

    def datagramReceived(self, datagram, addr):
        dgram = Datagram.decode(datagram)
        print "Data received from %r: %r" % (addr, dgram)
        if isinstance(dgram, ClientDiscoveryDatagram):
            self.sendDiscoveryResponse(addr)

    def sendDiscoveryResponse(self, addr):
        dgram = DiscoveryResponseDatagram(self.service.hostname, 3483)
        print "Sending discovery response %r" % (dgram.packet,)
        self.transport.write(dgram.packet, addr)

