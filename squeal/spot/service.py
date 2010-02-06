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

""" Spotify orchestration. """

__author__ = "Doug Winter <doug.winter@isotoma.com>"
__docformat__ = "restructuredtext en"
__version__ = "$Revision$"[11:-2]

from zope.interface import Interface, implements
from twisted.python.components import registerAdapter, Adapter
from twisted.python.util import sibpath
from twisted.python import log
from twisted.application import service
from twisted.internet import reactor
from twisted.internet.interfaces import *
from axiom.item import Item
from axiom.attributes import reference, inmemory, text, integer, timestamp

import traceback

from squeal.event import EventReactor
from squeal import isqueal
from squeal.adaptivejson import IJsonAdapter

import spotify
from spotify.manager import SpotifySessionManager
from spotify import Link
from ispotify import *

from squeal.spot import web

class SpotifyEvent(object):
    """ Basic event type """
    implements(ISpotifyEvent)

class SpotifyEventWithError(object):
    """ Events that provide an error message """
    implements(ISpotifyEvent)

    def __init__(self, error):
        self.error = error

class SpotifyEventWithMessage(object):
    """ Events that provide a message """
    implements(ISpotifyEvent)

    def __init__(self, message):
        self.message = message

class SpotifySearchResults(object):
    implements(ISpotifySearchResultsEvent)
    def __init__(self, results):
        self.results = results

class SpotifyTrack(object):

    playlist = None
    track = None
    type = 3
    title = 'unknown'
    artist = 'unknown'

    def __init__(self, tid, playlist=None, track=None):
        self.playlist = playlist
        self.track = track
        self.tid = tid

    def player_url(self):
        return "/spotify?tid=%s" % self.tid

class SpotifyPlaylist(object):

    id = None
    name = None

    def __init__(self, id, status, name):
        self.id = id
        self.status = status
        self.name = name

class SpotifyPlaylistJSON(Adapter):
    implements(IJsonAdapter)

    def encode(self):
        t = self.original
        return {
            u'id': t.id,
            u'status': unicode(t.status, 'utf-8'),
            u'name': unicode(t.name, 'utf-8'),
        }

registerAdapter(SpotifyPlaylistJSON, SpotifyPlaylist, IJsonAdapter)

class SpotifyTrackJSON(Adapter):
    implements(IJsonAdapter)
    def encode(self):
        return {
            u'name': unicode(self.original.name(), 'utf-8'),
            u'isLoaded': self.original.is_loaded(),
        }

class SpotifyTrackTrackJSON(Adapter):
    implements(IJsonAdapter)
    def encode(self):
        link = Link.from_string(self.original.tid)
        track = Link.as_track(link)
        return {
            u'name': unicode(track.name(), 'utf-8'),
            u'isLoaded': track.is_loaded(),
        }

registerAdapter(SpotifyTrackJSON, spotify.Track, IJsonAdapter)
registerAdapter(SpotifyTrackTrackJSON, SpotifyTrack, IJsonAdapter)

class SpotifyManager(SpotifySessionManager):
    implements(IPushProducer, IProducer)

    appkey_file = sibpath(__file__, 'appkey.key')


    def __init__(self, service):
        self.service = service
        SpotifySessionManager.__init__(self, service.username, service.password)
        self.ctr = None
        self.playing = False
        log.msg("Connecting as %s" % service.username, system="squeal.spot.service.SpotifyManager")

    def fireEvent(self, *a, **kw):
        return self.service.evreactor.fireEvent(*a, **kw)

    def load(self, tid):
        if self.playing:
            self.session.play(0)
        link = Link.from_string(tid)
        track = link.as_track()
        self.session.load(track)

    def play(self, consumer=None):
        self.playing = True
        self.session.play(1)
        if consumer is not None:
            self.consumer = consumer
            consumer.registerProducer(self, True)

    def search(self, query,  **kw):
        def cb(results, userdata):
            r = SpotifySearchResults(results)
            reactor.callFromThread(self.fireEvent, r)
        self.session.search(query.encode("utf-8"), cb, **kw)

    ### Callbacks from Spotify

    def logged_in(self, session, error):
        """ We have successfully logged in to spotify. This is the place we
        generally acquire the container for all the playlists from the
        session. """
        try:
            self.session = session
            self.ctr = session.playlist_container()
            reactor.callFromThread(self.fireEvent, SpotifyEventWithError(error), ISpotifyLoggedInEvent)
        except:
            traceback.print_exc()

    def logged_out(self, session, error):
        """ We have been logged out """
        try:
            reactor.callFromThread(self.fireEvent, SpotifyEventWithError(error), ISpotifyLoggedOutEvent)
        except:
            traceback.print_exc()


    def metadata_updated(self, sess):
        try:
            reactor.callFromThread(self.fireEvent, SpotifyEvent(), ISpotifyMetadataUpdatedEvent)
        except:
            traceback.print_exc()

    def connection_error(self, sess, error):
        try:
            reactor.callFromThread(self.fireEvent, SpotifyEventWithError(error), ISpotifyConnectionErrorEvent)
        except:
            traceback.print_exc()


    def message_to_user(self, sess, message):
        try:
            reactor.callFromThread(self.fireEvent, SpotifyEventWithMessage(message[:]), ISpotifyMessageToUserEvent)
        except:
            traceback.print_exc()


    def music_delivery(self, session, frames, frame_size, num_frames, sample_type, sample_rate, channels):
        try:
            frames = frames[:] # copy the frame data out, because it will be free()ed when this function returns
            reactor.callFromThread(self.consumer.write, frames)
        except:
            traceback.print_exc()

    def play_token_lost(self, sess):
        try:
            reactor.callFromThread(self.fireEvent, SpotifyEvent(), ISpotifyPlayTokenLostEvent)
        except:
            traceback.print_exc()

    def log_message(self, sess, data):
        try:
            reactor.callFromThread(self.fireEvent, SpotifyEventWithMessage(data[:]), ISpotifyLogMessageEvent)
        except:
            traceback.print_exc()

    def end_of_track(self, sess):
        try:
            reactor.callFromThread(self.fireEvent, SpotifyEvent(), ISpotifyEndOfTrackEvent)
            reactor.callFromThread(self.consumer.unregisterProducer)
        except:
            traceback.print_exc()

    ### IProducer interface

    def stopProducing(self):
        self.playing = False
        self.consumer = None

    def resumeProducing(self):
        self.playing = True

    def pauseProducing(self):
        self.playing = False

class Spotify(Item, service.Service):

    implements(isqueal.ISpotify, isqueal.ITrackSource)
    powerupInterfaces = (isqueal.ISpotify, isqueal.ITrackSource, isqueal.IMusicSource)

    namespace = 'spotify'
    username = text()
    password = text()
    running = inmemory()
    name = 'spotify'
    parent = inmemory()
    mgr = inmemory()
    playing = inmemory()

    label = "Spotify"

    def __init__(self, config, store):
        username = unicode(config.get("Spotify", "username"))
        password = unicode(config.get("Spotify", "password"))
        Item.__init__(self, store=store, username=username, password=password)

    def __repr__(self):
        return "Spotify(username=%r, password=SECRET, storeID=%r)" % (self.username, self.storeID)

    @property
    def evreactor(self):
        return self.store.findFirst(EventReactor)

    def activate(self):
        self.playing = None
        self.evreactor.subscribe(self.playerState, isqueal.IPlayerStateChange)

    def startService(self):
        self.mgr = SpotifyManager(self)
        reactor.callInThread(self.mgr.connect)
        return service.Service.startService(self)

    def play(self, tid):
        log.msg("Play called with %r" % tid, system="squeal.spot.service.Spotify")
        t = SpotifyTrack(tid)
        for p in self.store.powerupsFor(ISlimPlayerService):
            p.play(t)

    def registerConsumer(self, consumer, tid):
        log.msg("registering consumer %r on %r" % (consumer, self), system="squeal.spot.service.Spotify")
        self.playing = tid
        self.mgr.load(tid)
        self.mgr.play(consumer)

    def playlists(self):
        for id, p in enumerate(self.mgr.ctr):
            name = p.name() if p.is_loaded() else '-- Loading --'
            if self.playing and self.playing[0] == id:
                status = 'Playing'
            else:
                status = ''
            yield SpotifyPlaylist(id, status, name)

    def playerState(self, ev):
        """ We listen for state changes on the player. If it's ready for the
        next track then we initiate playing. """
        if ev.state == ev.State.READY:
            self.play(self.playing[0], self.playing[1] + 1)

    def search(self, query):
        self.mgr.search(query)

    def getTrackByLink(self, link):
        l = Link.from_string(link)
        return l.as_track()

    #isqueal.TrackSource
    def getTrackByID(self, tid):
        return SpotifyTrack(tid)

    def main_widget(self):
        return web.Main()


