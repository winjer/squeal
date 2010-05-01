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

""" Global interface definitions. """

__author__ = 'Doug Winter <doug.winter@isotoma.com>'
__docformat__ = 'restructuredtext en'
__version__ = '$Revision$'[11:-2]


from zope.interface import Interface, Attribute
from twisted.plugin import IPlugin

#### Core services

class ISlimPlayerService(Interface):
    """ The player management service.  This manages the connection of players to the server. """

    def play(track):
        """ Play the specified track.  The track should provide the ITrack interface. """

class IPlaylist(Interface):
    """ The playlist management service """

    def clear():
        """ Delete all tracks from this playlist completely. """

    def play():
        """ Start playing - either resume the currently loaded track, if it
        has time left to run, or load the next track and play that. """

    def stop():
        """ Stop playing all players. """

    def enqueue(track):
        """ Add the specified track to the end of the playlist. The Track
        should provide the ISerializableTrack interface. """

class IWebService(Interface):
    """ The web service, that manages the creation of the web site. """

class IDiscoveryService(Interface):
    """ Manages the UDP Discovery protocol for attaching new players. """

class IEventReactor(Interface):
    """ Handles subscribers to events, so the different services can communicate easily. """

#### End of core services

################################################################################
# Events
################################################################################

# Player events

class IPlayerEvent(Interface):

    """ Any event that represents a change of state on a player """

    player = Attribute(""" The local player instance representation """)

class IVolumeChangeEvent(IPlayerEvent):

    """ The volume has changed """

    volume = Attribute(""" The new volume """)

class IRemoteButtonPressedEvent(IPlayerEvent):
    """ A button has been pressed on the remote control """

    button = Attribute(""" The code for the button """)

class IPlayerStateChange(Interface):

    """ The state of the player has changed """

    state = Attribute(""" The new player state """)

class IPlayerTrackChange(IPlayerEvent):

    """ A new track has been loaded on the player """

    track = Attribute(""" The track """)

# Library events

class ILibraryChangeEvent(Interface):

    """ A track has been added, removed or changed in the library """

    added = Attribute(""" A list of tracks that have been added """)
    removed = Attribute(""" A list of tracks that have been removed """)
    changed = Attribute(""" A list of tracks that have changed """)

class IPlaylistEvent(Interface):

    """ Any event that represents a change to the playlist """

class IPlaylistChangeEvent(IPlaylistEvent):
    """ The playlist has changed.  This provides a list of all the playtracks that have changed or been removed """

    added = Attribute(""" A list of playtracks that have been added """)
    removed = Attribute(""" A list of PlayTracks that have been removed """)
    changed = Attribute(""" A list of PlayTracks that have changed """)

class IPlaylistReloadEvent(IPlaylistEvent):
    """ The entire playlist has been reloaded """

    tracks = Attribute(""" The new playlist """)

class IPlaylistReorderEvent(IPlaylistEvent):
    """ Tracks has been moved in the playlist """

    track = Attribute(""" The updated list of changed playtracks """)

class IMetadataChangeEvent(Interface):
    """ New metadata has been loaded by the spotify manager """

class IManholeService(Interface):
    """ Provided by the manhole service """

class ITrackSource(Interface):

    """ A source of tracks. This is able to provide an ITrack when called with
    a track identifier from within it's namespace """

    namespace = Attribute(""" The prefix of track identifiers that this source will handle """)

    def get_track(tid):
        """ Return an object conforming to ITrack that corresponds to the
        referenced track identifier """

class ISquealPlugin(IPlugin):
    """ A plugin for squeal """

class IPluginManager(Interface):
    """ Service that manages plugins """

class ICollection(Interface):
    """ A collection in the library """

    def update(pathname, ftype, details):
        # TBC
        pass

    def scan():
        """ Re-examine every file and update metadata stored accordingly. """

class ITrack(Interface):

    track_id = Attribute(""" An identifier that is unique for the track within the provider namespace """)
    provider = Attribute(""" The service that provides this track.  Required to successfully serialize the track. """)
    track_type = Attribute(""" The type of the track, one of, 0: ogg, 1: mp3,
    2: flac, 3: pcm""")
    is_loaded = Attribute(""" A boolean indicating whether the source of this
    track has loaded all information on the track yet """)
    title = Attribute(""" The name of the track, as a unicode string """)
    artist = Attribute(""" The name of the artist, as a unicode string """)
    album = Attribute(""" The name of the album, as a unicode string """)
    image_uri = Attribute(""" The URI from which the image can be requested """)

    def player_uri():
        """ The URI from which the track data can be requested by the squeezebox. """

class IUserConfigurable(Interface):

    """ Indicates a service that is configurable by the user """

    setup_interface = Attribute(""" The Interface that specifies the form to display """)

# Extension Points

class IMusicSource(Interface):

    name = Attribute("""The internal name of the source""")
    label = Attribute("""The text displayed in the source dropdown""")
    def options_widget():
        """ Returns the options widget """

class IRootResourceExtension(Interface):

    """ I provide a resource that hangs off the root resource provided by the web service. """

    def add_resources(resource):
        """ Adds children to this resource as required """

class IPluginInstallEvent(Interface):

    """ A new plugin has been installed into the system. """
