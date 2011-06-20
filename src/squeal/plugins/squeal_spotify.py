
from zope.interface import classProvides
from twisted.application.service import IService

try:
    from squeal.spot.service import Spotify
    from squeal.isqueal import ISquealPlugin
except ImportError:
    Spotify = None

if Spotify:
    class SpotifyPlugin(object):
        classProvides(ISquealPlugin)

        version = '0.0.0'
        name = "Spotify"
        description = "Streaming music from spotify - only available if you have a premium spotify account"
        setup_form = Spotify.setup_form

        @staticmethod
        def install(store, username, password):
            s = Spotify(store=store, username=username, password=password)
            for iface in s.powerupInterfaces:
                store.powerUp(s, iface)
            store.powerUp(s, IService)
            return s

