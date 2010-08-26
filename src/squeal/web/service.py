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

import jukebox

class WebService(Item, service.Service):

    implements(IWebService)
    powerupInterfaces = (IWebService, service.IService)

    listen = text(default=u"tcp:9000")
    parent = inmemory()
    site = inmemory()
    running = inmemory()
    pages = inmemory()
    root = inmemory()

    def activate(self):
        self.root = Root(self)
        self.site = appserver.NevowSite(self.root, logPath="/dev/null")
        self.add_root_resources()
        self.evreactor.subscribe(self.add_root_resources, IPluginInstallEvent)

    def add_root_resources(self, ev=None):
        """ Adds root resources provided by plugins to the root resource. """
        for s in self.store.powerupsFor(IRootResourceExtension):
            s.add_resources(self.root)

    @property
    def evreactor(self):
        return self.store.findFirst(EventReactor)

    def startService(self):
        strports.service(self.listen, self.site).setServiceParent(self.parent)
        return service.Service.startService(self)

class Root(rend.Page):

    def renderHTTP(self, ctx):
        request = inevow.IRequest(ctx)
        request.redirect("/jukebox")
        return ''

    def child_jukebox(self, ctx):
        return jukebox.Jukebox(self.original)

    def child_static(self, ctx):
        return File(sibpath(__file__, 'static'))

    def child_play(self, ctx):
        tid = int(ctx.arg('id'))
        pathname = self.original.store.getItemByID(tid).pathname
        return File(pathname)

