
import urllib

from zope.interface import implements

from squeal import isqueal
from spotify import Link


class SpotifyTrack(object):

    """ A wrapper for spotify.Track that conforms to ITrack. Generally you'd
    get this from the spotify service's get_track method. """

    implements(isqueal.ITrack)

    # all spotify tracks are played as raw PCM
    type = 3

    def __init__(self, provider, track):
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
        return self.track.name().decode("utf-8")

    @property
    def artist(self):
        artists = self.track.artists()
        return ",".join(x.name().decode("utf-8") for x in artists)

    @property
    def album(self):
        return self.track.album().name().decode("utf-8")

    def image_uri(self):
        return "/spotify/image?%s" % (urllib.urlencode({"image": self.track.album().cover()}))

    def player_uri(self):
        return "/spotify/stream?tid=%s" % self.track_id
