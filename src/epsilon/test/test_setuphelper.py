
import sys

from twisted.trial import unittest
from twisted.python import log
from twisted.python.reflect import namedAny
from epsilon.setuphelper import _regeneratePluginCache

class TestCacheRegeneration(unittest.TestCase):
    removeModules = []
    def setUp(self):
        self.removedModules = []
        for modname in self.removeModules:
            try:
                module = namedAny(modname)
                self.removedModules.append(module)
            except:
                print 'COULD NOT LOAD', modname
        self.sysmodules = sys.modules.copy()
        self.syspath = sys.path[:]

        for module in self.removedModules:
            for ent in self.syspath:
                if module.__file__.startswith(ent):
                    while ent in sys.path:
                        sys.path.remove(ent)
            rem = 0
            for modname in self.sysmodules:
                if modname.startswith(module.__name__):
                    rem += 1
                    sys.modules.pop(modname)
            assert rem, 'NO HITS: %r:%r' % (module,module.__name__)

    def testRegeneratingIt(self):
        for mod in self.removedModules:
            self.failIf(mod.__name__ in sys.modules, 'Started with %r loaded: %r' % (mod.__name__, sys.path))
        _regeneratePluginCache(['axiom', 'xmantissa'])
        log.flushErrors(ImportError) # This is necessary since there are Axiom
                                     # plugins that depend on Mantissa, so when
                                     # Axiom is installed, Mantissa-dependent
                                     # powerups are, but Mantissa isn't some
                                     # harmless tracebacks are printed.
        for mod in self.removedModules:
            self.failIf(mod.__name__ in sys.modules, 'Loaded %r: %r' % (mod.__name__, sys.path))

    testRegeneratingIt.skip = """
    This test really ought to be the dependency-direction test from old
    Quotient.  As it currently stands it's just broken.
    """

    def tearDown(self):
        sys.path[:] = self.syspath
        sys.modules.clear()
        sys.modules.update(self.sysmodules)

class WithoutAxiom(TestCacheRegeneration):
    removeModules = ['axiom']

class WithoutMantissa(TestCacheRegeneration):
    removeModules = ['xmantissa']

class WithoutEither(TestCacheRegeneration):
    removeModules = ['xmantissa', 'axiom']
