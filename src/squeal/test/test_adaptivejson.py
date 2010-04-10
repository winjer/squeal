
from zope.interface import Interface, implements
from twisted.python.components import Adapter, registerAdapter
import unittest

from squeal.adaptivejson import IJsonAdapter, loads, dumps, simplify

class Frob(object):

    def __init__(self, foo, bar, baz):
        self.foo  = foo
        self.bar = bar
        self.baz = baz

class FrobJSONAdapter(Adapter):

    def encode(self):
        return {
            u'foo': unicode(self.original.foo),
            u'bar': unicode(self.original.bar),
            u'baz': unicode(self.original.baz),
        }

registerAdapter(FrobJSONAdapter, Frob, IJsonAdapter)

class TestAdaptiveJson(unittest.TestCase):

    def test_encoding(self):
        f = Frob("qux", "quux", "corge")
        json = dumps(f)
        self.assertEqual(json, '{"baz": "corge", "foo": "qux", "bar": "quux"}')

    def test_compound(self):
        f = [10, 20, Frob("qux", "quux", "corge")]
        json = dumps(f)
        self.assertEqual(json, '[10, 20, {"baz": "corge", "foo": "qux", "bar": "quux"}]')

    def test_simplify(self):
        f = Frob("qux", "quux", "corge")
        self.assertEqual(simplify(f), {u'baz': u'corge', u'foo': u'qux', u'bar': u'quux'})

