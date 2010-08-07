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
from twisted.internet import defer
from twisted.python.components import Adapter, registerAdapter
from twisted.python import log

from axiom.item import Item
from axiom.attributes import text, timestamp, path, reference, integer, AND, inmemory
from epsilon.extime import Time

from squeal.isqueal import *
from squeal.adaptivejson import IJsonAdapter

from ilibrary import *

# we only need one magic database, and here it is
magicdb = magic.open(magic.MAGIC_NONE)
magicdb.load()

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

    # the pathname to the root of the collection
    pathname = text()
    # the date of the last update run
    last = timestamp()
    # number of files to process before yielding to the reactor loop
    files_per_loop = 20

    filetypes = {
        'ogg': 0,
        'mp3': 1,
        'flac': 2,
        'wav': 3
    }

    def update(self, pathname, ftype, details):
        """ Update a track in the database, based on it's filetype and the
        details we can extract from it's path or tags. """
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

    def _generate_changed_paths(self):
        """ Generator of all pathnames within this collection that have been
        created or updated since the collection was last updated. """
        for (dirpath, dirnames, filenames) in os.walk(self.pathname):
            for filename in filenames:
                pathname = os.path.join(dirpath, filename)
                if self.is_new_file(pathname):
                    yield pathname

    def file_type(self, pathname):
        """ Return our internal representation of the music file type for the
        file at pathname. """
        mtype = magicdb.file(pathname.encode('utf-8')).lower()
        if 'ogg' in mtype:
            mtype = 'ogg'
        elif 'flac' in mtype:
            mtype = 'flac'
        elif 'mp3' in mtype:
            mtype = 'mp3'
        elif 'mpeg' in mtype:
            mtype = 'mp3'
        elif 'audio file with id3' in mtype:
            mtype = 'mp3'
        elif 'wave' in mtype:
            mtype = 'wav'
        else:
            mtype = None
        log.msg("Found file %s of type %s" % (pathname, mtype), system="squeal.library.record.Collection")
        return self.filetypes.get(mtype, None)

    def is_new_file(self, pathname):
        """ Is this file newer than the last time the collection was scanned? """
        if self.last is not None:
            timestamp = self.last.asPOSIXTimestamp()
            if os.stat(pathname)[stat.ST_MTIME] < timestamp:
                return False
        return True

    def update_path(self, pathname):
        """ Update a database entry for a specified pathname. """
        ftype = self.file_type(pathname)
        if ftype is not None:
            details = self.library.naming_policy.details(self, pathname)
            self.update(pathname, ftype, details)

    def scan(self):
        """ Loop through every file in the collection and update the metadata
        stored against the track from it's tags and/or name """
        log.msg("Scanning collection %s" % self.pathname, system="squeal.library.record.Collection")
        for i, pathname in enumerate(self._generate_changed_paths()):
            self.update_path(pathname)
            if i % self.files_per_loop == 0:
                # allow other things to happen
                reactor.iterate()
        self.last = Time()


class Artist(Item):
    name = text()

    def tracks(self):
        """ This is how the web part knows which tracks to play when this item
        is selected """
        return self.store.query(Track,
                                AND(Track.artist==self, Track.album==Album.storeID),
                                sort=(Album.name.ascending, Track.track.ascending))

class Album(Item):
    name = text()
    artist = reference()

    def tracks(self):
        """ This is how the web part knows which tracks to play when this item
        is selected """
        return self.store.query(Track, Track.album==self, sort=Track.track.ascending)

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
    duration = integer() # milliseconds

    def tracks(self):
        """ This is how the web part knows which tracks to play when this item
        is selected """
        return [self]

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
                     duration=details['duration'],
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

    @property
    def image_uri(self):
        return u"/library/image?image=%s" % self.original.storeID

    def player_uri(self, player_id):
        return u"/library/stream?tid=%s&pid=%s" % (self.original.storeID, player_id)

    @property
    def duration(self):
        return self.original.duration

registerAdapter(TrackITrackAdapter, Track, ITrack)


