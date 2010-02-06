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

"""

Simple event forwarding system. Events are represented with python objects
that implement interfaces. For example:

> class IFooEvent(Interface): pass
> class IBarEvent(Interface): pass
>
> class MyEvent(object):
>     implements(IFooEvent, IBarEvent)
>
>     def __init__(self, x, y):
>     self.x = x
>     self.y = y

The object can provide whatever methods or attributes are required.

Subscribers specify which events they wish to received based on the interfaces
implemented by the events.

Additional interfaces can be added to an event as needed at the time it is fired.

Sending events
==============

> event = MyEvent(10, "foo")
> evr = self.store.findFirst(EventReactor)
> evr.fireEvent(event, IBazEvent)

Subscribing to and receiving events
=====================

> class Thing(Item, Service):
>
>     def activate(self):
>         evr = self.store.findFirst(EventReactor)
>         evr.subscribe(self.handleFooEvent, IFooEvent)
>
>     def handleFooEvent(self, ev):
>         x = ev.x

"""

__author__ = 'Doug Winter <doug.winter@isotoma.com>'
__docformat__ = 'restructuredtext en'
__version__ = '$Revision$'[11:-2]

from zope.interface import Interface, implements, alsoProvides
from twisted.application import service
from twisted.internet import defer
from twisted.internet import reactor
from twisted.python import log
from axiom.item import Item
from axiom.attributes import reference, inmemory, text, integer

from squeal.isqueal import *

import copy

class EventSubscription(object):

    """ An event subscription. By default the handler will be called every
    time this event is fired """

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
        log.msg("Firing Event: %s [%s]" % (event.__class__.__name__, ",".join(x.__name__ for x in interfaces)), system="squeal.event.EventReactor")
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

