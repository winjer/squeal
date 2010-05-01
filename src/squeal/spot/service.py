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

""" Spotify orchestration. """

__author__ = "Doug Winter <doug.winter@isotoma.com>"
__docformat__ = "restructuredtext en"
__version__ = "$Revision$"[11:-2]

from zope.interface import implements
from twisted.python import log
from twisted.application import service
from twisted.internet import reactor
from axiom.item import Item
from axiom.attributes import reference, inmemory, text, integer, timestamp

from squeal.event import EventReactor
from squeal import isqueal

import web
import ispotify
from event import *
from track import SpotifyTrack
from manager import SpotifyManager
from spotify import Link
import json

from formlet import form
from formlet import field

setup_form = form.Form("setup", action="install")
field.StringField(form=setup_form, name="username", label="Username")
field.StringField(form=setup_form, type_="password", name="password", label="Password")
field.SubmitButton(form=setup_form, name="submit", label="Configure spotify")

class Spotify(Item, service.Service):

    """ The spotify service. Provides an interface to the rest of the system
    for the spotify session and related machinery. """

    implements(ispotify.ISpotifyService,
               isqueal.IMusicSource,
               isqueal.ITrackSource,
               isqueal.IUserConfigurable,
               isqueal.IRootResourceExtension,
               )
    powerupInterfaces = (ispotify.ISpotifyService,
                         isqueal.ITrackSource,
                         isqueal.IMusicSource,
                         isqueal.IUserConfigurable,
                         isqueal.IRootResourceExtension,
                         )

    namespace = 'spotify'
    username = text()
    password = text()
    running = inmemory()
    name = 'spotify'
    parent = inmemory()
    mgr = inmemory()
    playing = inmemory()
    setup_form = setup_form

    label = "Spotify"

    def __init__(self, store, username, password):
        Item.__init__(self, store=store, username=username, password=password)

    def __repr__(self):
        return "Spotify(username=%r, password=SECRET, storeID=%r)" % (self.username, self.storeID)

    @property
    def evreactor(self):
        return self.store.findFirst(EventReactor)

    def activate(self):
        self.playing = None

    def startService(self):
        self.mgr = SpotifyManager(self)
        reactor.callInThread(self.mgr.connect)
        return service.Service.startService(self)

    def play(self, tid):
        log.msg("Play called with %r" % tid, system="squeal.spot.service.Spotify")
        track = self.get_track(tid)
        for p in self.store.powerupsFor(ISlimPlayerService):
            p.play(track)

    def registerConsumer(self, consumer, tid):
        log.msg("registering consumer %r on %r" % (consumer, self), system="squeal.spot.service.Spotify")
        self.playing = tid
        self.mgr.load(tid)
        self.mgr.play(consumer)

    def playlists(self):
        if self.mgr.ctr:
            return self.mgr.ctr
        return []

    def get_playlist(self, pid):
        for playlist in self.mgr.ctr:
            if unicode(Link.from_playlist(playlist)) == pid:
                return playlist

    def image(self, image_id):
        return self.mgr.image(image_id)

    def search(self, query):
        self.mgr.search(query)

    def getTrackByLink(self, link):
        l = Link.from_string(link)
        return l.as_track()

    def getPlaylistByLink(self, link):
        """
        Pass link as the string representation.

        This is a bit evil, there's no other way to do this, and if we
        list other people's playlists we'll need to do even more weird stuff.
        See
        http://getsatisfaction.com/spotify/topics/libspotify_does_not_provide_a_sp_link_as_playlist
        """
        for p in self.mgr.ctr:
            l = str(Link.from_playlist(p))
            if l == link:
                return p
        log.msg("Cannot find playlist for %s" % link, system="squeal.spot.service.Spotify")

    def main_widget(self):
        return web.Main()

    #isqueal.TrackSource

    def get_track(self, tid):
        track = Link.from_string(tid).as_track()
        return SpotifyTrack(self, track)

    def wrap_tracks(self, *tracks):
        for t in tracks:
            yield SpotifyTrack(self, t)


    #isqueal.IRootResourceExtension

    def add_resources(self, root):
        root.putChild("spotify", web.Root(self))

