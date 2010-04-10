# Copright 2008 Divmod, Inc.  See LICENSE file for details.

"""
L{epsilon.expose} is a module which allows a system that needs to expose code
to a network endpoint do so in a manner which only exposes methods which have
been explicitly designated.  It provides utilities for convenient annotation
and lookup of exposed methods.
"""

from epsilon.structlike import record

from epsilon.expose import Exposer, MethodNotExposed, NameRequired

from twisted.trial.unittest import TestCase


class ExposeTests:
    """
    This mixin provides tests for expose, based on a parameterized base type
    for the class which methods are being exposed on.  Subclass this before
    L{TestCase} and set L{superClass} to use this.

    @ivar superClass: the class to be subclassed by all classes which expose
    methods.
    """

    superClass = None
    def setUp(self):
        """
        Create two exposers to expose methods in tests.
        """
        self.exposer = Exposer("test exposer")
        self.otherExposer = Exposer("other exposer")


    def test_exposeDocAttribute(self):
        """
        Creating an exposer should require a docstring explaining what it's
        for.
        """
        docstring = "This is my docstring."
        exposer = Exposer(docstring)
        self.assertEqual(exposer.__doc__, docstring)


    def test_simpleExpose(self):
        """
        Creating an exposer, defining a class and exposing a method of a class
        with that exposer, then retrieving a method of that class should result
        in the method of that class.
        """
        class Foo(self.superClass):
            def __init__(self, num):
                self.num = num

            @self.exposer.expose()
            def bar(self):
                return self.num + 1
        f = Foo(3)
        method = self.exposer.get(f, 'bar')
        self.assertEqual(method(), 4)


    def test_notExposed(self):
        """
        Creating an exposer and then attempting to retrieve a method not
        exposed with it should result in a L{MethodNotExposed} exception.
        """
        class Foo(self.superClass):
            def bar(self):
                return 1
        f = Foo()
        self.assertRaises(MethodNotExposed, self.exposer.get, f, 'bar')


    def test_differentMethodsDifferentExposers(self):
        """
        Methods should only be able to be retrieved with the exposer that
        exposed them, not with any other exposer.
        """
        class Foo(self.superClass):
            @self.exposer.expose()
            def bar(self):
                return 1
            @self.otherExposer.expose()
            def baz(self):
                return 2
        f = Foo()
        self.assertEqual(self.exposer.get(f, 'bar')(), 1)
        self.assertEqual(self.otherExposer.get(f, 'baz')(), 2)
        self.assertRaises(MethodNotExposed, self.otherExposer.get, f, 'bar')
        self.assertRaises(MethodNotExposed, self.exposer.get, f, 'baz')


    def test_sameMethodExposedByDifferentExposers(self):
        """
        If the same method is exposed by two different exposers, it should be
        accessible by both of them.
        """
        class Foo(self.superClass):
            @self.exposer.expose()
            @self.otherExposer.expose()
            def bar(self):
                return 4
        f = Foo()
        self.assertEqual(self.exposer.get(f, 'bar')(), 4)
        self.assertEqual(self.otherExposer.get(f, 'bar')(), 4)


    def test_exposeWithDifferentKey(self):
        """
        The 'key' argument to {Exposer.expose} should change the argument to
        'get'.
        """
        class Foo(self.superClass):
            @self.exposer.expose(key='hello')
            def bar(self):
                return 7
        f = Foo()
        self.assertEqual(self.exposer.get(f, 'hello')(), 7)


    def test_exposeOnDifferentClass(self):
        """
        An exposer should only be able to retrieve a method from instances of
        types which it has explicitly exposed methods on.  Instances of
        different types with the same method name should raise
        L{MethodNotExposed}.
        """
        class Foo(self.superClass):
            @self.exposer.expose()
            def bar(self):
                return 7
        class Baz(self.superClass):
            def bar(self):
                return 8
        f = Foo()
        b = Baz()
        self.assertEqual(self.exposer.get(f, 'bar')(), 7)
        self.assertRaises(MethodNotExposed, self.otherExposer.get, b, 'bar')


    def test_exposeUnnamedNoKey(self):
        """
        L{Exposer.expose} raises L{NameRequired} when called without a value
        for the C{key} parameter if it is used to decorate a non-function
        object.
        """
        def f():
            class Foo(self.superClass):
                @self.exposer.expose()
                @classmethod
                def foo(self):
                    pass
        self.assertRaises(NameRequired, f)


    def test_exposeNonMethod(self):
        """
        L{Exposer.expose} should work on methods which have been decorated by
        another decorator and will therefore not result in function objects
        when retrieved with __get__.
        """
        class Getter(record('function')):
            def __get__(self, oself, type):
                return self.function

        class Foo(self.superClass):
            @self.exposer.expose(key='bar')
            @Getter
            def bar():
                return 7

        f = Foo()
        # Sanity check
        self.assertEqual(f.bar(), 7)
        self.assertEqual(self.exposer.get(f, 'bar')(), 7)


    def test_descriptorGetsType(self):
        """
        L{Exposer.get} should not interfere with the appropriate type object
        being passed to the wrapped descriptor's C{__get__}.
        """
        types = []
        class Getter(record('function')):
            def __get__(self, oself, type):
                types.append(type)
                return self.function
        class Foo(self.superClass):
            @self.exposer.expose(key='bar')
            @Getter
            def bar():
                return 7
        f = Foo()
        self.exposer.get(f, 'bar')
        self.assertEqual(types, [Foo])


    def test_descriptorGetsSubtype(self):
        """
        When a descriptor is exposed through a superclass, getting it from a
        subclass results in the subclass being passed to the C{__get__} method.
        """
        types = []
        class Getter(record('function')):
            def __get__(self, oself, type):
                types.append(type)
                return self.function
        class Foo(self.superClass):
            @self.exposer.expose(key='bar')
            @Getter
            def bar():
                return 7
        class Baz(Foo):
            pass
        b = Baz()
        self.exposer.get(b, 'bar')
        self.assertEqual(types, [Baz])


    def test_implicitSubclassExpose(self):
        """
        L{Exposer.expose} should expose the given object on all subclasses.
        """
        class Foo(self.superClass):
            @self.exposer.expose()
            def bar(self):
                return 7
        class Baz(Foo):
            pass
        b = Baz()
        self.assertEqual(self.exposer.get(b, 'bar')(), 7)


    def test_overrideDontExpose(self):
        """
        L{Exposer.expose} should not expose overridden methods on subclasses.
        """
        class Foo(self.superClass):
            @self.exposer.expose()
            def bar(self):
                return 7
        class Baz(Foo):
            def bar(self):
                return 8
        b = Baz()
	self.assertRaises(MethodNotExposed, self.otherExposer.get, b, 'bar')


    def test_sameKeyOnDifferentTypes(self):
        """
        L{Exposer.expose} should work with the same key on different types.
        """
        class Foo(self.superClass):
            @self.exposer.expose()
            def bar(self):
                return 17
        class Qux(self.superClass):
            @self.exposer.expose()
            def bar(self):
                return 71
        q = Qux()
        f = Foo()
        self.assertEqual(self.exposer.get(q, 'bar')(), 71)
        self.assertEqual(self.exposer.get(f, 'bar')(), 17)


    def test_overrideReExpose(self):
        """
        L{Exposer.expose} should expose a method on a subclass if that method
        is overridden.
        """
        class Foo(self.superClass):
            @self.exposer.expose()
            def bar(self):
                return 7
        class Baz(Foo):
            @self.exposer.expose()
            def bar(self):
                return 8
        f = Foo()
        b = Baz()
        self.assertEqual(self.exposer.get(f, 'bar')(), 7)
        self.assertEqual(self.exposer.get(b, 'bar')(), 8)


    def test_deleteExposedAttribute(self):
        """
        When an exposed attribute is deleted from a class, it should no longer
        be exposed; calling L{Exposer.get} should result in
        L{MethodNotExposed}.
        """
        class Foo(self.superClass):
            @self.exposer.expose()
            def bar(self):
                return 7
        f = Foo()
        del Foo.bar
        self.assertRaises(MethodNotExposed, self.otherExposer.get, f, 'bar')



class ExposeNewStyle(ExposeTests, TestCase):
    """
    All of the above functionality should work on new-style classes.
    """
    superClass = object


class Classic:
    """
    A dummy classic class.
    """


class ExposeOldStyle(ExposeTests, TestCase):
    """
    All of the above functionality should work on old-style classes.
    """
    superClass = Classic
