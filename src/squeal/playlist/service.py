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

""" Playlist management for squeal. Manages a persistent queue of tracks, and
schedules the for playing as appropriate. """

__author__ = "Doug Winter <doug.winter@isotoma.com>"
__docformat__ = "restructuredtext en"
__version__ = "$Revision$"[11:-2]

from zope.interface import Interface, implements
from twisted.python.components import registerAdapter, Adapter
from twisted.application import service
from twisted.python import log
from axiom.item import Item
from axiom.attributes import reference, inmemory, text, integer, timestamp

from squeal.event import EventReactor
from squeal.isqueal import *
from squeal.adaptivejson import IJsonAdapter
from squeal import adapters

class PlayTrack(Item):

    """ A track that is queued to play. The track identifier is known to the
    provider, and the provider will deliver a Track object on request. """

    position = integer(default=0)
    added = timestamp()
    tid = text()
    provider = reference()

    def player_uri(self):
        """ Return the URL of the track on the player """
        return "/play?id=%s" % self.storeID

    @property
    def track(self):
        return self.provider.get_track(self.tid)

class PlayTrackJSON(Adapter):
    def encode(self):
        encoded = IJsonAdapter(ITrack(self.original.track)).encode()
        encoded.update({
            u'position': self.original.position,
            u'added': self.original.added,
            u'tid': unicode(self.original.tid),
        })
        return encoded

registerAdapter(PlayTrackJSON, PlayTrack, IJsonAdapter)

class PlaylistChangeEvent(object):

    implements(IPlaylistChangeEvent)

    def __init__(self, added=(), removed=(), changed=(), playing=None):
        self.added = added
        self.removed = removed
        self.changed = changed
        self.playing = playing

class Playlist(Item, service.Service):

    """ The service that hosts the list of tracks queued up to play on the
    players. Right now there may only be one of these, and if there is more
    than one player they are assumed to be synchronised. """

    implements(IPlaylist)
    powerupInterfaces = (IPlaylist,)

    playing = inmemory()
    current = integer(default=-1) # currently playing
    maxposition = integer(default=0) # the highest track number
    running = inmemory()
    name = inmemory()
    parent = inmemory()

    @property
    def evreactor(self):
        return self.store.findFirst(EventReactor)

    def activate(self):
        self.playing = False
        self.evreactor.subscribe(self.playerState, IPlayerStateChange)
        self.evreactor.subscribe(self.buttonPressed, IRemoteButtonPressedEvent)

    def playerState(self, ev):
        """ Called by the event system in response to player state change events. """
        if ev.state == ev.State.ESTABLISHED: # just connected
            self.play()
        elif ev.state == ev.State.READY: # finished playing previous track
            self.play()

    def buttonPressed(self, ev):
        if ev.button == 'play' and not self.playing:
            self.play()

    def clear(self):
        log.msg("Clear", system="squeal.playlist.service.Playlist")
        for p in self.store.query(PlayTrack):
            p.deleteFromStore()
        self.maxposition = 0
        self.current = -1

    def play(self):
        log.msg("Playing", system="squeal.playlist.service.Playlist")
        for p in self.store.query(PlayTrack, PlayTrack.position == self.current + 1):
            self.load(p)
            break
        else:
            log.msg("No PlayTracks found",  system="squeal.playlist.service.Playlist")

    def stop(self):
        for p in self.store.powerupsFor(ISlimPlayerService):
            p.stop()
        self.playing = False

    def __iter__(self):
        return iter(self.store.query(PlayTrack, sort=PlayTrack.position.ascending))

    def get_current_track(self):
        for p in self.store.query(PlayTrack, PlayTrack.position == self.current):
            return p.track

    def load(self, playtrack):
        """ Load the specified track on the player. """
        log.msg("Loading %r" % playtrack.track, system="squeal.playlist.service.Playlist")
        for p in self.store.powerupsFor(ISlimPlayerService):
            log.msg("Slim player service located")
            if p.players:
                p.play(playtrack.track)
                self.current = playtrack.position
                self.playing = True
            else:
                log.msg("Not playing - no players connected", system="squeal.playlist.service.Playlist")
        for r in self.store.powerupsFor(IEventReactor):
            r.fireEvent(PlaylistChangeEvent(playing=[playtrack]))

    def enqueue(self, *tracks):
        """ Add a track to the end of the queue. Track must be conformable to
        ITrack. """
        pt = []
        for track in tracks:
            track = ITrack(track)
            log.msg("enqueing %r at %d" % (track.track_id, self.maxposition), system="squeal.playlist.service.Playlist")
            pt.append(PlayTrack(store=self.store, position=self.maxposition, tid=track.track_id, provider=track.provider))
            self.maxposition += 1
        for r in self.store.powerupsFor(IEventReactor):
            r.fireEvent(PlaylistChangeEvent(added=pt))

    def playfirst(self, *tracks):
        """ Replace the currently playing track with this new one, but keep
        the rest of the queue the same """
        pt = []
        for current in self.store.query(PlayTrack, PlayTrack.position==self.current):
            current.delete()
        # bump existing tracks up the queue
        for existing in self.store.query(PlayTrack, PlayTrack.position > self.current):
            existing.position += len(tracks)
        for i, track in enumerate(tracks):
            track = ITrack(track)
            log.msg("enqueing %r first at %d" % (track.track_id, self.maxposition), system="squeal.playlist.service.Playlist")
            pt.append(PlayTrack(store=self.store, position=self.current + i, tid=track.track_id, provider=track.provider))
        self.load(pt[0])
        for r in self.store.powerupsFor(IEventReactor):
            r.fireEvent(PlaylistChangeEvent(added=pt))

