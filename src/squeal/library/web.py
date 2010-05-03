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

""" Web interface for on-disk music library """

__author__ = "Doug Winter <doug.winter@isotoma.com>"
__docformat__ = "restructuredtext en"

from twisted.python.util import sibpath
from twisted.python import log

from nevow import page
from nevow import loaders
from nevow import tags as T
from nevow import athena

from squeal.web import base
from squeal import isqueal

import record
import ilibrary

template_dir = sibpath(__file__, 'templates')

def xmltemplate(s):
    return base.xmltemplate(s, template_dir)

class LibraryElement(base.BaseElement):
    @property
    def library(self):
        for library in self.store.powerupsFor(ilibrary.ILibrary):
            return library

class Artist(page.Element):
    docFactory = loaders.stan(
        T.li(class_="playable", render=T.directive("link")))

    def __init__(self, original):
        self.original = original

    @page.renderer
    def link(self, request, tag):
        return tag[
            T.a(href="#", id="artist-%s" % self.original.storeID)[
                self.original.name
            ]]

class Album(page.Element):
    docFactory = loaders.stan(
        T.li(class_="playable", render=T.directive("link")))

    def __init__(self, original):
        self.original = original

    @page.renderer
    def link(self, request, tag):
        return tag[
            T.a(href="#", id="album-%s" % self.original.storeID)[self.original.name],
        ]

class Track(page.Element):
    docFactory = loaders.stan(
        T.li(class_="playable", render=T.directive("link")))

    def __init__(self, original):
        self.original = original

    @page.renderer
    def link(self, request, tag):
        return tag[
            T.a(href="#", id="track-%s" % self.original.storeID)[self.original.title],
        ]

class Artists(LibraryElement):
    jsClass = u"Library.Artists"
    docFactory = xmltemplate("artists.html")

    @page.renderer
    def artists(self, request, tag):
        def _(request, tag):
            for a in self.library.artists():
                yield Artist(a)
        return tag[_]

class Albums(LibraryElement):
    jsClass = u"Library.Albums"
    docFactory = xmltemplate("albums.html")

    @page.renderer
    def albums(self, request, tag):
        def _(request, tag):
            for a in self.library.albums():
                yield Album(a)
        return tag[_]

class Tracks(LibraryElement):
    jsClass = u"Library.Tracks"
    docFactory = xmltemplate("tracks.html")

    @page.renderer
    def tracks(self, request, tag):
        def _(request, tag):
            for t in self.library.tracks():
                yield Track(t)
        return tag[_]

class Main(base.BaseElementContainer):
    jsClass = u"Library.Main"
    docFactory = xmltemplate("main.html")

    contained = {
        'artists': Artists,
        'albums': Albums,
        'tracks': Tracks,
    }

    @property
    def library(self):
        for library in self.store.powerupsFor(ilibrary.ILibrary):
            return library

    @property
    def playlist_service(self):
        for queue in self.store.powerupsFor(isqueal.IPlaylist):
            return queue

    @athena.expose
    def load_album(self, aid):
        album = self.store.getItemByID(int(aid))
        for track in self.store.query(record.Track,
                                      record.Track.album==album,
                                      sort=record.Track.track.ascending):

            self.playlist_service.enqueue(track)

    @page.renderer
    def artist_count(self, request, tag):
        return "[%d]" % self.library.artists().count()

    @page.renderer
    def album_count(self, request, tag):
        return "[%d]" % self.library.albums().count()

    @page.renderer
    def track_count(self, request, tag):
        return "[%d]" % self.library.tracks().count()


    @athena.expose
    def play(self, itemID):
        log.msg("Playing %s" % itemID, system="squeal.library.web.Main")

    @athena.expose
    def append(self, itemID):
        log.msg("Appending %s" % itemID, system="squeal.library.web.Main")
