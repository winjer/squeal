
from nevow import rend
from nevow import inevow
from nevow import loaders
from nevow import tags as T
from nevow import page
from nevow import athena

import base

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
    
class Search(base.BaseElement):
    jsClass = u"Squeal.Search"
    docFactory = base.xmltemplate("search.html")
    
class Options(base.BaseElement):
    jsClass = u"Squeal.Options"
    docFactory = base.xmltemplate("options.html")
    
class Main(base.BaseElement):
    jsClass = u"Squeal.Main"
    docFactory = base.xmltemplate("main.html")
    
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
 
    jsClass = u"Squeal.Jukebox"
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
