from zope.interface import Interface, implements
from twisted.application import service
from axiom.item import Item
from axiom.attributes import text, integer, inmemory, reference
from axiom.sequence import List
from twisted.plugin import getPlugins
from twisted.python import log

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
    installable = inmemory()
    uninstallable = inmemory()


    def __init__(self, conf, store):
        self.config = conf
        Item.__init__(self, store=store)

    def activate(self):
        self.installable = []
        self.uninstallable = []
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
                self.uninstallable.append({
                    'plugin': plugin,
                    'version': a.version,
                    'path': path
                })
                if plugin.version > installed[path]:
                    print "Plugin", path, "has been upgraded"
                elif plugin.version < installed[path]:
                    print "Plugin", path, "has been downgraded"
                else:
                    print "Plugin still present"
            else:
                print "Plugin", path, "is new"
                self.installable.append({
                    'plugin': plugin,
                    'version': a.version,
                    'path': path
                })

        for path, version in installed.items():
            if path not in available:
                print "Plugin", path, "has been removed"

    def install(self, plugin, version, path, args):
        """ Install the specified plugin and record the details of it's
        installation. Returns the service object in the store that manages
        this plugin. This service should be configured and then started if you
        want the plugin to actually do anything. """
        log.msg("Installing plugin %s" % (plugin.name), system="squeal.extension.PluginManager")
        s = plugin.install(self.store, **args)
        InstalledPlugin(store=self.store,
                        version=unicode(version),
                        path=unicode(path))
        return s

