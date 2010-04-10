
import sys
import os

from os.path import join as opj

projectName = sys.argv[1]

topDir = projectName.capitalize()
codeDir = projectName.lower()

os.mkdir(topDir)
os.mkdir(opj(topDir, codeDir))

file(opj(topDir, codeDir, '__init__.py'), 'w').write("""
# Don't put code here.
from twisted.python.versions import Version
version = Version(%r, 0, 0, 1)

""" %(codeDir,))

file(opj(topDir, codeDir, codeDir+'_model.py'),
     'w').write("""

from axiom.item import Item
from axiom.attributes import text, bytes, integer, reference

class %sStart(Item):
    schemaVersion = 1           # First version of this object.
    typeName = '%s_start'       # Database table name.

    name = text()               # We must have at least one attribute - model
                                # objects must store data.

    def explode(self):
        raise Exception('these should fail until you write some tests!')

""" % (topDir, codeDir))

os.mkdir(opj(topDir, codeDir, 'test'))

file(opj(topDir, codeDir, 'test', '__init__.py'), 'w').write(
    "# Don't put code here.")

file(opj(topDir, codeDir, 'test', 'test_'+codeDir+'.py'),
     'w').write("""

from axiom.store import Store

from twisted.trial import unittest
from %s import %s_model

class BasicTest(unittest.TestCase):
    def setUp(self):
        self.store = Store()

    def testUserWroteTests(self):
        o = %s_model.%sStart(store=self.store,
                    name=u'Test Object')
        self.assertEquals(1, 0)
        o.explode()

    def tearDown(self):
        self.store.close()

""" % (codeDir, codeDir, codeDir, topDir))

