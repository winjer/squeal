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

    def addCollection(self, pathname):
        for c in self.store.query(Collection, pathname == pathname):
            break
        else:
            return Collection(store=self.store, pathname=pathname)

    def tracks(self):
        return self.store.query(Track)
