
import os

from zope.interface import implements

from twisted.internet import reactor
from twisted.python.util import sibpath
from twisted.application import service
from twisted.application import strports

from axiom.item import Item
from axiom.attributes import reference, text, integer, inmemory

from nevow import rend
from nevow import inevow
from nevow.static import File
from nevow import loaders
from nevow import tags as T
from nevow import athena
from nevow import appserver

from squeal.library.record import *
from squeal.isqueal import *
from squeal.event import EventReactor

def liveElement(*s):
    """ Save some typing. """
    return loaders.stan(T.div(render=T.directive('liveElement'))[s])

class WebService(Item, service.Service):

    implements(IWebService)

    listen = text()
    parent = inmemory()
    site = inmemory()
    running = inmemory()
    pages = inmemory()

    def __init__(self, config, store):
        listen = unicode(config.get("WebService", "listen"))
        Item.__init__(self, store=store, listen=listen)

    def activate(self):
        self.site = appserver.NevowSite(Root(self))

    @property
    def evreactor(self):
        return self.store.findFirst(EventReactor)

    def startService(self):
        strports.service(self.listen, self.site).setServiceParent(self.parent)
        return service.Service.startService(self)

templateDir = sibpath(__file__, 'templates')

class BaseElement(athena.LiveElement):

    def __init__(self, *a, **kw):
        super(BaseElement, self).__init__(*a, **kw)
        self.subscriptions = []

    @athena.expose
    def goingLive(self):
        self.subscribe()

    def subscribe(self):
        """ Override this to subscribe your handlers via self.evreactor """

    def detached(self):
        for s in self.subscriptions:
            s.unsubscribe()

    @property
    def store(self):
        return self.service.store

    @property
    def service(self):
        return self.page.original

    @property
    def evreactor(self):
        return self.service.evreactor

class Controls(BaseElement):
    jsClass = u'Squeal.Controls'
    docFactory = liveElement(
        T.div(id='controls')[
            'Controls'
        ]
    )

    @athena.expose
    def play(self):
        for p in self.store.powerupsFor(IPlaylist):
            p.play()

    @athena.expose
    def stop(self):
        for p in self.store.powerupsFor(IPlaylist):
            p.stop()

class Status(BaseElement):
    jsClass = u'Squeal.Status'
    docFactory = liveElement(
        T.div(id='status')[
            'Status'
        ]
    )

    def subscribe(self):
        self.added = 0
        self.evreactor.subscribe(self.volumeChange, IVolumeChangeEvent)
        self.evreactor.subscribe(self.libraryChange, ILibraryChangeEvent)

    def volumeChange(self, ev):
        self.callRemote("volumeChanged", unicode(ev.volume))

    def libraryChange(self, ev):
        self.added += len(ev.added)
        if self.added % 10 == 0:
            self.callRemote("message", u"%d tracks added to library since launch..." % self.added)


class Library(BaseElement):
    jsClass = u'Squeal.Library'
    docFactory = liveElement(
        T.div(id='library')
    )

    @athena.expose
    def reload(self):
        for library in self.store.powerupsFor(ILibrary):
            rows = [IJSON(x).json() for x in library.tracks()]
            return {
                u'results': len(rows),
                u'rows': rows
            }

    @athena.expose
    def queue(self, id):
        track = self.store.getItemByID(id)
        for p in self.store.powerupsFor(IPlaylist):
            p.enqueue(track)

class Playlist(BaseElement):
    jsClass = u'Squeal.Playlist'
    docFactory = liveElement(
        T.div(id='playlist')
    )

    def subscribe(self):
        for e in self.store.powerupsFor(IEventReactor):
            e.subscribe(self.changed, IPlaylistChangeEvent)

    def changed(self, event):
        for added in event.added:
            self.addTrack(added)

    @athena.expose
    def reload(self):
        rows = []
        for p in self.page.original.store.powerupsFor(IPlaylist):
            rows = [IJSON(x).json() for x in p]
        return {
            u'results': len(rows),
            u'rows': rows
        }

    def addTrack(self, track):
        self.callRemote("addTrack", IJSON(track).json())

class Jukebox(athena.LivePage):

    docFactory = loaders.xmlfile(os.path.join(templateDir, 'index.html'))

    def __init__(self, original):
        super(Jukebox, self).__init__()
        self.original = original

    def render_controls(self, ctx, data):
        controls = Controls()
        controls.setFragmentParent(self)
        return ctx.tag[controls]

    def render_status(self, ctx, data):
        status = Status()
        status.setFragmentParent(self)
        return ctx.tag[status]

    def render_library(self, ctx, data):
        library = Library()
        library.setFragmentParent(self)
        return ctx.tag[library]

    def render_playlist(self, ctx, data):
        playlist = Playlist()
        playlist.setFragmentParent(self)
        return ctx.tag[playlist]


class Root(rend.Page):

    def __init__(self, original):
        super(Root, self).__init__()
        self.original = original

    def renderHTTP(self, ctx):
        request = inevow.IRequest(ctx)
        request.redirect(request.URLPath().child('jukebox'))
        return ''

    def child_static(self, ctx):
        return File(sibpath(__file__, 'static'))

    def child_jukebox(self, ctx):
        return Jukebox(self.original)

    def child_play(self, ctx):
        tid = int(ctx.arg('id'))
        pathname = self.original.store.getItemByID(tid).pathname
        return File(pathname)

