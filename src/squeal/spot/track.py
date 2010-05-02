
import urllib

from twisted.python.components import Adapter, registerAdapter
from zope.interface import implements

from squeal import isqueal
from spotify import Link, Track


class SpotifyTrack(object):

    """ A wrapper for spotify.Track that conforms to ITrack. Generally you'd
    get this from the spotify service's get_track method. """

    implements(isqueal.ITrack)

    # all spotify tracks are played as raw PCM
    type = 3

    def __init__(self, track, provider=None):
        self.provider = provider
        self.track = track

    @property
    def track_id(self):
        """ Return the id of the track within the provider namespace. """
        return unicode(Link.from_track(self.track, 0))

    @property
    def is_loaded(self):
        return self.track.is_loaded()

    @property
    def title(self):
        if self.is_loaded:
            return self.track.name().decode("utf-8")
        else:
            return u"Loading..."

    @property
    def artist(self):
        if self.is_loaded:
            artists = self.track.artists()
            return ",".join(x.name().decode("utf-8") for x in artists)
        else:
            return u"Loading..."

    @property
    def album(self):
        if self.is_loaded:
            return self.track.album().name().decode("utf-8")
        else:
            return u"Loading..."

    @property
    def duration(self):
        if self.is_loaded:
            return self.track.duration()
        else:
            return 0

    @property
    def image_uri(self):
        if self.is_loaded:
            return u"/spotify/image?%s" % (urllib.urlencode({"image": self.track.album().cover()}))
        else:
            return u''

    def player_uri(self):
        return u"/spotify/stream?tid=%s" % self.track_id

registerAdapter(SpotifyTrack, Track, isqueal.ITrack)