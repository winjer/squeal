
"""
Tests for L{epsilon.structlike}.
"""

import threading

from twisted.trial import unittest
from twisted.internet.threads import deferToThread
from twisted.internet.defer import gatherResults
from epsilon.structlike import record


class MyRecord(record('something somethingElse')):
    """
    A sample record subclass.
    """



class StructLike(unittest.TestCase):
    def _testme(self, TestStruct):
        x = TestStruct()
        self.assertEquals(x.x, 1)
        self.assertEquals(x.y, 2)
        self.assertEquals(x.z, 3)

        y = TestStruct('3', '2', '1')
        self.assertEquals(y.x, '3')
        self.assertEquals(y.y, '2')
        self.assertEquals(y.z, '1')

        z = TestStruct(z='z', x='x', y='y')
        self.assertEquals(z.x, 'x')
        self.assertEquals(z.y, 'y')
        self.assertEquals(z.z, 'z')

        a = TestStruct('abc')
        self.assertEquals(a.x, 'abc')
        self.assertEquals(a.y, 2)
        self.assertEquals(a.z, 3)

        b = TestStruct(y='123')
        self.assertEquals(b.x, 1)
        self.assertEquals(b.y, '123')
        self.assertEquals(b.z, 3)

    def testWithPositional(self):
        self._testme(record('x y z', x=1, y=2, z=3))

    def testWithPositionalSubclass(self):
        class RecordSubclass(record('x y z', x=1, y=2, z=3)):
            pass
        self._testme(RecordSubclass)

    def testWithoutPositional(self):
        self._testme(record(x=1, y=2, z=3))

    def testWithoutPositionalSubclass(self):
        class RecordSubclass(record(x=1, y=2, z=3)):
            pass
        self._testme(RecordSubclass)

    def testBreakRecord(self):
        self.assertRaises(TypeError, record)
        self.assertRaises(TypeError, record, 'a b c', a=1, c=2)
        self.assertRaises(TypeError, record, 'a b', c=2)
        self.assertRaises(TypeError, record, 'a b', a=1)

    def testUndeclared(self):
        R = record('a')
        r = R(1)
        r.foo = 2
        self.assertEquals(r.foo, 2)

    def testCreateWithNoValuesAndNoDefaults(self):
        R = record('x')
        self.assertRaises(TypeError, R)

    def testUnknownArgs(self):
        """
        Test that passing in unknown keyword and / or positional arguments to a
        record's initializer causes TypeError to be raised.
        """
        R = record('x')
        self.assertRaises(TypeError, R, x=5, y=6)
        self.assertRaises(TypeError, R, 5, 6)


    def test_typeStringRepresentation(self):
        """
        'Record' types should have a name which provides information about the
        slots they contain.
        """
        R = record('xyz abc def')
        self.assertEquals(R.__name__, "Record<xyz abc def>")


    def test_instanceStringRepresentation(self):
        """
        'Record' instances should provide a string representation which
        provides information about the values contained in their slots.
        """
        obj = MyRecord(something=1, somethingElse=2)
        self.assertEquals(repr(obj), 'MyRecord(something=1, somethingElse=2)')


    def test_instanceStringRepresentationNesting(self):
        """
        Nested L{Record} instances should have nested string representations.
        """
        obj = MyRecord(something=1, somethingElse=2)
        objRepr = 'MyRecord(something=1, somethingElse=2)'
        self.assertEquals(
            repr(MyRecord(obj, obj)),
            'MyRecord(something=%s, somethingElse=%s)' % (objRepr, objRepr))


    def test_instanceStringRepresentationRecursion(self):
        """
        'Record' instances should provide a repr that displays 'ClassName(...)'
        when it would otherwise infinitely recurse.
        """
        obj = MyRecord(something=1, somethingElse=2)
        obj.somethingElse = obj
        self.assertEquals(
            repr(obj), 'MyRecord(something=1, somethingElse=MyRecord(...))')


    def test_instanceStringRepresentationUnhashableRecursion(self):
        """
        'Record' instances should display 'ClassName(...)' even for unhashable
        objects.
        """
        obj = MyRecord(something=1, somethingElse=[])
        obj.somethingElse.append(obj)
        self.assertEquals(
            repr(obj), 'MyRecord(something=1, somethingElse=[MyRecord(...)])')


    def test_threadLocality(self):
        """
        An 'Record' repr()'d in two separate threads at the same time should
        look the same (i.e. the repr state tracking for '...' should be
        thread-local).
        """
        class StickyRepr(object):
            """
            This has a __repr__ which will block until a separate thread
            notifies it that it should return.  We use this to create a race
            condition.
            """
            waited = False
            def __init__(self):
                self.set = threading.Event()
                self.wait = threading.Event()
            def __repr__(self):
                if not self.waited:
                    self.set.set()
                    self.wait.wait()
                return 'sticky'
        r = StickyRepr()
        mr = MyRecord(something=1, somethingElse=r)
        d = deferToThread(repr, mr)
        def otherRepr():
            # First we wait for the first thread doing a repr() to enter its
            # __repr__()...
            r.set.wait()
            # OK, now it's blocked.  Let's make sure that subsequent calls to
            # this repr() won't block.
            r.waited = True
            # Do it!  This is a concurrent repr().
            result = repr(mr)
            # Now we're done, wake up the other repr and let it complete.
            r.wait.set()
            return result
        d2 = deferToThread(otherRepr)

        def done((thread1repr, thread2repr)):
            knownGood = 'MyRecord(something=1, somethingElse=sticky)'
            # self.assertEquals(thread1repr, thread2repr)
            self.assertEquals(thread1repr, knownGood)
            self.assertEquals(thread2repr, knownGood)
        return gatherResults([d, d2]).addCallback(done)


