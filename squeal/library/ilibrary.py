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

""" Local music library interface definitions. """

__author__ = 'Doug Winter <doug.winter@isotoma.com>'
__docformat__ = 'restructuredtext en'
__version__ = '$Revision$'[11:-2]


from zope.interface import Interface, Attribute
from twisted.plugin import IPlugin


class ILibrary(Interface):
    """ The music library management service. """

    def add_collection(pathname):
        """ Add the files in the specified path to the library. The files are
        not moved or copied, but references to their paths are kept within the
        collection database. """

    def tracks():
        """ Return an iterator of all tracks in the library """

    def rescan():
        """ Rescan every track in the library """

class INamingPolicy(Interface):

    """ Returns a set of details on a track. Different policies will make
    different decisions on naming (for example tags win or filename wins) """

    def details(collection, pathname):
        """ returns a dictionary of track details """

class ILibraryEvent(Interface):

    """ Any event that represents a change to the library """

class ILibraryChangeEvent(Interface):

    """ The library has changed.  This provides a list of all the tracks that have changed or been removed """

    added = Attribute(""" A list of tracks that have been added """)
    removed = Attribute(""" A list of tracks that have been removed """)
    changed = Attribute(""" A list of tracks that have changed """)

class ILibraryStatusEvent(Interface):

    """ The status of the library has changed """

    status = Attribute(""" either 'scanning' or 'not scanning' """)

