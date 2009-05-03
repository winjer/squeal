from zope.interface import Interface, implements
from twisted.application import service
from twisted.internet import defer
from twisted.internet import reactor
from axiom.item import Item
from axiom.attributes import reference, inmemory, text, integer

from squeal.isqueal import *

class EventSubscription(object):

    """ An event subscription.  By default the handler will be called every time this event is fired """

    def __init__(self, evreactor, handler, *ifaces):
        self.evreactor = evreactor
        self.ifaces = ifaces
        self.handler = handler

    def condition(self, event):
        for i in self.ifaces:
            if not i.providedBy(event):
                return False
        return True

    def unsubscribe(self):
        self.evreactor.unsubscribe(self)

class EventReactor(Item, service.Service):
    implements(IEventReactor)
    powerupInterfaces = (IEventReactor,)

    dummy = integer()
    running = inmemory()
    name = inmemory()
    parent = inmemory()
    subscribers = inmemory()

    def __init__(self, config, store):
        Item.__init__(self, store=store)

    def activate(self):
        self.subscribers = []

    @defer.inlineCallbacks
    def _fireEvent(self, event, *interfaces):
        """ Fire the specified event. You can optionally provide additional
        interfaces that will be added to the event before firing. """
        if interfaces:
            event = copy.copy(event)
            alsoProvides(event, *interfaces)
        for s in self.subscribers:
            call = yield defer.maybeDeferred(s.condition, event)
            if call:
                yield defer.maybeDeferred(s.handler, event)

    def fireEvent(self, event, *interfaces):
        reactor.callLater(0, self._fireEvent, event, *interfaces)

    def subscribe(self, handler, *ifaces):
        subscription = EventSubscription(self, handler, *ifaces)
        self.subscribers.append(subscription)
        return subscription

    def unsubscribe(self, subscription):
        self.subscribers.remove(subscription)

