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
from squeal.adaptivejson import IJsonAdapter
from squeal import adapters, isqueal

import time

class PlayTrack(Item):

    """ A track that is queued to play. The track identifier is known to the
    provider, and the provider will deliver a Track object on request. """

    implements(isqueal.ITrack)

    position = integer(default=0)
    added = timestamp()
    tid = text()
    provider = reference()

    @property
    def track(self):
        # caching this locally in memory may or may not be a good idea
        return isqueal.ITrack(self.provider.get_track(self.tid))

    # these are the ITrack interface. __getattr__ does weird shit with Axiom,
    # so I opted for simple-but-lots-of-typing

    @property
    def track_type(self):
        return self.track.track_type

    @property
    def track_id(self):
        return self.tid

    @property
    def is_loaded(self):
        return self.track.is_loaded

    @property
    def title(self):
        return self.track.title

    @property
    def artist(self):
        return self.track.artist

    @property
    def album(self):
        return self.track.album

    @property
    def duration(self):
        return self.track.duration

    @property
    def image_uri(self):
        return self.track.image_uri

    def player_uri(self, player_id):
        return self.track.player_uri(player_id)


class PlayTrackJSON(Adapter):
    def encode(self):
        encoded = IJsonAdapter(isqueal.ITrack(self.original.track)).encode()
        encoded.update({
            u'position': self.original.position,
            u'added': self.original.added,
            u'tid': unicode(self.original.tid),
        })
        return encoded

registerAdapter(PlayTrackJSON, PlayTrack, IJsonAdapter)

class PlaylistChangeEvent(object):

    implements(isqueal.IPlaylistChangeEvent)

    def __init__(self, added=(), removed=(), changed=(), playing=None):
        self.added = added
        self.removed = removed
        self.changed = changed
        self.playing = playing

class Playlist(Item, service.Service):

    """ The service that hosts the list of tracks queued up to play on the
    players. Right now there may only be one of these, and if there is more
    than one player they are assumed to be synchronised. """

    implements(isqueal.IPlaylist)
    powerupInterfaces = (isqueal.IPlaylist,)

    playing = inmemory()
    current = integer(default=-1) # currently playing
    maxposition = integer(default=0) # the highest track number
    running = inmemory()
    name = inmemory()
    parent = inmemory()
    previous_playtime = inmemory()
    last_started = inmemory()

    def time_played(self):
        if self.playing:
            return (self.previous_playtime + time.time() - self.last_started) * 1000
        else:
            return self.previous_playtime * 1000

    @property
    def evreactor(self):
        return self.store.findFirst(EventReactor)

    def activate(self):
        self.playing = False
        self.previous_playtime = 0
        self.last_started = 0
        #self.evreactor.subscribe(self.playerState, isqueal.IPlayerStateChange)
        self.evreactor.subscribe(self.buttonPressed, isqueal.IRemoteButtonPressedEvent)

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
        if self.previous_playtime != 0:
            # we're paused
            for p in self.store.powerupsFor(isqueal.ISlimPlayerService):
                p.unpause()
            self.last_started = time.time()
        else:
            for p in self.store.query(PlayTrack, PlayTrack.position == self.current + 1):
                self.load(p)
                self.previous_playtime = 0
                self.last_started = time.time()
                break
            else:
                log.msg("No PlayTracks found",  system="squeal.playlist.service.Playlist")

    def pause(self):
        for p in self.store.powerupsFor(isqueal.ISlimPlayerService):
            p.pause()
        self.playing = False
        self.previous_playtime += time.time() - self.last_started
        self.last_started = 0

    def stop(self):
        for p in self.store.powerupsFor(isqueal.ISlimPlayerService):
            p.stop()
        self.playing = False
        self.previous_playtime = 0
        self.last_started = 0

    def __iter__(self):
        return iter(self.store.query(PlayTrack, sort=PlayTrack.position.ascending))

    def get_current_track(self):
        for p in self.store.query(PlayTrack, PlayTrack.position == self.current):
            return p

    def load(self, playtrack):
        """ Load the specified track on the player. """
        connected = 0
        log.msg("Loading %r" % playtrack.track, system="squeal.playlist.service.Playlist")
        for p in self.store.powerupsFor(isqueal.IPlayMusic):
            connected += p.play(playtrack.track)
        if connected != 0:
            self.current = playtrack.position
            self.playing = True
        else:
            log.msg("Not playing - no players connected", system="squeal.playlist.service.Playlist")
        for r in self.store.powerupsFor(isqueal.IEventReactor):
            r.fireEvent(PlaylistChangeEvent(playing=[playtrack]))

    def enqueue(self, *tracks):
        """ Add a track to the end of the queue. Track must be conformable to
        ITrack. """
        pt = []
        for track in tracks:
            track = isqueal.ITrack(track)
            log.msg("enqueing %r at %d" % (track.track_id, self.maxposition), system="squeal.playlist.service.Playlist")
            pt.append(PlayTrack(store=self.store, position=self.maxposition, tid=track.track_id, provider=track.provider))
            self.maxposition += 1
        for r in self.store.powerupsFor(isqueal.IEventReactor):
            r.fireEvent(PlaylistChangeEvent(added=pt))

    def playfirst(self, *tracks):
        """ Replace the currently playing track with this new one, but keep
        the rest of the queue the same """
        pt = []
        for current in self.store.query(PlayTrack, PlayTrack.position==self.current):
            current.deleteFromStore()
        # bump existing tracks up the queue
        for existing in self.store.query(PlayTrack, PlayTrack.position > self.current):
            existing.position += len(tracks)
        for i, track in enumerate(tracks):
            track = isqueal.ITrack(track)
            log.msg("enqueing %r first at %d" % (track.track_id, self.maxposition), system="squeal.playlist.service.Playlist")
            pt.append(PlayTrack(store=self.store, position=self.current + i, tid=track.track_id, provider=track.provider))
        self.maxposition += len(tracks)
        self.load(pt[0])
        for r in self.store.powerupsFor(isqueal.IEventReactor):
            r.fireEvent(PlaylistChangeEvent(added=pt))

