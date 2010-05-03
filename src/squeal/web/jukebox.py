# $Id$
#
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

""" The web jukebox. """

__author__ = "Doug Winter <doug.winter@isotoma.com>"
__docformat__ = "restructuredtext en"
__version__ = "$Revision$"[11:-2]

from zope.interface import Interface, implements

from nevow import rend
from nevow import inevow
from nevow import loaders
from nevow import tags as T
from nevow import page
from nevow import athena
from nevow.flat import flatten
import urllib
import os

import base

import ijukebox
from squeal import isqueal
from squeal.adaptivejson import simplify

from formlet import widget
from formlet import form
from formlet import field

from twisted.python import log
from twisted.internet import defer

class Setup(base.BaseElement):
    jsClass = u"Squeal.Setup"
    docFactory = base.xmltemplate("setup.html")

    @property
    def plugin_manager(self):
        for s in self.store.powerupsFor(isqueal.IPluginManager):
            return s

    @page.renderer
    def install(self, request, tag):
        def installer(i):
            p = PluginInstaller(i)
            p.setFragmentParent(self)
            return p
        return tag[(installer(i) for i in self.plugin_manager.installable)]

class Account(base.BaseElement):
    jsClass = u"Squeal.Account"
    docFactory = base.xmltemplate("account.html")

    @page.renderer
    def credentials(self, request, tag):
        return tag['You are not logged in']

class Header(base.BaseElement):
    jsClass = u"Squeal.Header"
    docFactory = base.xmltemplate("header.html")

    def __init__(self, *a, **kw):
        super(Header, self).__init__(*a, **kw)
        self.ignore_volume_change = False

    @athena.expose
    def goingLive(self):
        self.subscribe()
        # need to work out what the logic is here if there
        # is more than one player - i guess the UI binds to
        # a single player
        for p in self.slim_service.players:
            self.callRemote("volume_change", p.volume.volume)
            break
        if self.playlist_service.playing:
            current = self.playlist_service.get_current_track()
            played = self.playlist_service.time_played()
            self.callRemote('start_progress', played, current.duration)

    def subscribe(self):
        self.evreactor.subscribe(self.queueChange, isqueal.IPlaylistChangeEvent)
        self.evreactor.subscribe(self.queueChange, isqueal.IMetadataChangeEvent)
        self.evreactor.subscribe(self.player_change, isqueal.IPlayerStateChange)
        self.evreactor.subscribe(self.volume_change, isqueal.IVolumeChangeEvent)

    @athena.expose
    @defer.inlineCallbacks
    def set_volume(self, value):
        self.ignore_volume_change = True
        for p in self.slim_service.players:
            p.volume.volume = value
            yield p.send_volume()
        self.ignore_volume_change = False

    def volume_change(self, ev):
        if not self.ignore_volume_change:
            self.callRemote("volume_change", ev.volume.volume)

    def player_change(self, ev):
        current = self.playlist_service.get_current_track()
        if ev.state == ev.State.PLAYING:
            if 'SQUEAL_DEBUG' in os.environ:
                log.msg("Player is playing, starting progress", system="squeal.web.jukebox.Header")
            self.callRemote('start_progress', 0, current.duration)
        elif ev.state == ev.State.PAUSED:
            self.callRemote('halt_progress')
            if 'SQUEAL_DEBUG' in os.environ:
                log.msg("Player is playing, halting progress", system="squeal.web.jukebox.Header")

    @property
    def playlist_service(self):
        for queue in self.store.powerupsFor(isqueal.IPlaylist):
            return queue

    @property
    def slim_service(self):
        for s in self.store.powerupsFor(isqueal.ISlimPlayerService):
            return s

    def queueChange(self, ev):
        self.reload()

    def reload(self):
        p = self.playdata()
        if p is not None:
            self.callRemote("reload", p)

    def playdata(self):
        current = self.playlist_service.get_current_track()
        if current is None:
            return None
        elif not current.is_loaded:
            return {
                u'image': u'',
                u'title': u'Loading...',
                u'artist': u'Loading...',
                u'album': u'Loading...',
                u'duration': 0
            }
        else:
            return {
                u'image': current.image_uri,
                u'title': current.title,
                u'artist': current.artist,
                u'album': current.album,
                u'duration': current.duration,
            }

    def current_renderer(self, attr):
        current = self.playlist_service.get_current_track()
        if current is None:
            return "-"
        elif not current.is_loaded:
            return "Loading..."
        else:
            return getattr(current, attr)

    @page.renderer
    def current_track(self, request, tag):
        return tag[self.current_renderer('title')]

    @page.renderer
    def current_artist(self, request, tag):
        return tag[self.current_renderer('artist')]

    @page.renderer
    def current_album(self, request, tag):
        return tag[self.current_renderer('album')]

    @athena.expose
    def back(self):
        """ Go back a track in the playlist """

    @athena.expose
    def playpause(self):
        """ Either play or pause, depending on the current state of the
        players """
        if self.playlist_service.playing:
            self.playlist_service.pause()
        else:
            self.playlist_service.play()

    @athena.expose
    def next(self):
        """ Skip to the next track in the playlist """


class Playlist(base.BaseElement):
    jsClass = u"Squeal.Playlist"
    docFactory = base.xmltemplate("playlist.html")

    @athena.expose
    def goingLive(self):
        self.subscribe()
        self.reload()

    def subscribe(self):
        self.evreactor.subscribe(self.queueChange, isqueal.IPlaylistChangeEvent)
        self.evreactor.subscribe(self.queueChange, isqueal.IMetadataChangeEvent)

    @property
    def playlist_service(self):
        for queue in self.store.powerupsFor(isqueal.IPlaylist):
            return queue

    def queueChange(self, ev):
        self.reload()

    @athena.expose
    def clear(self):
        log.msg("clear", system="squeal.web.jukebox.Queue")
        self.playlist_service.clear()
        self.reload()

    def reload(self):
        queue = self.playlist_service
        items = map(simplify, queue)
        self.callRemote("reload", {
            u'items': items,
            u'current': queue.current,
        })

    @athena.expose
    def queueTrack(self, namespace, tid):
        """ Called from other UI components, via the javascript partner class
        to this one. Allows queuing of any track if it's global tid is known.
        """
        log.msg("queueTrack called with %r, %r" % (namespace, tid), system="squeal.web.jukebox.Queue")
        queue = self.playlist_service
        for p in self.store.powerupsFor(isqueal.ITrackSource):
            if p.namespace == namespace:
                provider = p
                break
        else:
            raise KeyError("No track source uses the namespace %s" % namespace)
        track = provider.get_track(tid)
        queue.enqueue(track)

class Main(base.BaseElement):
    jsClass = u"Squeal.Main"
    docFactory = base.xmltemplate("main.html")

class PluginInstaller(base.BaseElement):
    jsClass = u"Squeal.PluginInstaller"
    docFactory = base.xmltemplate("plugin_installer.html")

    def __init__(self, original):
        super(PluginInstaller, self).__init__()
        self.original = original

    @property
    def plugin_manager(self):
        for s in self.store.powerupsFor(isqueal.IPluginManager):
            return s

    @page.renderer
    def name(self, request, tag):
        return tag[self.original['plugin'].name]

    @page.renderer
    def description(self, request, tag):
        return tag[self.original['plugin'].description]

    @page.renderer
    def configform(self, request, tag):
        setup_form = self.original['plugin'].setup_form
        return tag[setup_form.element(self)]

    @athena.expose
    def install(self, **kw):
        pm = self.plugin_manager
        s = pm.install(args=kw, **self.original)
        s.setServiceParent(self.plugin_manager.parent)

class Connected(base.BaseElement):
    jsClass = u"Squeal.Connected"
    docFactory = base.xmltemplate("connected.html")

    def subscribe(self):
        log.msg("Subscribing", system="squeal.web.jukebox.Connected")
        self.evreactor.subscribe(self.playerChange, isqueal.IPlayerStateChange)

    def playerChange(self, ev):
        log.msg("Reloading players", system="squeal.web.jukebox.Connected")
        self.callRemote("reload", unicode(flatten(self.player_content())))

    @page.renderer
    def users(self, request, tag):
        return tag['USERS']

    def player_content(self):
        for p in self.store.powerupsFor(isqueal.ISlimPlayerService):
            slimservice = p
            break
        else:
            raise("Unable to show the connected list with no SlimService running")
        players = []
        for p in slimservice.players:
            players.append(T.li["%s (%s)" % (p.mac_address, p.device_type)])
        if players:
            return T.h2["Players"], T.ul[players]
        else:
            return T.h2["Players"], "No players connected!"

    @page.renderer
    def players(self, request, tag):
        return tag[self.player_content()]

class PlayActions(base.BaseElement):
    jsClass = u"Squeal.PlayActions"
    docFactory = base.xmltemplate("playactions.html")

### this is really confusing
### we're mixing Elements and Pages, and they do
### stuff quite differently.  the following is a page!

class Jukebox(base.BasePageContainer):

    docFactory = base.xmltemplate("jukebox.html")

    contained = {
        'header': Header,
        'play_actions': PlayActions,
        'playlist': Playlist,
        #'account': Account,
        #'main': Main,
        #'playing': Playing,
        #'queue': Queue,
        #'connected': Connected,
        #'setup': Setup,
    }

    def __init__(self, service):
        super(Jukebox, self).__init__()
        self.service = service

    def render_sources(self, ctx, data):
        sources = []
        for s in self.service.store.powerupsFor(isqueal.IMusicSource):
            w = s.main_widget()
            w.setFragmentParent(self)
            sources.append(w)
        setup = Setup()
        setup.setFragmentParent(self)
        sources.append(setup)
        return ctx.tag[
            sources
        ]
