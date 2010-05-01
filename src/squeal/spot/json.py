from zope.interface import implements
from twisted.python.components import Adapter, registerAdapter
from squeal.adaptivejson import IJsonAdapter, simplify
from squeal import isqueal
from spotify import Link
import spotify
from track import SpotifyTrack

class PlaylistJSON(Adapter):
    implements(IJsonAdapter)

    def encode(self):
        t = self.original
        if t.is_loaded():
            return {
                u'id': unicode(Link.from_playlist(t)),
                u'status': u"",
                u'name': unicode(t.name(), 'utf-8'),
                u"tracks": [simplify(x) for x in t]
            }
        else:
            return {
                u'id': u'unknown',
                u'status': u"",
                u'name': u'Loading...',
                u'tracks': []
            }

class SpotifyTrackJSON(Adapter):
    implements(IJsonAdapter)
    def encode(self):
        st = isqueal.ITrack(self.original)
        return IJsonAdapter(st).encode()


registerAdapter(PlaylistJSON, spotify.Playlist, IJsonAdapter)
registerAdapter(SpotifyTrackJSON, spotify.Track, IJsonAdapter)
