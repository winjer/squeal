from squeal.web import base
from twisted.python.util import sibpath
from nevow import athena

from squeal import isqueal
from squeal.spot import ispotify
from squeal.web import ijukebox


from spotify import Link

template_dir = sibpath(__file__, 'templates')

def xmltemplate(s):
    return base.xmltemplate(s, template_dir)

class SearchEvent(object):
    def __init__(self, query):
        self.query = query

class Search(base.BaseElement):
    jsClass = u"Spot.Search"
    docFactory = xmltemplate("search.html")

    @athena.expose
    def search(self, query):
        e = self.evreactor
        spotify = self.store.powerupsFor(isqueal.ISpotify).next()
        e.fireEvent(SearchEvent(query), ijukebox.ISearchStartedEvent)
        spotify.search(query)

class Options(base.BaseElement):
    jsClass = u"Spot.Options"
    docFactory = xmltemplate("options.html")

class Document(base.BaseElement):
    jsClass = u"Spot.Document"
    docFactory = xmltemplate("document.html")

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

class Main(base.BaseElementContainer):
    docFactory = xmltemplate("main.html")

    contained = {
        'search': Search,
        'options': Options,
        'document': Document,
    }

