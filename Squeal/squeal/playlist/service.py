from zope.interface import Interface, implements
from twisted.python.components import registerAdapter, Adapter
from twisted.application import service
from axiom.item import Item
from axiom.attributes import reference, inmemory, text, integer, timestamp

from squeal.event import EventReactor
from squeal.isqueal import *

class PlayTrack(Item):

    position = integer(default=0)
    track = reference()
    added = timestamp()

class PlayTrackJSON(Adapter):
    implements(IJSON)

    def json(self):
        track = IJSON(self.original.track).json()
        track[u'id'] = self.original.storeID
        track[u'pos'] = self.original.position
        track[u'added'] = self.original.added
        return track

registerAdapter(PlayTrackJSON, PlayTrack, IJSON)

class PlaylistChangeEvent(object):

    implements(IPlaylistChangeEvent)

    def __init__(self, added=(), removed=(), changed=(), playing=None):
        self.added = added
        self.removed = removed
        self.changed = changed
        self.playing = playing

class Playlist(Item, service.Service):
    implements(IPlaylist)
    powerupInterfaces = (IPlaylist,)

    position = integer(default=0)
    maxposition = integer(default=0)
    running = inmemory()
    name = inmemory()
    parent = inmemory()

    def __init__(self, config, store):
        Item.__init__(self, store=store)

    @property
    def evreactor(self):
        return self.store.findFirst(EventReactor)

    def activate(self):
        self.evreactor.subscribe(self.playerState, IPlayerStateChange)

    def playerState(self, ev):
        if ev.state == ev.State.ESTABLISHED:
            #self.play()
            self.clear()

    def clear(self):
        for p in self.store.query(PlayTrack):
            p.deleteFromStore()

    def reset(self):
        for p in self.store.query(PlayTrack, sort=PlayTrack.position.ascending):
            self.position = p.position
            self.play()
            break
        else:
            self.position = 0
            self.maxposition = 0

    def play(self):
        for p in self.store.query(PlayTrack, PlayTrack.position == self.position):
            self.load(p)
            break
        else:
            self.reset()

    def stop(self):
        for p in self.store.powerupsFor(ISlimPlayerService):
            p.stop()

    def __iter__(self):
        return iter(self.store.query(PlayTrack, sort=PlayTrack.position.ascending))

    def load(self, playtrack):
        for p in self.store.powerupsFor(ISlimPlayerService):
            p.play(playtrack.track)
            self.position += 1
        for r in self.store.powerupsFor(IEventReactor):
            r.fireEvent(PlaylistChangeEvent(playing=[playtrack]))

    def enqueue(self, track):
        pt = PlayTrack(store=self.store, position=self.maxposition, track=track)
        for r in self.store.powerupsFor(IEventReactor):
            r.fireEvent(PlaylistChangeEvent(added=[pt]))
        self.maxposition += 1
        if self.position == 0 and self.maxposition == 1:
            self.play()

