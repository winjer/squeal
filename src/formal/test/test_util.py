from twisted.trial import unittest
from formal import util


class TestUtil(unittest.TestCase):

    def test_validIdentifier(self):
        self.assertEquals(util.validIdentifier('foo'), True)
        self.assertEquals(util.validIdentifier('_foo'), True)
        self.assertEquals(util.validIdentifier('_foo_'), True)
        self.assertEquals(util.validIdentifier('foo2'), True)
        self.assertEquals(util.validIdentifier('Foo'), True)
        self.assertEquals(util.validIdentifier(' foo'), False)
        self.assertEquals(util.validIdentifier('foo '), False)
        self.assertEquals(util.validIdentifier('9'), False)
    test_validIdentifier.todo = "Fails due to weird import poblem"

