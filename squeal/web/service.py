# $Id$
#
# Copyright 2010 Doug Winter
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

""" Orchestration of the web service. """

__author__ = "Doug Winter <doug.winter@isotoma.com>"
__docformat__ = "restructuredtext en"
__version__ = "$Revision$"[11:-2]

import os

from zope.interface import implements

from twisted.internet import reactor
from twisted.python.util import sibpath
from twisted.application import service
from twisted.application import strports
from twisted.python import log

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
from squeal.spot.sfy import SpotifyStreamer

import jukebox

class WebService(Item, service.Service):

    implements(IWebService)
    powerupInterfaces = (IWebService,)

    listen = text()
    parent = inmemory()
    site = inmemory()
    running = inmemory()
    pages = inmemory()

    def __init__(self, config, store):
        listen = unicode(config.get("WebService", "listen"))
        Item.__init__(self, store=store, listen=listen)

    def activate(self):
        self.site = appserver.NevowSite(Root(self), logPath="/dev/null")

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
        log.msg("Request for spotify track %s received" % ctx.arg('tid'), system="squeal.web.service.Root")
        tid = ctx.arg('tid')
        return SpotifyStreamer(self.original, tid)
