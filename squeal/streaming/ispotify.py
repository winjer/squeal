from zope.interface import Interface, Attribute

class ISpotifyEvent(Interface):
    """ Any spotify event """

class ISpotifyLoggedInEvent(ISpotifyEvent):
    """ We have logged into spotify successfully. """

class ISpotifyLoggedOutEvent(ISpotifyEvent):
    """ We have been logged out of spotify """

    error = Attribute("""The error that caused us to be logged out. """)

class ISpotifyMetadataUpdatedEvent(ISpotifyEvent):
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

