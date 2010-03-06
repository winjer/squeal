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

""" The spotify service and related classes """

__author__ = "Doug Winter <doug.winter@isotoma.com>"
__docformat__ = "restructuredtext en"
__version__ = "$Revision$"[11:-2]

from twisted.python.util import sibpath
from twisted.python import log

from nevow import inevow
from nevow import athena
from nevow import page
from nevow import tags as T
from nevow import loaders
from nevow import rend

from squeal import isqueal
from squeal.spot import ispotify
from squeal.web import ijukebox
from squeal.web import base
from squeal import adaptivejson

import ispotify

from spotify import Link
from sfy import SpotifyStreamer, SpotifyImage

template_dir = sibpath(__file__, 'templates')

def xmltemplate(s):
    return base.xmltemplate(s, template_dir)

class SearchEvent(object):
    def __init__(self, query):
        self.query = query

class Search(base.BaseElement):
    jsClass = u"Spot.Search"
    docFactory = xmltemplate("search.html")

    @athena.expose
    def search(self, query):
        e = self.evreactor
        spotify = self.store.powerupsFor(ispotify.ISpotifyService).next()
        e.fireEvent(SearchEvent(query), ijukebox.ISearchStartedEvent)
        spotify.search(query)

class Options(base.BaseElement):
    jsClass = u"Spot.Options"
    docFactory = xmltemplate("options.html")

class Playlist(page.Element):
    docFactory = loaders.stan(
        T.li(render=T.directive("link")))

    def __init__(self, original):
        self.original = original

    @page.renderer
    def link(self, request, tag):
        return tag[
            T.a(href="#", id="playlist-%s" % str(Link.from_playlist(self.original)))[self.original.name()]
        ]

class Playlists(base.BaseElement):
    jsClass = u"Spot.Playlists"
    docFactory = xmltemplate("playlists.html")

    @property
    def spotify_service(self):
        """ Return the one and only one spotify service running on the store """
        for spotify in self.store.powerupsFor(ispotify.ISpotifyService):
            return spotify

    @page.renderer
    def playlists(self, request, tag):
        def _(request, tag):
            for p in self.spotify_service.playlists():
                yield Playlist(p)
        return tag[_]

class Document(base.BaseElement):
    jsClass = u"Spot.Document"
    docFactory = xmltemplate("document.html")

    @property
    def spotify_service(self):
        """ Return the one and only one spotify service running on the store """
        for spotify in self.store.powerupsFor(ispotify.ISpotifyService):
            return spotify

    def subscribe(self):
        e = self.evreactor
        e.subscribe(self.handle_search_start, ijukebox.ISearchStartedEvent)
        e.subscribe(self.handle_search_results, ispotify.ISpotifySearchResultsEvent)

    def handle_search_start(self, ev):
        self.callRemote("startThrobber")

    def human_duration(self, d):
        mins = int(d/60000)
        secs = int((d - (mins*60000)) / 1000)
        return u"%dm %ds" % (mins, secs)

    @athena.expose
    def playlist_info(self, pid):
        return adaptivejson.simplify(self.spotify_service.get_playlist(pid))

    def handle_search_results(self, ev):
        artists = {}
        albums = {}
        tracks = {}
        for a in ev.results.artists():
            k = unicode(Link.from_artist(a))
            artists[k] = {
                u'name': a.name().decode("utf-8"),
                u'link': k,
            }
        for a in ev.results.albums():
            k = unicode(Link.from_album(a))
            albums[k] = {
                u'name': a.name().decode("utf-8"),
                u'link': k,
            }
        for a in ev.results.tracks():
            k = unicode(Link.from_track(a, 0))
            tracks[k] = {
                u'name': a.name().decode("utf-8"),
                u'link': k,
                u'album_name': a.album().name().decode("utf-8"),
                u'artist_name': ", ".join([x.name() for x in a.artists()]).decode("utf-8"),
                u'duration': self.human_duration(a.duration()),
            }
        self.callRemote("searchResults", artists, albums, tracks)

class Main(base.BaseElementContainer):
    docFactory = xmltemplate("main.html")

    contained = {
        'search': Search,
        'options': Options,
        'document': Document,
        'playlists': Playlists,
    }

class Root(rend.Page):

    """ This hangs from /spotify at the root of the server. """

    def renderHTTP(self, ctx):
        request = inevow.IRequest(ctx)
        request.redirect(request.URLPath().child('jukebox'))
        return ''

    def child_stream(self, ctx):
        log.msg("Request for spotify track %s received" % ctx.arg('tid'), system="squeal.web.service.Root")
        tid = ctx.arg('tid')
        return SpotifyStreamer(self.original, tid)

    def child_image(self, ctx):
        #log.msg("Request for spotify image %s received" % ctx.arg('image'), system="squeal.web.service.Root")
        image_id = ctx.arg('image')
        return SpotifyImage(self.original, image_id)
