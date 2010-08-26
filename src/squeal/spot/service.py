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

""" Spotify orchestration. """

__author__ = "Doug Winter <doug.winter@isotoma.com>"
__docformat__ = "restructuredtext en"

from zope.interface import implements
from twisted.python import log
from twisted.application import service
from twisted.internet import reactor
from axiom.item import Item
from axiom.attributes import reference, inmemory, text, integer, timestamp
from twisted.internet.interfaces import IConsumer, IProducer, IPushProducer

from squeal.event import EventReactor
from squeal import isqueal

import web
import ispotify
from event import *
from track import SpotifyTrack
from manager import SpotifyManager
from spotify import Link
import json
import sys
import os
import signal

from formlet import form
from formlet import field

setup_form = form.Form("setup", action="install")
field.StringField(form=setup_form, name="username", label="Username")
field.StringField(form=setup_form, type_="password", name="password", label="Password")
field.SubmitButton(form=setup_form, name="submit", label="Configure spotify")

class SqueezeboxStreamer(object):


    """ Manages the streaming to a single squeezebox. One of these objects is
    created for each squeezebox that we know about. """

    implements(IProducer, IPushProducer)

    def __init__(self, player, streamer):
        # current request for this squeezebox
        self.request = None
        # track id requested.  probably not required.
        self.player = player
        self.streamer = streamer

    def new_request(self, request):
        if self.request is not None:
            log.err("New request received, while we still have an existing request!", system="squeal.spot.service.SqueezeboxStreamer")
            return
        self.request = request
        self.request.registerProducer(self, 1)

    def write(self, data):
        self.request.write(data)

    def finish(self):
        self.request.unregisterProducer()
        self.request.finish()
        self.request = None

    def pauseProducing(self):
        #self.streamer.pauseProducing()
        pass

    def resumeProducing(self):
        #self.streamer.resumeProducing()
        pass

    def stopProducing(self):
        #self.streamer.stopProducing()
        pass


class SpotifyStreamer(object):

    """ Manages streaming music to multiple squeezeboxes. Handles connections
    and disconnections of squeezeboxes, and ensures they remain synchronised.
    """

    implements(IConsumer)

    def __init__(self, service):
        self.sb = []
        self.service = service
        self.data = []
        self.paused = False
        self.finished = False
        self.all_connected = False
        self.producer = None
        self.written = 0
        self.service.evreactor.subscribe(self.player_state_changed, isqueal.IPlayerStateChange)

    def registerProducer(self, producer, streaming):
        log.msg("registerProducer", system="squeal.spot.sfy.SpotifyTransfer")
        self.producer = producer

    def unregisterProducer(self):
        """ Called by the spotify service when the end of track is reached. We
        may stop receiving data long before we stop sending it of course, so
        the request remains active. """
        log.msg("unregisterProducer", system="squeal.spot.sfy.SpotifyTransfer")
        self.producer = None
        self.finished = True

    def pauseProducing(self):
        if 'SQUEAL_DEBUG' in os.environ:
            log.msg("pauseProducing", system="squeal.spot.sfy.SpotifyTransfer")
        self.paused = True

    def stopProducing(self):
        if 'SQUEAL_DEBUG' in os.environ:
            log.msg("stopProducing", system="squeal.spot.sfy.SpotifyTransfer")

    def resumeProducing(self):
        log.msg("resumeProducing", system="squeal.spot.sfy.SpotifyTransfer")
        if self.data:
            for s in self.sb:
                s.write("".join(self.data))
            self.data = []
        if self.finished:
            for s in self.sb:
                s.finish()
            self.written = 0
        self.paused = False
        self.all_connected = False

    def play(self, track):
        """ Called when we wish to start playing.  The squeezeboxes will shortly request this track from us. """
        log.msg("Requesting %s from spotify" % track.track_id, system="squeal.spot.service.SpotifyStreamer")
        self.service.registerConsumer(self, track)

    def write(self, data):
        """ Data received from spotify, to send to all the squeezeboxen """
        self.written += len(data)
        if self.all_connected and not self.paused:
            for s in self.sb:
                s.write(data)
        else:
            self.data.append(data)

    def squeezebox_request(self, request, pid):
        connected = 0
        for s in self.sb:
            if str(id(s.player)) == pid:
                s.new_request(request)
            if s.request is not None:
                connected += 1
        if connected == len(self.sb):
            self.all_connected = True
            log.msg("All squeezeboxes connected and ready to receive data", system="squeal.spot.service.SpotifyStreamer")

    def player_state_changed(self, ev):
        if ev.state == ev.State.ESTABLISHED:
            self.player_connected(ev.player)
        elif ev.state == ev.State.DISCONNECTED:
            self.player_disconnected(ev.player)

    def player_connected(self, player):
        self.sb.append(SqueezeboxStreamer(player, self))
        log.msg("Player %r registered" % player, system="squeal.spot.service.SpotifyStreamer")

    def player_disconnected(self, player):
        for p in self.sb:
            if p.player is player:
                self.sb.remove(p)
                log.msg("Player %r removed" % player, system="squeal.spot.service.SpotifyStreamer")

class Spotify(Item, service.Service):

    """ The spotify service. Provides an interface to the rest of the system
    for the spotify session and related machinery. """

    implements(ispotify.ISpotifyService,
               isqueal.IMusicSource,
               isqueal.ITrackSource,
               isqueal.IUserConfigurable,
               isqueal.IRootResourceExtension,
               )
    powerupInterfaces = (ispotify.ISpotifyService,
                         isqueal.ITrackSource,
                         isqueal.IMusicSource,
                         isqueal.IUserConfigurable,
                         isqueal.IRootResourceExtension,
                         isqueal.IPlayMusic,
                         )

    namespace = 'spotify'
    username = text()
    password = text()
    running = inmemory()
    name = 'spotify'
    parent = inmemory()
    mgr = inmemory()
    playing = inmemory()
    streamer = inmemory()
    setup_form = setup_form

    label = "Spotify"

    def __init__(self, store, username, password):
        Item.__init__(self, store=store, username=username, password=password)

    def __repr__(self):
        return "Spotify(username=%r, password=SECRET, storeID=%r)" % (self.username, self.storeID)

    @property
    def evreactor(self):
        return self.store.findFirst(EventReactor)

    def activate(self):
        self.playing = None
        self.streamer = SpotifyStreamer(self)

    def sigint(self, handler, frame):
        # filthy hack!
        os.kill(os.getpid(), signal.SIGQUIT)

    def startService(self):
        # interrupts go nasty when we have spotify running in a thread
        signal.signal(signal.SIGINT, self.sigint)
        self.mgr = SpotifyManager(self)
        reactor.callInThread(self.mgr.connect)
        return service.Service.startService(self)

    def play(self, track):
        log.msg("Play called with %r" % track.track_id, system="squeal.spot.service.Spotify")
        self.streamer.play(track)
        return 0 # we don't actually play the music, we just prepare it

    def registerConsumer(self, consumer, track):
        log.msg("registering consumer %r on %r" % (consumer, self), system="squeal.spot.service.Spotify")
        self.playing = track
        self.mgr.load(track)
        self.mgr.play(consumer)

    def playlists(self):
        if self.mgr.ctr:
            return self.mgr.ctr
        return []

    def get_playlist(self, pid):
        for playlist in self.mgr.ctr:
            if unicode(Link.from_playlist(playlist)) == pid:
                return playlist

    def image(self, image_id):
        return self.mgr.image(image_id)

    def search(self, query):
        self.mgr.search(query)

    def getTrackByLink(self, link):
        l = Link.from_string(link)
        return l.as_track()

    def getPlaylistByLink(self, link):
        """
        Pass link as the string representation.

        This is a bit evil, there's no other way to do this, and if we
        list other people's playlists we'll need to do even more weird stuff.
        See
        http://getsatisfaction.com/spotify/topics/libspotify_does_not_provide_a_sp_link_as_playlist
        """
        for p in self.mgr.ctr:
            l = str(Link.from_playlist(p))
            if l == link:
                return p
        log.msg("Cannot find playlist for %s" % link, system="squeal.spot.service.Spotify")

    def main_widget(self):
        return web.Main()

    def squeezebox_request(self, request, pid):
        self.streamer.squeezebox_request(request, pid)

    #isqueal.TrackSource

    def get_track(self, tid):
        track = Link.from_string(tid).as_track()
        return SpotifyTrack(track, self)

    def wrap_tracks(self, *tracks):
        for t in tracks:
            yield SpotifyTrack(t, self)


    #isqueal.IRootResourceExtension

    def add_resources(self, root):
        root.putChild("spotify", web.Root(self))

