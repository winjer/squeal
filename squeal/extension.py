from zope.interface import Interface, implements
from twisted.application import service
from axiom.item import Item
from axiom.attributes import text, integer, inmemory, reference
from axiom.sequence import List
from twisted.plugin import getPlugins
from twisted.python import log

from squeal import isqueal
from squeal import plugins

class PluginInstallEvent(object):
    implements(isqueal.IPluginInstallEvent)

    def __init__(self, plugin, version, path):
        self.plugin = plugin
        self.version = version
        self.path = path


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
    installable = inmemory()
    uninstallable = inmemory()


    @property
    def evreactor(self):
        for s in self.store.powerupsFor(isqueal.IEventReactor):
            return s

    def activate(self):
        self.installable = []
        self.uninstallable = []
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
                    log.warning("Plugin %s has been upgraded" % path)
                elif plugin.version < installed[path]:
                    log.warning("Plugin %s has been downgraded" % path)
            else:
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
        self.evreactor.fireEvent(PluginInstallEvent(plugin, version, path))
        return s

