# Copyright (c) 2008 Divmod.  See LICENSE for details.

"""
Tests for L{epsilon.amprouter}.
"""

from zope.interface import implements
from zope.interface.verify import verifyObject

from twisted.python.failure import Failure
from twisted.protocols.amp import IBoxReceiver, IBoxSender
from twisted.trial.unittest import TestCase

from epsilon.amprouter import _ROUTE, RouteNotConnected, Router


class SomeReceiver:
    """
    A stub AMP box receiver which just keeps track of whether it has been
    started or stopped and what boxes have been delivered to it.

    @ivar sender: C{None} until C{startReceivingBoxes} is called, then a
        reference to the L{IBoxSender} passed to that method.

    @ivar reason: C{None} until {stopReceivingBoxes} is called, then a
        reference to the L{Failure} passed to that method.

    @ivar started: C{False} until C{startReceivingBoxes} is called, then
        C{True}.

    @ivar stopped: C{False} until C{stopReceivingBoxes} is called, then
        C{True}.
    """
    implements(IBoxReceiver)

    sender = None
    reason = None
    started = False
    stopped = False

    def __init__(self):
        self.boxes = []


    def startReceivingBoxes(self, sender):
        self.started = True
        self.sender = sender


    def ampBoxReceived(self, box):
        if self.started and not self.stopped:
            self.boxes.append(box)


    def stopReceivingBoxes(self, reason):
        self.stopped = True
        self.reason = reason



class CollectingSender:
    """
    An L{IBoxSender} which collects and saves boxes and errors sent to it.
    """
    implements(IBoxSender)

    def __init__(self):
        self.boxes = []
        self.errors = []


    def sendBox(self, box):
        """
        Reject boxes with non-string keys or values; save all the rest in
        C{self.boxes}.
        """
        for k, v in box.iteritems():
            if not (isinstance(k, str) and isinstance(v, str)):
                raise TypeError("Cannot send boxes containing non-strings")
        self.boxes.append(box)


    def unhandledError(self, failure):
        self.errors.append(failure.getErrorMessage())



class RouteTests(TestCase):
    """
    Tests for L{Route}, the L{IBoxSender} which handles adding routing
    information to outgoing boxes.
    """
    def setUp(self):
        """
        Create a route attached to a stub sender.
        """
        self.receiver = SomeReceiver()
        self.sender = CollectingSender()
        self.localName = u"foo"
        self.remoteName = u"bar"
        self.router = Router()
        self.router.startReceivingBoxes(self.sender)
        self.route = self.router.bindRoute(self.receiver, self.localName)


    def test_interfaces(self):
        """
        L{Route} instances provide L{IBoxSender}.
        """
        self.assertTrue(verifyObject(IBoxSender, self.route))


    def test_start(self):
        """
        L{Route.start} starts its L{IBoxReceiver}.
        """
        self.assertFalse(self.receiver.started)
        self.route.start()
        self.assertTrue(self.receiver.started)
        self.assertIdentical(self.receiver.sender, self.route)


    def test_stop(self):
        """
        L{Route.stop} stops its L{IBoxReceiver}.
        """
        self.route.start()
        self.assertFalse(self.receiver.stopped)
        self.route.stop(Failure(RuntimeError("foo")))
        self.assertTrue(self.receiver.stopped)
        self.receiver.reason.trap(RuntimeError)


    def test_sendBox(self):
        """
        L{Route.sendBox} adds the route name to the box before passing it on to
        the underlying sender.
        """
        self.route.connectTo(self.remoteName)
        self.route.sendBox({"foo": "bar"})
        self.assertEqual(
            self.sender.boxes, [{_ROUTE: self.remoteName, "foo": "bar"}])


    def test_sendUnroutedBox(self):
        """
        If C{Route.connectTo} is called with C{None}, no route name is added to
        the outgoing box.
        """
        self.route.connectTo(None)
        self.route.sendBox({"foo": "bar"})
        self.assertEqual(
            self.sender.boxes, [{"foo": "bar"}])


    def test_sendBoxWithoutConnection(self):
        """
        L{Route.sendBox} raises L{RouteNotConnected} if called before the
        L{Route} is connected to a remote route name.
        """
        self.assertRaises(
            RouteNotConnected, self.route.sendBox, {'foo': 'bar'})


    def test_unbind(self):
        """
        L{Route.unbind} removes the route from its router.
        """
        self.route.unbind()
        self.assertRaises(
            KeyError, self.router.ampBoxReceived, {_ROUTE: self.localName})



class RouterTests(TestCase):
    """
    Tests for L{Router}, the L{IBoxReceiver} which directs routed AMP boxes to
    the right object.
    """
    def setUp(self):
        """
        Create sender, router, receiver, and route objects.
        """
        self.sender = CollectingSender()
        self.router = Router()
        self.router.startReceivingBoxes(self.sender)
        self.receiver = SomeReceiver()
        self.route = self.router.bindRoute(self.receiver)
        self.route.connectTo(u"foo")


    def test_interfaces(self):
        """
        L{Router} instances provide L{IBoxReceiver}.
        """
        self.assertTrue(verifyObject(IBoxReceiver, self.router))


    def test_uniqueRoutes(self):
        """
        L{Router.createRouteIdentifier} returns a new, different route
        identifier on each call.
        """
        identifiers = [self.router.createRouteIdentifier() for x in range(10)]
        self.assertEqual(len(set(identifiers)), len(identifiers))


    def test_bind(self):
        """
        L{Router.bind} returns a new L{Route} instance which will send boxes to
        the L{Route}'s L{IBoxSender} after adding a C{_ROUTE} key to them.
        """
        self.route.sendBox({'foo': 'bar'})
        self.assertEqual(
            self.sender.boxes,
            [{_ROUTE: self.route.remoteRouteName, 'foo': 'bar'}])

        self.route.unhandledError(Failure(Exception("some test exception")))
        self.assertEqual(
            self.sender.errors, ["some test exception"])


    def test_bindBeforeStart(self):
        """
        If a L{Route} is created with L{Router.bind} before the L{Router} is
        started with L{Router.startReceivingBoxes}, the L{Route} is created
        unstarted and only started when the L{Router} is started.
        """
        router = Router()
        receiver = SomeReceiver()
        route = router.bindRoute(receiver)
        route.connectTo(u'quux')
        self.assertFalse(receiver.started)
        sender = CollectingSender()
        router.startReceivingBoxes(sender)
        self.assertTrue(receiver.started)
        route.sendBox({'foo': 'bar'})
        self.assertEqual(
            sender.boxes, [{_ROUTE: route.remoteRouteName, 'foo': 'bar'}])
        router.ampBoxReceived({_ROUTE: route.localRouteName, 'baz': 'quux'})
        self.assertEqual(receiver.boxes, [{'baz': 'quux'}])


    def test_bindBeforeStartFinishAfterStart(self):
        """
        If a L{Route} is created with L{Router.connect} before the L{Router} is
        started with L{Router.startReceivingBoxes} but the Deferred returned by
        the connect thunk does not fire until after the router is started, the
        L{IBoxReceiver} associated with the route is not started until that
        Deferred fires and the route is associated with a remote route name.
        """
        router = Router()
        receiver = SomeReceiver()
        route = router.bindRoute(receiver)
        sender = CollectingSender()
        router.startReceivingBoxes(sender)
        self.assertFalse(receiver.started)
        route.connectTo(u"remoteName")
        self.assertTrue(receiver.started)
        receiver.sender.sendBox({'foo': 'bar'})
        self.assertEqual(sender.boxes, [{_ROUTE: 'remoteName', 'foo': 'bar'}])


    def test_ampBoxReceived(self):
        """
        L{Router.ampBoxReceived} passes on AMP boxes to the L{IBoxReceiver}
        identified by the route key in the box.
        """
        firstReceiver = SomeReceiver()
        firstRoute = self.router.bindRoute(firstReceiver)
        firstRoute.start()

        secondReceiver = SomeReceiver()
        secondRoute = self.router.bindRoute(secondReceiver)
        secondRoute.start()

        self.router.ampBoxReceived(
            {_ROUTE: firstRoute.localRouteName, 'foo': 'bar'})
        self.router.ampBoxReceived(
            {_ROUTE: secondRoute.localRouteName, 'baz': 'quux'})

        self.assertEqual(firstReceiver.boxes, [{'foo': 'bar'}])
        self.assertEqual(secondReceiver.boxes, [{'baz': 'quux'}])


    def test_ampBoxReceivedDefaultRoute(self):
        """
        L{Router.ampBoxReceived} delivers boxes with no route to the default
        box receiver.
        """
        sender = CollectingSender()
        receiver = SomeReceiver()
        router = Router()
        router.startReceivingBoxes(sender)
        router.bindRoute(receiver, None).start()
        router.ampBoxReceived({'foo': 'bar'})
        self.assertEqual(receiver.boxes, [{'foo': 'bar'}])


    def test_stopReceivingBoxes(self):
        """
        L{Router.stopReceivingBoxes} calls the C{stop} method of each connected
        route.
        """
        sender = CollectingSender()
        router = Router()
        router.startReceivingBoxes(sender)
        receiver = SomeReceiver()
        router.bindRoute(receiver)

        class DummyException(Exception):
            pass

        self.assertFalse(receiver.stopped)

        router.stopReceivingBoxes(Failure(DummyException()))

        self.assertTrue(receiver.stopped)
        receiver.reason.trap(DummyException)
