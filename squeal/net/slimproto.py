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

""" Implementation of the Squeezebox network protocol. This protocol is barely
documented, but what is available is here:

    http://wiki.slimdevices.com/index.php/SlimProtoTCPProtocol
"""

__author__ = "Doug Winter <doug.winter@isotoma.com>"
__docformat__ = "restructuredtext en"
__version__ = "$Revision$"[11:-2]

from zope.interface import implements
from twisted.application import service
from twisted.application import strports
from twisted.internet import protocol
from twisted.python import log

from axiom.item import Item
from axiom.attributes import text, reference, integer, inmemory

import os
import struct
import time
import decimal
from netaddr import EUI

from squeal.event import EventReactor
from squeal.player.display import Display
from squeal.player.remote import Remote
from squeal.isqueal import *

class RemoteButtonPressed(object):

    """ Someone has pressed a button on a remote control. """

    implements(IRemoteButtonPressedEvent)

    class Button:
        PLAY = 0

    def __init__(self, player, button):
        self.player = player
        self.button = button

class VolumeChanged(object):

    implements(IVolumeChangeEvent)

    def __init__(self, player, volume):
        self.player = player
        self.volume = volume

class StateChanged(object):
    implements(IPlayerStateChange)

    class State:
        DISCONNECTED = 0
        ESTABLISHED = 1
        STOPPED = 2
        PAUSED = 3
        PLAYING = 4
        UNDERRUN = 5
        READY = 6

    def __init__(self, player, state):
        self.player = player
        self.state = state

class SlimService(Item, service.Service):

    implements(ISlimPlayerService)
    powerupInterfaces = (ISlimPlayerService,)

    listen = text()
    parent = inmemory()
    pages = inmemory()
    players = inmemory()
    factory = inmemory()
    running = inmemory()

    def __init__(self, config, store):
        listen = unicode(config.get("SlimService", "listen"))
        Item.__init__(self, store=store, listen=listen)

    def activate(self):
        self.players = []
        self.factory = Factory(self)

    @property
    def evreactor(self):
        return self.store.findFirst(EventReactor)

    def startService(self):
        strports.service(self.listen, self.factory).setServiceParent(self.parent)
        return service.Service.startService(self)

    def play(self, track):
        """ Play the track. """
        assert ITrack.providedBy(track)
        log.msg("Playing %r" % track, system="squeal.net.slimproto.SlimService")
        for p in self.players:
            p.play(track)

    def stop(self):
        for p in self.players:
            p.stop()

class Player(protocol.Protocol):

    # these numbers are also in a dict in Collection.  This should obviously be refactored.
    typeMap = {
        0: 'o', # ogg
        1: 'm', # mp3
        2: 'f', # flac
        3: 'p', # pcm (wav etc.)
    }

    def __init__(self):
        self.buffer = ''
        self.display = Display()
        self.volume = 0
        self.device_type = None
        self.mac_address = None

    @property
    def service(self):
        return self.factory.service

    def connectionEstablished(self):
        """ Called when a connection has been successfully established with
        the player. """
        self.service.evreactor.fireEvent(StateChanged(self, StateChanged.State.ESTABLISHED))
        self.render("Connected to Squeal")
        log.msg("Connected to squeezebox", system="squeal.net.slimproto.Player")

    def connectionLost(self, reason=protocol.connectionDone):
        self.service.evreactor.fireEvent(StateChanged(self, StateChanged.State.DISCONNECTED))
        self.service.players.remove(self)

    def dataReceived(self, data):
        self.buffer = self.buffer + data
        if len(self.buffer) > 8:
            operation, length = self.buffer[:4], self.buffer[4:8]
            length = struct.unpack('!I', length)[0]
            plen = length + 8
            if len(self.buffer) >= plen:
                packet, self.buffer = self.buffer[8:plen], self.buffer[plen:]
                operation = operation.strip("!").strip(" ")
                handler = getattr(self, "process_%s" % operation, None)
                if handler is None:
                    raise NotImplementedError
                handler(packet)

    def sendFrame(self, command, data):
        packet = struct.pack('!H', len(data) + 4) + command + data
        #print "Sending packet %r" % packet
        self.transport.write(packet)

    def sendVersion(self):
        self.sendFrame('vers', '7.0')

    def packStream(self, command, autostart="1", formatbyte = 'o', pcmargs = '1321', threshold = 255, spdif = 0, transDuration = 0, transType = '0', flags = 0x40, outputThreshold = 0, replayGain = 0, serverPort = 9000, serverIp = 0):
        return struct.pack("!ccc4sBBBcBBBLHL",
                           command, autostart, formatbyte, pcmargs,
                           threshold, spdif, transDuration, transType,
                           flags, outputThreshold, 0, replayGain, serverPort, serverIp)

    def stopStreaming(self):
        data = self.packStream("q", autostart="0", flags=0)
        self.sendFrame("strm", data)

    def stop(self):
        self.stopStreaming()

    def play(self, track):
        command = 's'
        autostart = '1'
        formatbyte = self.typeMap[track.type]
        data = self.packStream(command, autostart=autostart, flags=0x00, formatbyte=formatbyte)
        request = "GET %s HTTP/1.0\r\n\r\n" % (track.player_uri(),)
        data = data + request.encode("utf-8")
        self.sendFrame('strm', data)
        self.service.evreactor.fireEvent(StateChanged(self, StateChanged.State.PLAYING))
        self.displayTrack(track)

    def displayTrack(self, track):
        self.render("%s by %s" % (track.title, track.artist))

    def process_HELO(self, data):
        devices = {2: 'squeezebox', 3: 'softsqueeze', 4: 'squeezebox2', 5: 'transporter', 6: 'softsqueeze3'}
        #(devId, rev, mac, wlan, bytes) = struct.unpack('BB6sHL', data[:16])
        (devId, rev, mac) = struct.unpack('BB6s', data[:8])
        (mac,) = struct.unpack("l", "00" + mac)
        mac = EUI(mac)
        self.device_type = devices.get(devId, 'unknown device')
        self.mac_address = str(mac)
        log.msg("HELO received from %s %s" % (self.mac_address, self.device_type), system="squeal.net.slimproto.Player")
        self.initClient()

    def initClient(self):
        self.sendVersion()
        self.stopStreaming()
        self.setBrightness()
        self.disableVisualisation()
        self.sendFrame("setd", struct.pack("B", 0))
        self.sendFrame("setd", struct.pack("B", 4))
        self.enableAudio()
        self.setVolume(0x1800)
        self.sendFrame("strm", self.packStream('t', autostart="1", flags=0, replayGain=int(time.time() * 1000 % 0xffffffff)))
        self.connectionEstablished()

    def enableAudio(self):
        self.sendFrame("aude", struct.pack("2B", 1, 1))

    def setVolume(self, volume):
        self.volume = volume
        self.sendFrame("audg", struct.pack("!2I2B2I", 0, 0, 1, 0xff, volume, volume))
        most = volume >> 16
        least = volume - (most << 16)
        d = decimal.Decimal("%d.%d" % (most, least))
        self.service.evreactor.fireEvent(VolumeChanged(self, d))

    def setBrightness(self, level=4):
        assert 0 <= level <= 4
        self.sendFrame("grfb", struct.pack("!H", level))

    def disableVisualisation(self):
        self.sendFrame("visu", struct.pack("!BB", 0, 0))

    def render(self, text):
        self.display.clear()
        self.display.renderText(text, "DejaVu-Sans", 16, (0,0))
        self.updateDisplay(self.display.frame())

    def updateDisplay(self, bitmap, transition = 'c', offset=0, param=0):
        frame = struct.pack("!Hcb", offset, transition, param) + bitmap
        self.sendFrame("grfe", frame)

    def process_STAT(self, data):
        #print "STAT received: %r" % data
        ev = data[:4]
        if ev == '\x00\x00\x00\x00':
            log.msg("Presumed informational stat message", system="squeal.net.slimproto.Player")
        else:
            handler = getattr(self, 'stat_%s' % ev, None)
            if handler is None:
                raise NotImplementedError("Stat message %r not known" % ev)
            handler(data[4:])

    def stat_aude(self, data):
        log.msg("ACK aude", system="squeal.net.slimproto.Player")

    def stat_audg(self, data):
        log.msg("ACK audg", system="squeal.net.slimproto.Player")

    def stat_strm(self, data):
        log.msg("ACK strm", system="squeal.net.slimproto.Player")

    def stat_STMc(self, data):
        log.msg("Status Message: Connect", system="squeal.net.slimproto.Player")

    def stat_STMd(self, data):
        log.msg("Decoder Ready", system="squeal.net.slimproto.Player")
        self.service.evreactor.fireEvent(StateChanged(self, StateChanged.State.READY))

    def stat_STMe(self, data):
        log.msg("Connection established", system="squeal.net.slimproto.Player")

    def stat_STMf(self, data):
        log.msg("Status Message: Connection closed", system="squeal.net.slimproto.Player")

    def stat_STMh(self, data):
        log.msg("Status Message: End of headers", system="squeal.net.slimproto.Player")

    def stat_STMn(self, data):
        log.msg("Decoder does not support file format", system="squeal.net.slimproto.Player")

    def stat_STMo(self, data):
        log.msg("Output Underrun", system="squeal.net.slimproto.Player")

    def stat_STMp(self, data):
        log.msg("Pause confirmed", system="squeal.net.slimproto.Player")

    def stat_STMr(self, data):
        log.msg("Resume confirmed", system="squeal.net.slimproto.Player")

    def stat_STMs(self, data):
        log.msg("Player status message: playback of new track has started", system="squeal.net.slimproto.Player")

    def stat_STMt(self, data):
        """ Timer heartbeat """
        self.last_heartbeat = time.time()

    def stat_STMu(self, data):
        log.msg("Underrun", system="squeal.net.slimproto.Player")

    def process_BYE(self, data):
        log.msg("BYE received", system="squeal.net.slimproto.Player")

    def process_RESP(self, data):
        log.msg("RESP received", system="squeal.net.slimproto.Player")

    def process_BODY(self, data):
        log.msg("BODY received", system="squeal.net.slimproto.Player")

    def process_META(self, data):
        log.msg("META received", system="squeal.net.slimproto.Player")

    def process_DSCO(self, data):
        log.msg("Data Stream Disconnected", system="squeal.net.slimproto.Player")

    def process_DBUG(self, data):
        log.msg("DBUG received", system="squeal.net.slimproto.Player")

    def process_IR(self, data):
        (time, code) = struct.unpack("!IxxI", data)
        command = Remote.codes.get(code, None)
        if command is not None:
            log.msg("IR received: %r, %r" % (time, command), system="squeal.net.slimproto.Player")
            handler = getattr(self, "process_remote_" + command, None)
            if handler is not None:
                handler()
        else:
            log.msg("Unknown IR received: %r, %r" % (time, code), system="squeal.net.slimproto.Player")

    def process_remote_volumeUp(self):
        vol = self.volume + 0x0400 # some increment
        self.setVolume(vol)

    def process_remote_volumeDown(self):
        vol = self.volume - 0x0400
        self.setVolume(vol)

    def process_remote_play(self):
        self.service.evreactor.fireEvent(RemoteButtonPressed(self, RemoteButtonPressed.Button.PLAY))

    def process_RAWI(self, data):
        log.msg("RAWI received", system="squeal.net.slimproto.Player")

    def process_ANIC(self, data):
        log.msg("ANIC received", system="squeal.net.slimproto.Player")

    def process_BUTN(self, data):
        log.msg("BUTN received", system="squeal.net.slimproto.Player")

    def process_KNOB(self, data):
        log.msg("KNOB received", system="squeal.net.slimproto.Player")

    def process_SETD(self, data):
        log.msg("SETD received", system="squeal.net.slimproto.Player")

    def process_UREQ(self, data):
        log.msg("UREQ received", system="squeal.net.slimproto.Player")

class Factory(protocol.ServerFactory):

    protocol = Player

    def __init__(self, service):
        self.service = service

    def buildProtocol(self, addr):
        p = self.protocol()
        p.factory = self
        self.service.players.append(p)
        return p

