
from zope.interface import Interface, Attribute

#### Core services

class ISlimPlayerService(Interface):
    """ The player management service.  This manages the connection of players to the server. """

class ILibrary(Interface):
    """ The music library management service. """

class IPlaylist(Interface):
    """ The playlist management service """

class IWebService(Interface):
    """ The web service, that manages the creation of the web site. """

class IDiscoveryService(Interface):
    """ Manages the UDP Discovery protocol for attaching new players. """

class IEventReactor(Interface):
    """ Handles subscribers to events, so the different services can communicate easily. """

#### End of core services

class INamingPolicy(Interface):

    def details(collection, pathname):
        """ returns a dictionary of track details """

class IJSON(Interface):

    def json():
        """ Return a jsonified representation of the adapted item """

class IPlayerEvent(Interface):

    """ Any event that represents a change of state on a player """

    player = Attribute(""" The local player instance representation """)

class IVolumeChangeEvent(Interface):

    """ The volume has changed """

    volume = Attribute(""" The new volume """)

class ILibraryChangeEvent(Interface):

    """ A track has been added, removed or changed in the library """

    added = Attribute(""" A list of tracks that have been added """)
    removed = Attribute(""" A list of tracks that have been removed """)
    changed = Attribute(""" A list of tracks that have changed """)

class IPlayerStateChange(Interface):

    """ The state of the player has changed """

    state = Attribute(""" The new player state """)

class IPlayerTrackChange(Interface):

    """ A new track has been loaded on the player """

    track = Attribute(""" The track """)

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

class IManholeService(Interface):
    """ Provided by the manhole service """
