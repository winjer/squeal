from twisted.python.components import Adapter, registerAdapter
import isqueal
from adaptivejson import IJsonAdapter
from zope.interface import implements

class TrackJSON(Adapter):
    implements(IJsonAdapter)
    def encode(self):
        return {
            u'id': self.original.track_id,
            u'title': self.original.title,
            u'artist': self.original.artist,
            u'album': self.original.album,
            u'image_uri': self.original.image_uri,
            u'user': u'', #TODO
            u'length': u'', #TODO
            u'isLoaded': self.original.is_loaded,
        }

registerAdapter(TrackJSON, isqueal.ITrack, IJsonAdapter)
