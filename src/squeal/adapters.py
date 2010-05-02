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
            u'duration': self.original.duration,
            u'length': self.length(),
            u'isLoaded': self.original.is_loaded,
        }

    def length(self):
        """ Return a human representation of a length in seconds """
        minutes = self.original.duration / 60000
        seconds = (self.original.duration - (minutes * 60000))/1000
        return u"%d:%02d" % (minutes, seconds)

registerAdapter(TrackJSON, isqueal.ITrack, IJsonAdapter)
