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
import logging
import uuid
try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict

from zope.interface import implements
from twisted.application import service
from twisted.application import internet
from twisted.internet import protocol
from twisted.python import log

from axiom.item import Item
from axiom.attributes import text, integer, reference, inmemory

import squeal
from squeal.isqueal import *
from socket import gethostname

class DiscoveryService(Item, service.Service):

    """ http://wiki.slimdevices.com/index.php/SLIMP3ClientProtocol """

    implements(IDiscoveryService)
    powerupInterfaces = (IDiscoveryService, service.IService)

    parent = inmemory()
    listen = integer(default=3483)
    hostname = text(default=unicode(gethostname()))
    protocol = inmemory()
    running = inmemory()
    uuid = text(default=unicode(uuid.uuid1())) # :todo: decide on a reasonable value

    def activate(self):
        self.protocol = DiscoveryProtocol(self)

    def startService(self):
        internet.UDPServer(self.listen, self.protocol).setServiceParent(self.parent)
        return service.Service.startService(self)

class Datagram(object):

    @classmethod
    def decode(self, data):
        if data[0] == 'e':
            return TLVDiscoveryRequestDatagram(data)
        elif data[0] == 'E':
            return TLVDiscoveryResponseDatagram(data)
        elif data[0] == 'd':
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


class TLVDiscoveryRequestDatagram(Datagram):
    
    def __init__(self, data):
        requestdata = OrderedDict()
        assert data[0] == 'e'
        idx = 1
        length = len(data)-5
        while idx <= length:
            typ, l = struct.unpack_from("4sB", data, idx)
            if l:
                val = data[idx+5:idx+5+l]
                idx += 5+l
            else:
                val = None
                idx += 5
            requestdata[typ] = val
        self.data = requestdata
            
    def __repr__(self):
        return "<%s data=%r>" % (self.__class__.__name__, self.data.items())

class TLVDiscoveryResponseDatagram(Datagram):

    def __init__(self, responsedata):
        parts = ['E'] # new discovery format
        for typ, value in responsedata.items():
            if value is None:
                value = ''
            elif len(value) > 255:
                log.msg("Response %s too long, truncating to 255 bytes" % typ,
                        logLevel=logging.WARNING)
                value = value[:255]
            parts.extend((typ, chr(len(value)), value))
        self.packet = ''.join(parts)


class DiscoveryProtocol(protocol.DatagramProtocol):

    def __init__(self, service):
        self.service = service

    def build_TLV_response(self, requestdata):
        responsedata = OrderedDict()
        for typ, value in requestdata.items():
            if typ == 'NAME':
                # send full host name - no truncation
                value = self.service.hostname.encode("UTF-8")
            elif typ == 'IPAD':
                # send ipaddress as a string only if it is set
                value = self.transport.getHost().host
                # :todo: IPv6
                if value == '0.0.0.0':
                    # do not send back an ip address
                    typ = None
            elif typ == 'JSON':
                # send port as a string
                json_port = 9000 # todo: web.service.port
                value = str(json_port)
            elif typ == 'VERS':
                # send server version
                 value = squeal.__version__
            elif typ == 'UUID':
                # send server uuid
                value = self.service.uuid
            elif typ == 'JVID':
                # not handle, just log the information
                typ = None
                log.msg("Jive: %x:%x:%x:%x:%x:%x:" % struct.unpack('>6B', value),
                        logLevel=logging.INFO)
            else:
                log.error('Unexpected information request: %r', typ)
                typ = None
            if typ:
                responsedata[typ] = value
        return responsedata

    def datagramReceived(self, datagram, addr):
        dgram = Datagram.decode(datagram)
        log.msg("Data received from %r: %r" % (addr, dgram), system="squeal.net.discovery.DiscoveryProtocol")
        if isinstance(dgram, ClientDiscoveryDatagram):
            self.sendDiscoveryResponse(addr)
        elif isinstance(dgram, TLVDiscoveryRequestDatagram):
            resonsedata = self.build_TLV_response(dgram.data)
            self.sendTLVDiscoveryResponse(resonsedata, addr)

    def sendDiscoveryResponse(self, addr):
        dgram = DiscoveryResponseDatagram(self.service.hostname, 3483)
        log.msg("Sending discovery response %r" % (dgram.packet,), system="squeal.net.discovery.DiscoveryProtocol")
        self.transport.write(dgram.packet, addr)

    def sendTLVDiscoveryResponse(self, resonsedata, addr):
        dgram = TLVDiscoveryResponseDatagram(resonsedata)
        log.msg("Sending discovery response %r" % (dgram.packet,), system="squeal.net.discovery.DiscoveryProtocol")
        self.transport.write(dgram.packet, addr)

