from squeal.web import base

template_dir = sibpath(__file__, 'templates')

def xmltemplate(s):
    return base.xmltemplate(s, template_dir)

class Search(base.BaseElement):
    jsClass = u"Spot.Search"
    docFactory = base.xmltemplate("search.html")

    @athena.expose
    def search(self, query):
        e = self.evreactor
        spotify = self.store.powerupsFor(isqueal.ISpotify).next()
        e.fireEvent(SearchEvent(query), ijukebox.ISearchStartedEvent)
        spotify.search(query)

class Main(base.BaseElement):
    jsClass = u"Spot.Main"
    docFactory = base.xmltemplate("main.html")

    def subscribe(self):
        e = self.evreactor
        e.subscribe(self.handle_search_start, ijukebox.ISearchStartedEvent)
        e.subscribe(self.handle_search_results, ispotify.ISpotifySearchResultsEvent)

    def handle_search_start(self, ev):
        self.callRemote("startThrobber")

    def human_duration(self, d):
        mins = int(d/60000)
        secs = int((d - (mins*60000)) / 1000)
        return u"%dm %ds" % (mins, secs)

    def handle_search_results(self, ev):
        artists = {}
        albums = {}
        tracks = {}
        for a in ev.results.artists():
            k = unicode(Link.from_artist(a))
            artists[k] = {
                u'name': a.name().decode("utf-8"),
                u'link': k,
            }
        for a in ev.results.albums():
            k = unicode(Link.from_album(a))
            albums[k] = {
                u'name': a.name().decode("utf-8"),
                u'link': k,
            }
        for a in ev.results.tracks():
            k = unicode(Link.from_track(a, 0))
            tracks[k] = {
                u'name': a.name().decode("utf-8"),
                u'link': k,
                u'album_name': a.album().name().decode("utf-8"),
                u'artist_name': ", ".join([x.name() for x in a.artists()]).decode("utf-8"),
                u'duration': self.human_duration(a.duration()),
            }
        self.callRemote("searchResults", artists, albums, tracks)
