# $Id$
#
# Copyright 2010 Doug Winter
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

""" Implementation of the Squeezebox discovery protocol. """

__author__ = "Doug Winter <doug.winter@isotoma.com>"
__docformat__ = "restructuredtext en"
__version__ = "$Revision$"[11:-2]

import struct
import socket

from zope.interface import implements
from twisted.application import service
from twisted.application import internet
from twisted.internet import protocol
from twisted.python import log

from axiom.item import Item
from axiom.attributes import text, integer, reference, inmemory

from squeal.isqueal import *

class DiscoveryService(Item, service.Service):

    """ http://wiki.slimdevices.com/index.php/SLIMP3ClientProtocol """

    implements(IDiscoveryService)
    powerupInterfaces = (IDiscoveryService,)

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
        elif data[0] == 'h':
            pass # Hello!
        elif data[0] == 'i':
            pass # IR
        elif data[0] == '2':
            pass # i2c?
        elif data[0] == 'a':
            pass # ack!

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
        log.msg("Data received from %r: %r" % (addr, dgram), system="squeal.net.discovery.DiscoveryProtocol")
        if isinstance(dgram, ClientDiscoveryDatagram):
            self.sendDiscoveryResponse(addr)

    def sendDiscoveryResponse(self, addr):
        dgram = DiscoveryResponseDatagram(self.service.hostname, 3483)
        log.msg("Sending discovery response %r" % (dgram.packet,), system="squeal.net.discovery.DiscoveryProtocol")
        self.transport.write(dgram.packet, addr)

