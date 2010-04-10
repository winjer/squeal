"""
Tests for L{epsilon.descriptor}.
"""

from twisted.trial import unittest

from epsilon import descriptor

class Test1(object):
    class a(descriptor.attribute):
        def get(self):
            return 1
        def set(self, value):
            pass
        def delete(self):
            pass


class Test2(object):
    class a(descriptor.attribute):
        "stuff"
        def get(self):
            return 10


class DescriptorTest(unittest.TestCase):
    def testCase1(self):
        t = Test1()
        self.assertEquals(t.a, 1)
        t.a = 2
        self.assertEquals(t.a, 1)
        del t.a
        self.assertEquals(t.a, 1)


    def testCase2(self):
        t = Test2()
        self.assertEquals(Test2.a.__doc__, 'stuff')
        self.assertEquals(t.a, 10)
        self.assertRaises(AttributeError, setattr, t, 'a', 1)
        self.assertRaises(AttributeError, delattr, t, 'a')



class AbstractClassic:
    """
    Toy classic class used by L{RequiredAttributeTestCase}.
    """
    foo = descriptor.requiredAttribute('foo')
    bar = descriptor.requiredAttribute('bar')


class ManifestClassic(AbstractClassic):
    """
    Toy classic class used by L{RequiredAttributeTestCase}.
    """
    foo = 'bar'



class AbstractNewStyle(object):
    """
    Toy new-style class used by L{RequiredAttributeTestCase}.
    """
    foo = descriptor.requiredAttribute('foo')
    bar = descriptor.requiredAttribute('bar')



class ManifestNewStyle(AbstractNewStyle):
    """
    Toy classic class used by L{RequiredAttributeTestCase}.
    """
    foo = 'bar'



class RequiredAttributeTestCase(unittest.TestCase):
    """
    Tests for L{descriptor.requiredAttribute}.
    """
    def _defaultAccess(self, abstractFoo):
        exception = self.assertRaises(AttributeError, getattr, abstractFoo, 'foo')
        self.assertEqual(len(exception.args), 1)
        self.assertEqual(
            exception.args[0],
            ("Required attribute 'foo' has not been changed"
                " from its default value on %r" % (abstractFoo,)))

    def test_defaultAccessClassic(self):
        """
        Accessing a L{descriptor.requiredAttribute} on a classic class raises
        an C{AttributeError} if its value has not been overridden.
        """
        abstractFoo = AbstractClassic()
        self._defaultAccess(abstractFoo)


    def test_defaultAccessNewStyle(self):
        """
        Accessing a L{descriptor.requiredAttribute} on a new-style class raises
        an C{AttributeError} if its value has not been overridden.
        """
        abstractFoo = AbstractNewStyle()
        self._defaultAccess(abstractFoo)


    def _derivedAccess(self, manifestFoo):
        self.assertEqual(manifestFoo.foo, 'bar')


    def test_derivedAccessClassic(self):
        """
        If a derived classic class sets a new value for a
        L{descriptor.requiredAttribute}, things should work fine.
        """
        manifestFoo = ManifestClassic()
        self._derivedAccess(manifestFoo)


    def test_derivedAccessNewStyle(self):
        """
        If a new-style derived class sets a new value for a
        L{descriptor.requiredAttribute}, things should work fine.
        """
        manifestFoo = ManifestNewStyle()
        self._derivedAccess(manifestFoo)


    def _instanceAccess(self, abstractMadeManifest):
        abstractMadeManifest.foo = 123
        self.assertEqual(abstractMadeManifest.foo, 123)


    def test_instanceAccessClassic(self):
        """
        Accessing a L{descriptor.requiredAttribute} after setting a value for
        it on an instance of a classic class evaluates to that value.
        """
        abstractMadeManifest = AbstractClassic()
        self._instanceAccess(abstractMadeManifest)


    def test_instanceAccessNewStyle(self):
        """
        Accessing a L{descriptor.requiredAttribute} after setting a value for
        it on an instance of a new-style class evaluates to that value.
        """
        abstractMadeManifest = AbstractNewStyle()
        self._instanceAccess(abstractMadeManifest)


    def test_instanceAttributesUnrelatedClassic(self):
        """
        Accessing one L{descriptor.requiredAttribute} after setting a value for
        a different L{descriptor.requiredAttribute} raises an
        L{AttributeError}.
        """
        partiallyAbstract = AbstractClassic()
        partiallyAbstract.bar = 123
        self._defaultAccess(partiallyAbstract)


    def test_instanceAttributesUnrelatedNewStyle(self):
        """
        Accessing one L{descriptor.requiredAttribute} after setting a value for
        a different L{descriptor.requiredAttribute} raises an
        L{AttributeError}.
        """
        partiallyAbstract = AbstractNewStyle()
        partiallyAbstract.bar = 123
        self._defaultAccess(partiallyAbstract)
