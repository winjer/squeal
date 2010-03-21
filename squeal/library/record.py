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

""" Keeps records of what is in the local library. """

__author__ = "Doug Winter <doug.winter@isotoma.com>"
__docformat__ = "restructuredtext en"
__version__ = "$Revision$"[11:-2]


import os
import magic
import stat

from zope.interface import Interface, implements

from twisted.internet import reactor
from twisted.python.components import Adapter, registerAdapter
from twisted.python import log

from axiom.item import Item
from axiom.attributes import text, timestamp, path, reference, integer, AND
from epsilon.extime import Time

from squeal.isqueal import *
from squeal.adaptivejson import IJsonAdapter

from ilibrary import *

class LibraryChangeEvent(object):

    implements(ILibraryChangeEvent)

    def __init__(self, added=(), removed=(), changed=(), playing=None):
        self.added = added
        self.removed = removed
        self.changed = changed
        self.playing = playing

class Collection(Item):

    """ A collection of tracks in the library """

    implements(ICollection)

    pathname = text()
    last = timestamp()

    filetypes = {
        'ogg': 0,
        'mp3': 1,
        'flac': 2,
        'wav': 3
    }

    def update(self, pathname, ftype, details):
        for track in self.store.query(Track, Track.pathname == pathname):
            # we should make updating an option
            #track.update(details)
            break
        else:
            Track.create(self, pathname, ftype, details)

    @property
    def library(self):
        for l in self.store.powerupsFor(ILibrary):
            return l

    def scan(self):
        """ Loop through every file in the collection and update the metadata
        stored against the track from it's tags and/or name """
        log.msg("Scanning collection %s" % self.pathname, system="squeal.library.record.Collection")
        m = magic.open(magic.MAGIC_NONE)
        m.load()
        scanning = enumerate(os.walk(self.pathname))
        if self.last is not None:
            timestamp = self.last.asPOSIXTimestamp()
        policy = self.library.naming_policy
        def _process():
            try:
                i, (dirpath, dirnames, filenames) = scanning.next()
            except StopIteration:
                self.last = Time()
                return
            for f in filenames:
                pathname = os.path.join(dirpath, f)
                if self.last is not None:
                    if os.stat(pathname)[stat.ST_MTIME] < timestamp:
                        continue
                mtype = m.file(pathname.encode('utf-8')).lower()
                if 'ogg' in mtype:
                    mtype = 'ogg'
                elif 'flac' in mtype:
                    mtype = 'flac'
                elif 'mp3' in mtype:
                    mtype = 'mp3'
                elif 'wave' in mtype:
                    mtype = 'wav'
                else:
                    mtype = None
                log.msg("Found file %s of type %s" % (pathname, mtype), system="squeal.library.record.Collection")
                ftype = self.filetypes.get(mtype, None)
                details = policy.details(self, pathname)
                self.update(pathname, ftype, details)
            reactor.callLater(0, _process)
        reactor.callLater(0, _process)


class Artist(Item):
    name = text()

class Album(Item):
    name = text()
    artist = reference()


class Track(Item):

    collection = reference()
    artist = reference()
    album = reference()
    track = integer()
    type = integer()
    pathname = text()
    title = text()
    year = text()
    genre = text()

    @classmethod
    def create(self, collection, pathname, ftype, details):
        if details is None:
            return
        store = collection.store
        artist, album = self.dependencies(store, details)
        track = Track(store=store,
                     collection=collection,
                     artist=artist,
                     album=album,
                     track=details['track'],
                     type=ftype,
                     pathname=pathname,
                     title=details['title'],
                     year=details['year'],
                     genre=details['genre'],
                     )
        for r in track.store.powerupsFor(IEventReactor):
            r.fireEvent(LibraryChangeEvent(added=[track]))
        return track

    @classmethod
    def dependencies(self, store, details):
        if details['artist'] is not None:
            for artist in store.query(Artist, Artist.name == details['artist']):
                break
            else:
                artist = Artist(store=store, name=details['artist'])
            if details['album'] is not None:
                for album in store.query(Album,
                                         AND(Album.artist == artist,
                                         Album.name == details['album'])):
                    break
                else:
                    album = Album(store=store, artist=artist, name=details['album'])
            else:
                album = None
        else:
            artist = None
        return artist, album

    def update(self, details):
        artist, album = self.dependencies(self.store, details)
        self.artist = artist
        self.album = album
        self.track = details['track']
        self.title = details['title']
        self.year = details['year']
        self.genre = details['genre']



class TrackJSON(Adapter):

    implements(IJsonAdapter)

    def encode(self):
        t = self.original
        return {
            u'id': t.storeID,
            u'artist': t.artist.name,
            u'album': t.album.name,
            u'track': t.track,
            u'title': t.title
        }

registerAdapter(TrackJSON, Track, IJsonAdapter)

class TrackITrackAdapter(Adapter):
    implements(ITrack)

    @property
    def track_id(self):
        return unicode(self.original.storeID)

    @property
    def provider(self):
        for library in self.original.store.powerupsFor(ILibrary):
            return library

    @property
    def track_type(self):
        return self.original.type

    @property
    def is_loaded(self):
        return True

    @property
    def title(self):
        return self.original.title

    @property
    def artist(self):
        return self.original.artist.name

    @property
    def album(self):
        return self.original.album.name

registerAdapter(TrackITrackAdapter, Track, ITrack)


