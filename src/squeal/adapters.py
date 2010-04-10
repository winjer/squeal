from twisted.python.components import Adapter, registerAdapter
import isqueal
from adaptivejson import IJsonAdapter
from zope.interface import implements

class TrackJSON(Adapter):
    implements(IJsonAdapter)
    def encode(self):
        return {
            u'id': unicode(self.original.track_id),
            u'name': self.original.title,
            u'isLoaded': self.original.is_loaded,
        }

registerAdapter(TrackJSON, isqueal.ITrack, IJsonAdapter)
