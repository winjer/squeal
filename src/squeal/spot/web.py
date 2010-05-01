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

class Playlists(base.BaseElement):
    jsClass = u"Spot.Playlists"
    docFactory = xmltemplate("playlists.html")

    @property
    def spotify_service(self):
        """ Return the one and only one spotify service running on the store """
        for spotify in self.store.powerupsFor(ispotify.ISpotifyService):
            return spotify

    @property
    def playlist_service(self):
        for p in self.store.powerupsFor(isqueal.IPlaylist):
            return p

    @athena.expose
    def playlists(self):
        return map(adaptivejson.simplify, self.spotify_service.playlists())

    def reload(self, ev):
        self.callRemote("reload");

    @athena.expose
    def goingLive(self):
        self.callRemote("reload");
        self.evreactor.subscribe(self.reload, ispotify.ISpotifyMetadataUpdatedEvent)

    @athena.expose
    def play(self, playlistID):
        log.msg("Playing %s" % playlistID, system="squeal.spot.web.Playlists")
        playlist = self.spotify_service.getPlaylistByLink(playlistID)
        self.playlist_service.playfirst(*self.spotify_service.wrap_tracks(*playlist))

    @athena.expose
    def append(self, playlistID):
        log.msg("Appending %s" % playlistID, system="squeal.spot.web.Playlists")
        playlist = self.spotify_service.getPlaylistByLink(playlistID)
        self.playlist_service.enqueue(*self.spotify_service.wrap_tracks(*playlist))

class Search(base.BaseElement):
    jsClass = u"Spot.Search"
    docFactory = xmltemplate("search.html")

class Main(base.BaseElementContainer):
    docFactory = xmltemplate("main.html")
    jsClass = u"Spot.Main"

    contained = {
        'search': Search,
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
