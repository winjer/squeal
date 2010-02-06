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

""" Interfaces for spotify services. """

__author__ = "Doug Winter <doug.winter@isotoma.com>"
__docformat__ = "restructuredtext en"
__version__ = "$Revision$"[11:-2]


from zope.interface import Interface, Attribute

from squeal import isqueal

class ISpotifyEvent(Interface):
    """ Any spotify event """

class ISpotifyLoggedInEvent(ISpotifyEvent):
    """ We have logged into spotify successfully. """

class ISpotifyLoggedOutEvent(ISpotifyEvent):
    """ We have been logged out of spotify """

    error = Attribute("""The error that caused us to be logged out. """)

class ISpotifyMetadataUpdatedEvent(ISpotifyEvent, isqueal.IMetadataChangeEvent):
    """ Spotify metadata has been updated. """

class ISpotifyConnectionErrorEvent(ISpotifyEvent):
    """ Connection error """

class ISpotifyMessageToUserEvent(ISpotifyEvent):
    """ Message specifically to the user (for example, invites available) """

class ISpotifyLogMessageEvent(ISpotifyEvent):
    """ Log message, for operator consumption not for the user """

class ISpotifyEndOfTrackEvent(ISpotifyEvent):
    """ The track has been completed.  Will happen long before it finishes playing normally. """

class ISpotifyPlayTokenLostEvent(ISpotifyEvent):
    """ Play token has been lost """

class ISpotifySearchResultsEvent(ISpotifyEvent):
    """ A search has completed """

