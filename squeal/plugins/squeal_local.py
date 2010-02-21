from zope.interface import classProvides
from twisted.application.service import IService

from squeal.isqueal import ISquealPlugin
from squeal.library.service import Library

from squeal.library.policies import StandardNamingPolicy

class LibraryPlugin(object):
    classProvides(ISquealPlugin)

    version = '0.0.0'
    name = "Local Library"
    description = "Collections of mp3, ogg or flac files on disk"
    setup_form = Library.setup_form

    @staticmethod
    def install(store, pathname):
        p = StandardNamingPolicy(store=store)
        s = Library(store=store, naming_policy=p)
        for iface in s.powerupInterfaces:
            store.powerUp(s, iface)
        store.powerUp(s, IService)
        s.add_collection(pathname)
        s.rescan()
        return s

