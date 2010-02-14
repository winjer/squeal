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
from twisted.internet import defer
from axiom.item import Item
from axiom.attributes import reference, inmemory, text, integer, timestamp

import traceback

from squeal.event import EventReactor
from squeal import isqueal
from squeal.adaptivejson import IJsonAdapter
import sys
import urllib
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

    """ A wrapper for spotify.Track that conforms to ITrack. Generally you'd
    get this from the spotify service's get_track method. """

    implements(isqueal.ITrack)

    # all spotify tracks are played as raw PCM
    type = 3

    def __init__(self, provider, track):
        self.provider = provider
        self.track = track

    @property
    def track_id(self):
        """ Return the id of the track within the provider namespace. """
        return unicode(Link.from_track(self.track, 0))

    @property
    def is_loaded(self):
        return self.track.is_loaded()

    @property
    def title(self):
        return self.track.name().decode("utf-8")

    @property
    def artist(self):
        artists = self.track.artists()
        return ",".join(x.name().decode("utf-8") for x in artists)

    @property
    def album(self):
        return self.track.album().name().decode("utf-8")

    def image_uri(self):
        return "/spotify_image?%s" % (urllib.urlencode({"image": self.track.image_id()}))

    def player_uri(self):
        return "/spotify?tid=%s" % self.track_id

class PlaylistJSON(Adapter):
    implements(IJsonAdapter)

    def encode(self):
        t = self.original
        return {
            u'id': unicode(Link.from_playlist(t)),
            u'status': "",
            u'name': unicode(t.name(), 'utf-8'),
        }

registerAdapter(PlaylistJSON, spotify.Playlist, IJsonAdapter)

class SpotifyTrackJSON(Adapter):
    implements(IJsonAdapter)
    def encode(self):
        return {
            u'name': unicode(self.original.name(), 'utf-8'),
            u'isLoaded': self.original.is_loaded(),
        }

class TrackJSON(Adapter):
    implements(IJsonAdapter)
    def encode(self):
        return {
            u'name': self.original.title,
            u'isLoaded': self.original.is_loaded,
        }

registerAdapter(SpotifyTrackJSON, spotify.Track, IJsonAdapter)
registerAdapter(TrackJSON, SpotifyTrack, IJsonAdapter)

class SpotifyManager(SpotifySessionManager):

    """ Only the Spotify service talks to the Manager directly. The Manager is
    running in it's own thread, so be careful. """

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
        log.msg("load %r" % tid, system="squeal.spot.service.SpotifyManager")
        if self.playing:
            self.session.play(0)
        link = Link.from_string(tid)
        track = link.as_track()
        self.session.load(track)

    def play(self, consumer=None):
        log.msg("play", system="squeal.spot.service.SpotifyManager")
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

    def image(self, image_id):
        assert len(image_id) == 20
        d = defer.Deferred()
        def cb(image, userdata):
            reactor.callFromThread(d.callback, image)
        image = self.session.image_create(image_id)
        image.add_load_callback(cb, None)
        return d

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
            if self.consumer is None:
                return 0
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
            log.msg(data.encode("utf-8").strip(), system="Spotify")
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
        log.msg("stopProducing", system="squeal.spot.service.SpotifyManager")
        self.session.play(0)
        self.playing = False
        self.consumer = None

    def resumeProducing(self):
        log.msg("resumeProducing", system="squeal.spot.service.SpotifyManager")
        self.session.play(1)
        self.playing = True

    def pauseProducing(self):
        log.msg("pauseProducing", system="squeal.spot.service.SpotifyManager")
        self.session.play(0)
        self.playing = False

class Spotify(Item, service.Service):

    """ The spotify service. Provides an interface to the rest of the system
    for the spotify session and related machinery. """

    implements(ISpotifyService, isqueal.ITrackSource)
    powerupInterfaces = (ISpotifyService, isqueal.ITrackSource, isqueal.IMusicSource)

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

    def startService(self):
        self.mgr = SpotifyManager(self)
        reactor.callInThread(self.mgr.connect)
        return service.Service.startService(self)

    def play(self, tid):
        log.msg("Play called with %r" % tid, system="squeal.spot.service.Spotify")
        track = self.get_track(tid)
        for p in self.store.powerupsFor(ISlimPlayerService):
            p.play(track)

    def registerConsumer(self, consumer, tid):
        log.msg("registering consumer %r on %r" % (consumer, self), system="squeal.spot.service.Spotify")
        self.playing = tid
        self.mgr.load(tid)
        self.mgr.play(consumer)

    def playlists(self):
        return self.mgr.ctr

    def image(self, image_id):
        return self.mgr.image(image_id)

    def search(self, query):
        self.mgr.search(query)

    def getTrackByLink(self, link):
        l = Link.from_string(link)
        return l.as_track()

    def main_widget(self):
        return web.Main()

    #isqueal.TrackSource

    def get_track(self, tid):
        track = Link.from_string(tid).as_track()
        return SpotifyTrack(self, track)

