# Copyright 2010 Doug Winter
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

""" Automated unit tests for squeal.library.record. """

__author__ = "Doug Winter <doug.winter@isotoma.com>"
__docformat__ = "restructuredtext en"
__version__ = "$Revision$"[11:-2]

import os

from twisted.python.util import sibpath
from twisted.trial import unittest
from squeal.library import record
from epsilon.extime import Time
from axiom.store import Store

class TestCollection(unittest.TestCase):

    def setUp(self):
        self.store = Store()
        self.c = record.Collection(store=self.store, pathname=u"colltest")

    def test_file_type(self):
        files = sibpath(__file__, "files")
        for t, i in [('flac', 2), ('mp3', 1), ('ogg', 0), ('wav', 3)]:
            pathname = os.path.join(files, "la.%s" % t)
            self.assertEqual(self.c.file_type(pathname), i)

    def test_generate_changed_paths(self):
        self.c.last = Time().fromPOSIXTimestamp(1000)
        os.mkdir("colltest")
        correct = []
        for d in 1, 2, 3:
            dirpath = os.path.join("colltest", "dir%d" % d)
            os.mkdir(dirpath)
            for f in 500, 600, 1200, 2400:
                filepath = os.path.join(dirpath, "file%d"  %f)
                open(filepath, "w")
                os.utime(filepath, (0, f))
                if f > 1000:
                    correct.append(filepath)
        changed = list(self.c._generate_changed_paths())
        self.assertEqual(sorted(changed), sorted(correct))

