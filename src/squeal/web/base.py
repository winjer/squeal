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

""" Base classes for web interface """

__author__ = "Doug Winter <doug.winter@isotoma.com>"
__docformat__ = "restructuredtext en"
__version__ = "$Revision$"[11:-2]

import os

from twisted.python.util import sibpath
from squeal.adaptivejson import simplify
from twisted.python import log

from nevow import loaders
from nevow import tags as T
from nevow import athena

def liveElement(*s):
    """ Save some typing. """
    return loaders.stan(T.div(render=T.directive('liveElement'))[s])

template_dir = sibpath(__file__, 'templates')

def xmltemplate(name, template_dir=template_dir):
    return loaders.xmlfile(os.path.join(template_dir, name))

class BaseElement(athena.LiveElement):

    def __init__(self, *a, **kw):
        log.msg("Initializing", system=self.__class__.__name__)
        super(BaseElement, self).__init__(*a, **kw)
        self.subscriptions = []

    @athena.expose
    def goingLive(self):
        log.msg("goingLive", system=self.__class__.__name__)
        self.subscribe()

    def subscribe(self):
        """ Override this to subscribe your handlers via self.evreactor """

    def detached(self):
        for s in self.subscriptions:
            s.unsubscribe()

    @property
    def store(self):
        return self.page.service.store

    @property
    def service(self):
        return self.page.original

    @property
    def evreactor(self):
        return self.page.service.evreactor

    def callRemote(self, method, *args):
        def _simplify(o):
            try:
                return simplify(o)
            except ValueError:
                return o
        na = map(_simplify, args)
        return athena.LiveElement.callRemote(self, method, *na)

class BaseElementContainer(BaseElement):

    """ Provides a simple method of providing default fragment instantiation """

    contained = {}

    def _contained_render(self, name):
        if not hasattr(self, 'runtime'):
            self.runtime = {}
        def _(request, tag):
            elem = self.contained[name]()
            self.runtime[name] = elem
            elem.setFragmentParent(self.page)
            return tag[elem]
        return _

    def renderer(self, name):
        if name in self.contained:
            return self._contained_render(name)
        return super(BaseElementContainer, self).renderer(name)

class BasePageContainer(athena.LivePage):

    """ Provides a simple method of providing default fragment instantiation """

    contained = {}

    def _contained_render(self, name):
        if not hasattr(self, 'runtime'):
            self.runtime = {}
        def _(ctx, data):
            elem = self.contained[name]()
            self.runtime[name] = elem
            elem.setFragmentParent(self)
            return ctx.tag[elem]
        return _

    def renderer(self, ctx, name):
        if name in self.contained:
            return self._contained_render(name)
        return super(BasePageContainer, self).renderer(ctx, name)
