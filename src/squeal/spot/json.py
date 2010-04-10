from zope.interface import implements
from twisted.python.components import Adapter, registerAdapter
from squeal.adaptivejson import IJsonAdapter, simplify
from spotify import Link
import spotify
from track import SpotifyTrack

class PlaylistJSON(Adapter):
    implements(IJsonAdapter)

    def encode(self):
        t = self.original
        return {
            u'id': unicode(Link.from_playlist(t)),
            u'status': u"",
            u'name': unicode(t.name(), 'utf-8'),
            u"tracks": [simplify(x) for x in t]
        }

class SpotifyTrackJSON(Adapter):
    implements(IJsonAdapter)
    def encode(self):
        return {
            u'id': unicode(Link.from_track(self.original, 0)),
            u'name': unicode(self.original.name(), 'utf-8'),
            u'isLoaded': self.original.is_loaded(),
        }


registerAdapter(PlaylistJSON, spotify.Playlist, IJsonAdapter)
registerAdapter(SpotifyTrackJSON, spotify.Track, IJsonAdapter)
