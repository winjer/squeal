# coding=utf-8
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

""" Automated unit tests for squeal.library.policies """

__author__ = "Doug Winter <doug.winter@isotoma.com>"
__docformat__ = "restructuredtext en"
__version__ = "$Revision$"[11:-2]

from twisted.trial import unittest
from squeal.library import policies
from itertools import cycle

trackName = u"example £5 track"
trackPart = trackName.replace(" ", "_").encode("utf-8")
albumName = u"€50 for unicode victory"
albumPart = albumName.replace(" ", "_").encode("utf-8")
artistName = u"fifty cent"
artistPart = artistName.replace(" ", "_").encode("utf-8")

class TestStandardNamingPolicy(unittest.TestCase):

    def setUp(self):
        self.policy = policies.StandardPolicyMixin()
        self._p = self.policy.detailsFromPath
        self._t = self.policy.detailsFromTags
        self.details = dict(zip(self.policy.tags, cycle([None])))

    def test_path_title_only(self):
        self.details["title"] = trackName
        self.assertEqual(self._p(trackPart), self.details)

    def test_path_title_only_unicode(self):
        self.details["title"] = trackName
        self.assertEqual(self._p(trackName), self.details)

    def test_path_track_title(self):
        self.details["track"] = 4
        self.details["title"] = trackName
        self.assertEqual(self._p("04-%s" % trackPart), self.details)

    def test_path_invalid_track_title(self):
        self.details["title"] = trackName
        self.assertEqual(self._p("xx-%s" % trackPart), self.details)

    def test_path_album_title(self):
        self.details["album"] = albumName
        self.details["title"] = trackName
        self.assertEqual(self._p("%s/%s" % (albumPart, trackPart)), self.details)

    def test_path_album_track_title(self):
        self.details["track"] = 4
        self.details["album"] = albumName
        self.details["title"] = trackName
        self.assertEqual(self._p("%s/04-%s" % (albumPart, trackPart)), self.details)

    def test_path_artist_album_title(self):
        self.details["artist"] = artistName
        self.details["album"] = albumName
        self.details["title"] = trackName
        self.assertEqual(self._p("%s/%s/%s" % (artistPart, albumPart, trackPart)), self.details)

    def test_path_artist_album_track_title(self):
        self.details["track"] = 4
        self.details["artist"] = artistName
        self.details["album"] = albumName
        self.details["title"] = trackName
        self.assertEqual(self._p("%s/%s/04-%s" % (artistPart, albumPart, trackPart)), self.details)

    def test_path_junk_artist_album_track_title(self):
        self.details["track"] = 4
        self.details["artist"] = artistName
        self.details["album"] = albumName
        self.details["title"] = trackName
        self.assertEqual(self._p("foo/bar/baz/%s/%s/04-%s" % (artistPart, albumPart, trackPart)), self.details)
