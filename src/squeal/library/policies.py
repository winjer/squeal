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

""" Policies for how to name tracks, based on their filename, path and tags.
"""

__author__ = "Doug Winter <doug.winter@isotoma.com>"
__docformat__ = "restructuredtext en"
__version__ = "$Revision$"[11:-2]


import os
import magic
import tagpy
import stat
from itertools import cycle

from zope.interface import implements
from axiom.item import Item
from axiom.attributes import text

from ilibrary import INamingPolicy

class StandardPolicyMixin:

    """ Extracts details from tags and from the pathname assuming the path is of the form:

        /artist/album/num - track

        or similar formats. The pathname is considered to be more trustworthy
        than the tags, as long as the pathname is of that form, or similar.
        """

    tags = ['artist', 'album', 'comment', 'genre', 'title', 'track', 'year', 'duration']

    def detailsFromPath(self, pathname):
        if type(pathname) is not unicode:
            pathname = pathname.decode("utf-8")
        def normalise(s):
            return s.replace("_", " ")
        segments = pathname.split("/")
        parts = segments.pop(-1).split(".", 1)[0].split("-")
        details = dict(zip(self.tags, cycle([None])))
        if len(parts) == 1:
            details['track'] = None
            details['title'] = normalise(parts[0])
        elif len(parts) == 2:
            try:
                details['track'] = int(parts[0])
            except ValueError:
                # assume it's the artist at 0
                details['track'] = None
            details['title'] = normalise(parts[1])
        if len(segments) == 0:
            pass
        elif len(segments) == 1:
                details['album'] = normalise(segments[0])
        elif len(segments) == 2:
                details['artist'] = normalise(segments[0])
                details['album'] = normalise(segments[1])
        else:
            details['artist'] = normalise(segments[-2])
            details['album'] = normalise(segments[-1])
        return details

    def detailsFromTags(self, pathname):
        f = tagpy.FileRef(pathname.encode("UTF-8"))
        if f.isNull():
            return None
        t = f.tag()
        return {
            'artist': t.artist,
            'album': t.album,
            'comment': t.comment,
            'genre': t.genre,
            'title': t.title,
            'track': t.track,
            'year': unicode(t.year),
            'duration': f.file().audioProperties().length * 1000,
            }

class StandardNamingPolicy(Item, StandardPolicyMixin):

    implements(INamingPolicy)

    wins = text(default=u'path') # who wins.  "path" or "tags"

    def details(self, collection, pathname):
        pathd = self.detailsFromPath(os.path.join(collection.pathname, pathname))
        try:
            tagsd = self.detailsFromTags(pathname)
        except ValueError:
            tagsd = None
        details = {}
        for t in self.tags:
            if tagsd is None:
                details[t] = pathd[t]
            elif pathd[t] is None:
                details[t] = tagsd[t]
            elif tagsd[t] is None:
                details[t] = pathd[t]
            elif tagsd[t] == pathd[t]:
                details[t] = tagsd[t]
            elif self.wins == 'tags':
                details[t] = tagsd[t]
            elif self.wins == 'path':
                details[t] = pathd[t]
            else:
                raise NotImplementedError
        return details
