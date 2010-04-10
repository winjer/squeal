"""
Tests for L{epsilon.caseless}.
"""

import sys
from twisted.trial.unittest import TestCase
from epsilon.caseless import Caseless

class CaselessTestCase(TestCase):
    """
    Tests for L{Caseless}.
    """

    def _casings(s):
        """
        Generate variously cased versions of the given string.
        """
        yield s.lower()
        yield s.upper()
        yield s.title()
        yield s.title().swapcase()
    _casings = staticmethod(_casings)

    def _strings(self):
        """
        Generate a variety of C{str} and C{unicode} test samples.
        """
        for t in [str, unicode]:
            yield t()
            for s in self._casings('foo'):
                yield t(s)


    def test_cased(self):
        """
        L{Caseless} should expose the wrapped string as C{cased}.
        """
        for s in self._strings():
            self.assertIdentical(Caseless(s).cased, s)


    def test_idempotence(self):
        """
        L{Caseless} should be idempotent.
        """
        for s in self._strings():
            self.assertIdentical(Caseless(Caseless(s)).cased, s)


    def test_repr(self):
        """
        L{Caseless} should implement L{repr}.
        """
        for s in self._strings():
            self.assertEquals(repr(Caseless(s)), 'Caseless(%r)' % s)


    def test_str(self):
        """
        L{Caseless} should delegate L{str}.
        """
        for s in self._strings():
            self.assertEquals(str(Caseless(s)), str(s))


    def test_unicode(self):
        """
        L{Caseless} should delegate L{unicode}.
        """
        for s in self._strings():
            self.assertEquals(unicode(Caseless(s)), unicode(s))


    def test_len(self):
        """
        L{Caseless} should delegate L{len}.
        """
        for s in self._strings():
            self.assertEquals(len(Caseless(s)), len(s))


    def test_getitem(self):
        """
        L{Caseless} should delegate indexing/slicing.
        """
        for s in self._strings():
            for i in xrange(len(s)):
                self.assertEquals(Caseless(s)[i], s[i])
                self.assertEquals(Caseless(s)[:i], s[:i])
                self.assertEquals(Caseless(s)[i:], s[i:])
            self.assertEquals(Caseless(s)[::-1], s[::-1])


    def test_iter(self):
        """
        L{Caseless} should delegate L{iter}.
        """
        for s in self._strings():
            self.assertEquals(list(iter(Caseless(s))), list(iter(s)))


    def test_lower(self):
        """
        L{Caseless} should delegate C{lower}.
        """
        for s in self._strings():
            self.assertEquals(Caseless(s).lower(), s.lower())


    def test_upper(self):
        """
        L{Caseless} should delegate C{upper}.
        """
        for s in self._strings():
            self.assertEquals(Caseless(s).upper(), s.upper())


    def test_title(self):
        """
        L{Caseless} should delegate C{title}.
        """
        for s in self._strings():
            self.assertEquals(Caseless(s).title(), s.title())


    def test_swapcase(self):
        """
        L{Caseless} should delegate C{swapcase}.
        """
        for s in self._strings():
            self.assertEquals(Caseless(s).swapcase(), s.swapcase())


    def test_comparison(self):
        """
        L{Caseless} should implement comparison and hashing case-insensitively.
        """
        for a in map(Caseless, self._casings(u'abc')):
            for b in map(Caseless, self._casings(u'abc')):
                self.assertEquals(a, b)
                self.assertEquals(hash(a), hash(b))
                self.assertEquals(cmp(a, b), 0)
        for a in map(Caseless, self._casings(u'abc')):
            for b in map(Caseless, self._casings(u'abd')):
                self.assertNotEquals(a, b)
                self.assertNotEquals(hash(a), hash(b))
                self.assertEquals(cmp(a, b), -1)


    def test_contains(self):
        """
        L{Caseless} should search for substrings case-insensitively.
        """
        for a in map(Caseless, self._casings(u'abc')):
            for b in map(Caseless, self._casings(u'{{{abc}}}')):
                self.assertIn(a, b)
        for a in map(Caseless, self._casings(u'abc')):
            for b in map(Caseless, self._casings(u'{{{abd}}}')):
                self.assertNotIn(a, b)


    def test_startswith(self):
        """
        L{Caseless} should implement C{startswith} case-insensitively.
        """
        for a in map(Caseless, self._casings(u'abcbabcba')):
            for b in self._casings(u'abc'):
                self.assertTrue(a.startswith(b))
                self.assertTrue(a.startswith(b, 4))
                self.assertFalse(a.startswith(b, 2))
                self.assertFalse(a.startswith(b, 4, 6))
        for a in map(Caseless, self._casings(u'abcbabcba')):
            for b in self._casings(u'cba'):
                self.assertFalse(a.startswith(b))
                self.assertFalse(a.startswith(b, 4))
                self.assertTrue(a.startswith(b, 2))
                self.assertFalse(a.startswith(b, 4, 6))


    def test_endswith(self):
        """
        L{Caseless} should implement C{endswith} case-insensitively.
        """
        for a in map(Caseless, self._casings(u'abcbabcba')):
            for b in self._casings(u'cba'):
                self.assertTrue(a.endswith(b))
                self.assertTrue(a.endswith(b, 0, 5))
                self.assertFalse(a.endswith(b, 0, 3))
                self.assertFalse(a.endswith(b, 7))
        for a in map(Caseless, self._casings(u'abcbabcba')):
            for b in self._casings(u'abc'):
                self.assertFalse(a.endswith(b))
                self.assertFalse(a.endswith(b, 0, 5))
                self.assertTrue(a.endswith(b, 0, 3))
                self.assertFalse(a.endswith(b, 7))


    def test_startswithTuple(self):
        """
        L{test_startswith} with tuple arguments.
        """
        for a in map(Caseless, self._casings(u'abcbabcba')):
            for b in self._casings(u'abc'):
                self.assertTrue(a.startswith((u'foo', b, u'bar')))
                self.assertTrue(a.startswith((u'foo', b, u'bar'), 4))
                self.assertFalse(a.startswith((u'foo', b, u'bar'), 2))
                self.assertFalse(a.startswith((u'foo', b, u'bar'), 4, 6))
        for a in map(Caseless, self._casings(u'abcbabcba')):
            for b in self._casings(u'cba'):
                self.assertFalse(a.startswith((u'foo', b, u'bar')))
                self.assertFalse(a.startswith((u'foo', b, u'bar'), 4))
                self.assertTrue(a.startswith((u'foo', b, u'bar'), 2))
                self.assertFalse(a.startswith((u'foo', b, u'bar'), 4, 6))


    def test_endswithTuple(self):
        """
        L{test_endswith} with tuple arguments.
        """
        for a in map(Caseless, self._casings(u'abcbabcba')):
            for b in self._casings(u'cba'):
                self.assertTrue(a.endswith((u'foo', b, u'bar')))
                self.assertTrue(a.endswith((u'foo', b, u'bar'), 0, 5))
                self.assertFalse(a.endswith((u'foo', b, u'bar'), 0, 3))
                self.assertFalse(a.endswith((u'foo', b, u'bar'), 7))
        for a in map(Caseless, self._casings(u'abcbabcba')):
            for b in self._casings(u'abc'):
                self.assertFalse(a.endswith((u'foo', b, u'bar')))
                self.assertFalse(a.endswith((u'foo', b, u'bar'), 0, 5))
                self.assertTrue(a.endswith((u'foo', b, u'bar'), 0, 3))
                self.assertFalse(a.endswith((u'foo', b, u'bar'), 7))

    if sys.version_info < (2, 5):
        test_startswithTuple.skip = test_endswithTuple.skip = (
            'Tuple arguments implemented in Python 2.5')


    def test_count(self):
        """
        L{Caseless} should implement C{count} case-insensitively.
        """
        for a in map(Caseless, self._casings(u'abcbabcba')):
            self.assertEquals(a.count(u'foo'), 0)
            for b in self._casings(u'cba'):
                self.assertEquals(a.count(b), 2)
                self.assertEquals(a.count(b, 2), 2)
                self.assertEquals(a.count(b, 3), 1)
                self.assertEquals(a.count(b, 0, 4), 0)


    def test_findindex(self):
        """
        L{Caseless} should implement C{find}/C{index} case-insensitively.
        """
        def assertFound(a, b, result, rest=()):
            self.assertEquals(a.find(b, *rest), result)
            self.assertEquals(a.index(b, *rest), result)
        def assertNotFound(a, b, rest=()):
            self.assertEquals(a.find(b, *rest), -1)
            err = self.assertRaises(ValueError, lambda: a.index(b, *rest))
            self.assertEquals(str(err), 'substring not found')

        for a in map(Caseless, self._casings(u'abcbabcba')):
            assertNotFound(a, u'foo')
            for b in self._casings(u'abc'):
                assertFound(a, b, result=0)
                assertFound(a, b, rest=(1,), result=4)
                assertNotFound(a, b, rest=(1, 6))


    def test_rfindindex(self):
        """
        L{Caseless} should implement C{rfind}/C{rindex} case-insensitively.
        """
        def assertFound(a, b, result, rest=()):
            self.assertEquals(a.rfind(b, *rest), result)
            self.assertEquals(a.rindex(b, *rest), result)
        def assertNotFound(a, b, rest=()):
            self.assertEquals(a.rfind(b, *rest), -1)
            err = self.assertRaises(ValueError, lambda: a.rindex(b, *rest))
            self.assertEquals(str(err), 'substring not found')

        for a in map(Caseless, self._casings(u'abcbabcba')):
            assertNotFound(a, u'foo')
            for b in self._casings(u'cba'):
                assertFound(a, b, result=6)
                assertFound(a, b, rest=(0, 8), result=2)
                assertNotFound(a, b, rest=(7,))


__doctests__ = ['epsilon.caseless']
