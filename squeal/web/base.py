
import os

from twisted.python.util import sibpath

from nevow import loaders
from nevow import tags as T
from nevow import athena

def liveElement(*s):
    """ Save some typing. """
    return loaders.stan(T.div(render=T.directive('liveElement'))[s])

template_dir = sibpath(__file__, 'templates')

def xmltemplate(name):
    return loaders.xmlfile(os.path.join(template_dir, name))

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
        return self.page.service.store

    @property
    def service(self):
        return self.page.original

    @property
    def evreactor(self):
        return self.page.service.evreactor
