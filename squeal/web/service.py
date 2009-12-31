
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
from squeal.streaming.service import SpotifyTransfer

import jukebox

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

class Root(rend.Page):

    def __init__(self, original):
        super(Root, self).__init__()
        self.original = original

    def renderHTTP(self, ctx):
        request = inevow.IRequest(ctx)
        request.redirect(request.URLPath().child('jukebox'))
        return ''
    
    def child_jukebox(self, ctx):
        return jukebox.Jukebox(self.original)

    def child_static(self, ctx):
        return File(sibpath(__file__, 'static'))

    def child_play(self, ctx):
        tid = int(ctx.arg('id'))
        pathname = self.original.store.getItemByID(tid).pathname
        return File(pathname)

    def child_spotify(self, ctx):
        print ctx.arg
        playlist = int(ctx.arg('playlist'))
        track = int(ctx.arg('track'))
        print "Request received for spotify %s/%s" % (playlist, track)
        return SpotifyStreamer(self.original, playlist, track)
