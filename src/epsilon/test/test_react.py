# Copyright (c) 2008 Divmod.  See LICENSE for details.

"""
Tests for L{epsilon.react}.
"""

from twisted.internet.defer import Deferred, succeed, fail
from twisted.internet.task import Clock
from twisted.trial.unittest import TestCase

from epsilon.react import react


class _FakeReactor(object):
    """
    A fake implementation of L{IReactorCore}.
    """
    def __init__(self):
        self._running = False
        self._clock = Clock()
        self.callLater = self._clock.callLater
        self.seconds = self._clock.seconds
        self.getDelayedCalls = self._clock.getDelayedCalls
        self._whenRunning = []
        self._shutdownTriggers = {'before': [], 'during': []}


    def callWhenRunning(self, callable):
        if self._running:
            callable()
        else:
            self._whenRunning.append(callable)


    def addSystemEventTrigger(self, phase, event, callable, *args):
        assert phase in ('before', 'during')
        assert event == 'shutdown'
        self._shutdownTriggers[phase].append((callable, args))


    def run(self):
        """
        Call timed events until there are no more or the reactor is stopped.

        @raise RuntimeError: When no timed events are left and the reactor is
            still running.
        """
        self._running = True
        whenRunning = self._whenRunning
        self._whenRunning = None
        for callable in whenRunning:
            callable()
        while self._running:
            calls = self.getDelayedCalls()
            if not calls:
                raise RuntimeError("No DelayedCalls left")
            self._clock.advance(calls[0].getTime() - self.seconds())
        shutdownTriggers = self._shutdownTriggers
        self._shutdownTriggers = None
        for (trigger, args) in shutdownTriggers['before'] + shutdownTriggers['during']:
            trigger(*args)


    def stop(self):
        """
        Stop the reactor.
        """
        self._running = False



class ReactTests(TestCase):
    """
    Tests for L{epsilon.react.react}.
    """
    def test_runsUntilAsyncCallback(self):
        """
        L{react} runs the reactor until the L{Deferred} returned by the
        function it is passed is called back, then stops it.
        """
        timePassed = []
        def main(reactor):
            finished = Deferred()
            reactor.callLater(1, timePassed.append, True)
            reactor.callLater(2, finished.callback, None)
            return finished
        r = _FakeReactor()
        react(r, main, [])
        self.assertEqual(timePassed, [True])
        self.assertEqual(r.seconds(), 2)


    def test_runsUntilSyncCallback(self):
        """
        L{react} returns quickly if the L{Deferred} returned by the function it
        is passed has already been called back at the time it is returned.
        """
        def main(reactor):
            return succeed(None)
        r = _FakeReactor()
        react(r, main, [])
        self.assertEqual(r.seconds(), 0)


    def test_runsUntilAsyncErrback(self):
        """
        L{react} runs the reactor until the L{Deferred} returned by the
        function it is passed is errbacked, then it stops the reactor and
        reports the error.
        """
        class ExpectedException(Exception):
            pass

        def main(reactor):
            finished = Deferred()
            reactor.callLater(1, finished.errback, ExpectedException())
            return finished
        r = _FakeReactor()
        react(r, main, [])
        errors = self.flushLoggedErrors(ExpectedException)
        self.assertEqual(len(errors), 1)


    def test_runsUntilSyncErrback(self):
        """
        L{react} returns quickly if the L{Deferred} returned by the function it
        is passed has already been errbacked at the time it is returned.
        """
        class ExpectedException(Exception):
            pass

        def main(reactor):
            return fail(ExpectedException())
        r = _FakeReactor()
        react(r, main, [])
        self.assertEqual(r.seconds(), 0)
        errors = self.flushLoggedErrors(ExpectedException)
        self.assertEqual(len(errors), 1)


    def test_singleStopCallback(self):
        """
        L{react} doesn't try to stop the reactor if the L{Deferred} the
        function it is passed is called back after the reactor has already been
        stopped.
        """
        def main(reactor):
            reactor.callLater(1, reactor.stop)
            finished = Deferred()
            reactor.addSystemEventTrigger(
                'during', 'shutdown', finished.callback, None)
            return finished
        r = _FakeReactor()
        react(r, main, [])
        self.assertEqual(r.seconds(), 1)


    def test_singleStopErrback(self):
        """
        L{react} doesn't try to stop the reactor if the L{Deferred} the
        function it is passed is errbacked after the reactor has already been
        stopped.
        """
        class ExpectedException(Exception):
            pass

        def main(reactor):
            reactor.callLater(1, reactor.stop)
            finished = Deferred()
            reactor.addSystemEventTrigger(
                'during', 'shutdown', finished.errback, ExpectedException())
            return finished
        r = _FakeReactor()
        react(r, main, [])
        self.assertEqual(r.seconds(), 1)
        errors = self.flushLoggedErrors(ExpectedException)
        self.assertEqual(len(errors), 1)


    def test_arguments(self):
        """
        L{react} passes the elements of the list it is passed as positional
        arguments to the function it is passed.
        """
        args = []
        def main(reactor, x, y, z):
            args.extend((x, y, z))
            return succeed(None)
        r = _FakeReactor()
        react(r, main, [1, 2, 3])
        self.assertEqual(args, [1, 2, 3])
