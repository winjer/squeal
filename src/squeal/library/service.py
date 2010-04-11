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

""" The service that orchestrates library activity in the service hierarchy. """

__author__ = "Doug Winter <doug.winter@isotoma.com>"
__docformat__ = "restructuredtext en"
__version__ = "$Revision$"[11:-2]


from zope.interface import Interface, implements
from twisted.python import log
from twisted.application import service
from twisted.internet import reactor
from axiom.item import Item
from axiom.attributes import reference, inmemory

import web
from record import *
from ilibrary import *

from formlet import form
from formlet import field

setup_form = form.Form("library-setup", action="install")
field.StringField(form=setup_form, name="pathname", label="Directory containing music files")
field.SubmitButton(form=setup_form, name="submit", label="Configure library")

class Library(Item, service.Service):
    implements(ILibrary, IMusicSource)
    powerupInterfaces = (ILibrary, IMusicSource)

    collections = reference()
    running = inmemory()
    name = 'library'
    label = 'Local music'
    parent = inmemory()
    naming_policy = reference()

    setup_form = setup_form

    def activate(self):
        self.rescan()

    def rescan(self):
        log.msg("Rescanning music collections", system="squeal.library.service.Library")
        for collection in self.store.query(Collection):
            log.msg("Initiating scan on %r" % collection)
            reactor.callLater(0, collection.scan)

    def add_collection(self, pathname):
        """ Add a new collection, representing a set of music under a specific
        pathname. If this pathname has already been added then a duplicate is
        not created - the original is returned instead. """
        for c in self.store.query(Collection, Collection.pathname == pathname):
            log.msg("Found duplicate collection %s" % pathname, system="squeal.library.service.Library")
            return c
        log.msg("Adding a collection at %s" % pathname, system="squeal.library.service.Library")
        return Collection(store=self.store, pathname=pathname)

    def tracks(self):
        return self.store.query(Track, sort=Track.title.asc)

    def artists(self):
        return self.store.query(Artist, sort=Artist.name.asc)

    def albums(self):
        return self.store.query(Album, sort=Album.name.asc)

    def main_widget(self):
        return web.Main()

    def get_track(self, tid):
        return self.store.getItemByID(int(tid))

