
from zope.interface import Interface, implements

from nevow import rend
from nevow import inevow
from nevow import loaders
from nevow import tags as T
from nevow import page
from nevow import athena

import base

import ijukebox
from squeal.streaming import ispotify
from squeal import isqueal

from spotify import Link

class BaseContainer(object):
    
    """ Provides a simple method of providing default fragment instantiation """
    
    contained = {}
    
    def _contained_render(self, name):
        def _(ctx, data):
            elem = self.contained[name]()
            elem.setFragmentParent(self)
            return ctx.tag[elem]
        return _
    
    def renderer(self, ctx, name):
        if name in self.contained:
            return self._contained_render(name)
        return super(BaseContainer, self).renderer(ctx, name)
    
class Source(base.BaseElement):
    jsClass = u"Squeal.Source"
    docFactory = base.xmltemplate("source.html")
    
class Account(base.BaseElement):
    jsClass = u"Squeal.Account"
    docFactory = base.xmltemplate("account.html")

class SearchEvent(object):
    def __init__(self, query):
        self.query = query
    
class Search(base.BaseElement):
    jsClass = u"Squeal.Search"
    docFactory = base.xmltemplate("search.html")
    
    @athena.expose
    def search(self, query):
        e = self.evreactor
        spotify = self.store.powerupsFor(isqueal.ISpotify).next()
        e.fireEvent(SearchEvent(query), ijukebox.ISearchStartedEvent)
        spotify.search(query)
    
class Options(base.BaseElement):
    jsClass = u"Squeal.Options"
    docFactory = base.xmltemplate("options.html")
    
class Main(base.BaseElement):
    jsClass = u"Squeal.Main"
    docFactory = base.xmltemplate("main.html")
    
    def subscribe(self):
        e = self.evreactor
        e.subscribe(self.handle_search_start, ijukebox.ISearchStartedEvent)
        e.subscribe(self.handle_search_results, ispotify.ISpotifySearchResultsEvent)
        
    def handle_search_start(self, ev):
        self.callRemote("startThrobber")
        
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
            }
        self.callRemote("searchResults", artists, albums, tracks)

class Playing(base.BaseElement):
    jsClass = u"Squeal.Playing"
    docFactory = base.xmltemplate("playing.html")
    
class Queue(base.BaseElement):
    jsClass = u"Squeal.Queue"
    docFactory = base.xmltemplate("queue.html")
    
class Connected(base.BaseElement):
    jsClass = u"Squeal.Connected"
    docFactory = base.xmltemplate("connected.html")

class Jukebox(BaseContainer, athena.LivePage):
 
    docFactory = base.xmltemplate("jukebox.html")
    
    contained = {
        'source': Source,
        'account': Account,
        'search': Search,
        'options': Options,
        'main': Main,
        'playing': Playing,
        'queue': Queue,
        'connected': Connected,
    }
    
    def __init__(self, service):
        super(Jukebox, self).__init__()
        self.service = service
