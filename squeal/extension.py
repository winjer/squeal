from zope.interface import Interface, implements
from twisted.application import service
from axiom.item import Item
from axiom.attributes import text, integer, inmemory, reference
from axiom.sequence import List
from twisted.plugin import getPlugins

from squeal import isqueal
from squeal import plugins

class InstalledPlugin(Item):

    path = text()
    version = text()

class PluginManager(Item, service.Service):

    implements(isqueal.IPluginManager)
    powerupInterfaces = (isqueal.IPluginManager,)

    dummy = text()
    running = inmemory()
    name = inmemory()
    parent = inmemory()
    config = inmemory()

    def __init__(self, conf, store):
        self.config = conf
        Item.__init__(self, store=store)

    def activate(self):
        from ConfigParser import ConfigParser
        self.config = ConfigParser()
        self.config.read("squeal.ini")
        installed = {}
        available = {}
        for i in self.store.query(InstalledPlugin):
            installed[i.path] = i.version

        for a in getPlugins(isqueal.ISquealPlugin, plugins):
            path = a.__name__ + "." + a.__module__
            available[path] = a

        for path, plugin in available.items():
            if path in installed:
                if plugin.version > installed[path]:
                    print "Plugin", path, "has been upgraded"
                elif plugin.version < installed[path]:
                    print "Plugin", path, "has been downgraded"
                else:
                    print "Plugin still present"
            else:
                print "Plugin", path, "is new"
                plugin.install(self.config, self.store)
                InstalledPlugin(store=self.store,
                                version=unicode(a.version),
                                path=unicode(path))


        for path, version in installed.items():
            if path not in available:
                print "Plugin", path, "has been removed"
