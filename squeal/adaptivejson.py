# $Id$
#
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

"""
A mechanism for specifying jsonification for any class using an adapter.
"""

__author__ = 'Doug Winter <doug.winter@isotoma.com>'
__docformat__ = 'restructuredtext en'
__version__ = '$Revision$'[11:-2]

from zope.interface import Interface, implements
import simplejson

class IJsonAdapter(Interface):

    """ This is a JSON Encoder. When it's encode method is called with a
    python object, it will return a simplified python representation of the
    object, suitable for further JSONification by other components. The class
    that implements this should in general be a subclass of
    twisted.python.components.Adapter. """

    def encode(obj):
        """ Encode the provided object, and return a JSON representation. """


class JSONEncoder(simplejson.JSONEncoder):
    def default(self, obj):
        adapter = IJsonAdapter(obj, None)
        if adapter:
            return adapter.encode()
        else:
            return simplejson.JSONEncoder.default(self, obj)

def dumps(*a, **kw):
    return simplejson.dumps(*a, cls=JSONEncoder, **kw)

def loads(*a, **kw):
    return simplejson.loads(*a, **kw)

