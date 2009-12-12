
from zope.interface import Interface, implements
from twisted.python.components import registerAdapter, Adapter
from twisted.application import service
from twisted.internet import reactor
from twisted.internet.interfaces import *
from axiom.item import Item
from axiom.attributes import reference, inmemory, text, integer, timestamp

from squeal.event import EventReactor
from squeal.isqueal import *

from spotify.manager import SpotifySessionManager

class SpotifyTransfer(object):

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

        if self.paused:
            self.data.append(data)
        else:
            self.request.write(data)

    def registerProducer(self, producer, streaming):
        self.producer = producer

    def unregisterProducer(self):
        self.producer = None
        self.request = None

class SpotifyTrack(object):

    playlist = 1
    track = 1
    type = 3
    title = 'unknown'
    artist = 'unknown'

    def player_url(self):
        return "/spotify?playlist=%s&track=%s" % (self.playlist, self.track)

class SpotifyManager(SpotifySessionManager):

    implements(IPushProducer, IProducer)

    def __init__(self, service):
        self.service = service
        SpotifySessionManager.__init__(self, service.username, service.password)
        self.ctr = None
        self.playing = False
        print "Connecting as %s" % service.username

    def logged_in(self, session, error):
        self.session = session
        try:
            self.ctr = session.playlist_container()
            print "Got Container"
        except:
            traceback.print_exc()

    def load(self, playlist, track):
        if self.playing:
            self.session.play(0)
        self.session.load(self.ctr[playlist][track])
        #print "Loading %s from %s" % (unicode(self.ctr[playlist][track].name(), 'utf-8'), unicode(self.ctr[playlist].name(), 'utf-8'))

    def play(self, consumer):
        self.playing = True
        self.session.play(1)
        self.consumer = consumer
        consumer.registerProducer(self, True)

    def music_delivery(self, session, frames, frame_size, num_frames, sample_type, sample_rate, channels):
        # copy the frame data out, because it will be free()ed when this function returns
        frames = frames[:]
        reactor.callFromThread(self.consumer.write, frames)

    def log_message(self, sess, data):
        print data

    def stopProducing(self):
        self.playing = False
        self.session.play(0)
        self.consumer = None

    def resumeProducing(self):
        self.playing = True
        self.session.play(1)

    def pauseProducing(self):
        self.playing = False
        self.session.play(0)

class Spotify(Item, service.Service):
    implements(ISpotify)
    powerupInterfaces = (ISpotify,)

    username = text()
    password = text()
    running = inmemory()
    name = inmemory()
    parent = inmemory()
    mgr = inmemory()

    def __init__(self, config, store):
        username = unicode(config.get("Spotify", "username"))
        password = unicode(config.get("Spotify", "password"))
        Item.__init__(self, store=store, username=username, password=password)

    def startService(self):
        self.mgr = SpotifyManager(self)
        reactor.callInThread(self.mgr.connect)
        return service.Service.startService(self)

    def play(self):
        track = SpotifyTrack()
        for p in self.store.powerupsFor(ISlimPlayerService):
            p.play(track)

    def registerConsumer(self, consumer, playlist, track):
        self.mgr.load(playlist, track)
        self.mgr.play(consumer)

