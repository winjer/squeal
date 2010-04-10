# Copyright (c) 2008 Divmod.  See LICENSE for details.

"""
Tests for L{epsilon.process}.
"""

from zope.interface.verify import verifyObject

from twisted.trial.unittest import TestCase
from twisted.application.service import IService, MultiService
from twisted.internet.protocol import Protocol

from epsilon import process


class StandardIOServiceTests(TestCase):
    """
    Tests for L{StandardIOService}, an L{IService} implementation which
    associates a L{IProtocol} provider with stdin and stdout when it is
    started.
    """
    def test_interface(self):
        """
        L{StandardIOService} instances provide L{IService}.
        """
        verifyObject(IService, process.StandardIOService(None))


    def test_startService(self):
        """
        L{StandardIOService.startService} connects a protocol to a standard io
        transport.
        """
        # This sucks.  StandardIO sucks.  APIs should be testable.
        L = []
        self.patch(process, 'StandardIO', L.append)
        proto = Protocol()
        service = process.StandardIOService(proto)
        service.startService()
        self.assertEqual(L, [proto])


    def test_setName(self):
        """
        L{StandardIOService.setName} sets the C{name} attribute.
        """
        service = process.StandardIOService(None)
        service.setName("foo")
        self.assertEqual(service.name, "foo")


    def test_setServiceParent(self):
        """
        L{StandardIOService.setServiceParent} sets the C{parent} attribute and
        adds the service as a child of the given parent.
        """
        parent = MultiService()
        service = process.StandardIOService(None)
        service.setServiceParent(parent)
        self.assertEqual(list(parent), [service])
        self.assertIdentical(service.parent, parent)


    def test_disownServiceParent(self):
        """
        L{StandardIOService.disownServiceParent} sets the C{parent} attribute
        to C{None} and removes the service from the parent's child list.
        """
        parent = MultiService()
        service = process.StandardIOService(None)
        service.setServiceParent(parent)
        service.disownServiceParent()
        self.assertEqual(list(parent), [])
        self.assertIdentical(service.parent, None)
