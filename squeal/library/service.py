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

""" The service that orchestrates library activity in the service hierarchy. """

__author__ = "Doug Winter <doug.winter@isotoma.com>"
__docformat__ = "restructuredtext en"
__version__ = "$Revision$"[11:-2]


from zope.interface import Interface, implements
from twisted.application import service
from twisted.internet import reactor
from axiom.item import Item
from axiom.attributes import reference, inmemory

from record import *
from squeal.isqueal import *

class Library(Item, service.Service):
    implements(ILibrary)
    powerupInterfaces = (ILibrary,)

    collections = reference()
    running = inmemory()
    name = inmemory()
    parent = inmemory()

    def __init__(self, config, store):
        """ I have no configuration """
        Item.__init__(self, store=store)

    def activate(self):
        self.rescan()

    def rescan(self):
        for collection in self.store.query(Collection):
            reactor.callLater(0, collection.scan)

    def add_collection(self, pathname):
        for c in self.store.query(Collection, pathname == pathname):
            break
        else:
            return Collection(store=self.store, pathname=pathname)

    def tracks(self):
        return self.store.query(Track)
