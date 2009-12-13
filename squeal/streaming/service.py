
from zope.interface import Interface, implements
from twisted.python.components import registerAdapter, Adapter
from twisted.application import service
from twisted.internet import reactor
from twisted.internet.interfaces import *
from axiom.item import Item
from axiom.attributes import reference, inmemory, text, integer, timestamp

import traceback

from squeal.event import EventReactor
from squeal.isqueal import *

from spotify.manager import SpotifySessionManager

class ISpotifyEvent(Interface):
    """ Any spotify event """

class ISpotifyLoggedInEvent(ISpotifyEvent):
    """ We have logged into spotify successfully. """

class ISpotifyLoggedOutEvent(ISpotifyEvent):
    """ We have been logged out of spotify """

    error = Attribute("""The error that caused us to be logged out. """)

class ISpotifyMetadataUpdatedEvent(ISpotifyEvent):
    """ Spotify metadata has been updated. """

class ISpotifyConnectionErrorEvent(ISpotifyEvent):
    """ Connection error """

class ISpotifyMessageToUserEvent(ISpotifyEvent):
    """ Message specifically to the user (for example, invites available) """

class ISpotifyLogMessageEvent(ISpotifyEvent):
    """ Log message, for operator consumption not for the user """

class ISpotifyEndOfTrackEvent(ISpotifyEvent):
    """ The track has been completed.  Will happen long before it finishes playing normally. """

class ISpotifyPlayTokenLostEvent(ISpotifyEvent):
    """ Play token has been lost """

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

class SpotifyTransfer(object):

    """ Implements the streaming interface between spotify and a web request. """

    implements(IConsumer, IProducer, IPushProducer)

    request = None

    def __init__(self, playlist, track, service, request):
        print "Initiating transfer"
        self.playlist = playlist
        self.track = track
        self.request = request
        self.service = service
        self.data = []
        self.paused = False
        self.finished = False
        request.registerProducer(self, 1)
        self.service.registerConsumer(self, playlist, track)

    def resumeProducing(self):
        if not self.request:
            return
        if self.data:
            for x in self.data:
                self.request.write(x)
            self.data = []
        if self.finished:
            self.request.unregisterProducer()
            self.request.finish()
            self.request = None
        self.paused = False

    def pauseProducing(self):
        self.paused = True
        pass

    def stopProducing(self):
        self.producer.stopProducing()
        self.request = None

    def write(self, data):
        """ Called by spotify to queue data to send to the squeezebox  """

        if not self.request:
            print "overrun: writing to a closed request"
            return
        if self.paused:
            self.data.append(data)
        else:
            self.request.write(data)

    def registerProducer(self, producer, streaming):
        self.producer = producer

    def unregisterProducer(self):
        self.request.unregisterProducer()
        self.request.finish()
        self.producer = None
        self.request = None

class SpotifyTrack(object):

    playlist = 1
    track = 1
    type = 3
    title = 'unknown'
    artist = 'unknown'

    def __init__(self, playlist, track):
        self.playlist = playlist
        self.track = track

    def player_url(self):
        return "/spotify?playlist=%s&track=%s" % (self.playlist, self.track)

class SpotifyPlaylist(object):

    id = None
    name = None

    def __init__(self, id, status, name):
        self.id = id
        self.status = status
        self.name = name

class SpotifyPlaylistJSON(Adapter):
    implements(IJSON)

    def json(self):
        t = self.original
        return {
            u'id': t.id,
            u'status': unicode(t.status, 'utf-8'),
            u'name': unicode(t.name, 'utf-8'),
        }

registerAdapter(SpotifyPlaylistJSON, SpotifyPlaylist, IJSON)

class SpotifyManager(SpotifySessionManager):

    implements(IPushProducer, IProducer)

    def __init__(self, service):
        self.service = service
        SpotifySessionManager.__init__(self, service.username, service.password)
        self.ctr = None
        self.playing = False
        print "Connecting as %s" % service.username

    def fireEvent(self, *a, **kw):
        return self.service.evreactor.fireEvent(*a, **kw)

    def load(self, playlist, track):
        if self.playing:
            self.session.play(0)
        self.session.load(self.ctr[playlist][track])

    def play(self, consumer=None):
        self.playing = True
        self.session.play(1)
        if consumer is not None:
            self.consumer = consumer
            consumer.registerProducer(self, True)

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
    implements(ISpotify)
    powerupInterfaces = (ISpotify,)

    username = text()
    password = text()
    running = inmemory()
    name = inmemory()
    parent = inmemory()
    mgr = inmemory()
    playing = inmemory()

    def __init__(self, config, store):
        username = unicode(config.get("Spotify", "username"))
        password = unicode(config.get("Spotify", "password"))
        Item.__init__(self, store=store, username=username, password=password)

    @property
    def evreactor(self):
        return self.store.findFirst(EventReactor)

    def activate(self):
        self.playing = None
        self.evreactor.subscribe(self.playerState, IPlayerStateChange)

    def startService(self):
        self.mgr = SpotifyManager(self)
        reactor.callInThread(self.mgr.connect)
        return service.Service.startService(self)

    def play(self, playlist, track=0):
        t = SpotifyTrack(playlist=playlist, track=track)
        for p in self.store.powerupsFor(ISlimPlayerService):
            p.play(t)

    def registerConsumer(self, consumer, playlist, track):
        self.playing = (playlist, track)
        self.mgr.load(playlist, track)
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
            print "Loading", self.playing[0], self.playing[1] + 1
            self.play(self.playing[0], self.playing[1] + 1)
