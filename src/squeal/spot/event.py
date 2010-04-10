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

""" Events specific to spotify """

__author__ = "Doug Winter <doug.winter@isotoma.com>"
__docformat__ = "restructuredtext en"
__version__ = "$Revision$"[11:-2]

from zope.interface import implements
import ispotify

class SpotifyEvent(object):
    """ Basic event type """
    implements(ispotify.ISpotifyEvent)

class SpotifyEventWithError(object):
    """ Events that provide an error message """
    implements(ispotify.ISpotifyEvent)

    def __init__(self, error):
        self.error = error

class SpotifyEventWithMessage(object):
    """ Events that provide a message """
    implements(ispotify.ISpotifyEvent)

    def __init__(self, message):
        self.message = message

class SpotifySearchResults(object):
    implements(ispotify.ISpotifySearchResultsEvent)
    def __init__(self, results):
        self.results = results

