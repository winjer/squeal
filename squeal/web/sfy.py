
class SpotifyStreamer(rend.Page):

    def __init__(self, original, playlist, track):
        self.original = original
        self.playlist = playlist
        self.track = track

    def renderHTTP(self, ctx):
        for service in self.original.store.powerupsFor(ISpotify):
            request = inevow.IRequest(ctx)
            SpotifyTransfer(self.playlist, self.track, service, request)
            return request.deferred
