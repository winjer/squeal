

import traceback
import os

from twisted.internet import reactor, defer
from twisted.internet.interfaces import IPushProducer, IProducer
from twisted.python import log
from twisted.python.util import sibpath

from spotify.manager import SpotifySessionManager
from spotify import Link

from ispotify import *
from event import *

class SpotifyManager(SpotifySessionManager):

    """ Only the Spotify service talks to the Manager directly. The Manager is
    running in it's own thread, so be careful. """

    implements(IPushProducer, IProducer)

    appkey_file = sibpath(__file__, 'appkey.key')

    def __init__(self, service):
        self.service = service
        self.cache_location = self.service.store.dbdir.child("temp").path
        SpotifySessionManager.__init__(self, service.username, service.password)
        self.ctr = None
        self.playing = False
        log.msg("Connecting as %s" % service.username, system="squeal.spot.service.SpotifyManager")

    def fireEvent(self, *a, **kw):
        return self.service.evreactor.fireEvent(*a, **kw)

    def load(self, track):
        """ Pass this a SpotifyTrack """
        log.msg("load %r" % track.track_id, system="squeal.spot.service.SpotifyManager")
        if self.playing:
            self.session.play(0)
        self.session.load(track.track)

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
        if 'SQUEAL_DEBUG' in os.environ:
            log.msg("stopProducing", system="squeal.spot.service.SpotifyManager")
        self.session.play(0)
        self.playing = False
        self.consumer = None

    def resumeProducing(self):
        if 'SQUEAL_DEBUG' in os.environ:
            log.msg("resumeProducing", system="squeal.spot.service.SpotifyManager")
        self.session.play(1)
        self.playing = True

    def pauseProducing(self):
        if 'SQUEAL_DEBUG' in os.environ:
            log.msg("pauseProducing", system="squeal.spot.service.SpotifyManager")
        self.session.play(0)
        self.playing = False

