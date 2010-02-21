
from zope.interface import classProvides
from twisted.application.service import IService

from squeal.isqueal import ISquealPlugin
from squeal.manhole import ManholeService

class ManholePlugin(object):
    classProvides(ISquealPlugin)

    version = '0.0.0'
    name = "Manhole"
    description = "Provides a 'manhole' allowing you to ssh directly into the squeal server and poke around in a python prompt. """
    setup_form = ManholeService.setup_form

    @staticmethod
    def install(store, listen, username, password):
        s = ManholeService(store=store, listen=listen, username=username, password=password)
        for iface in s.powerupInterfaces:
            store.powerUp(s, iface)
        store.powerUp(s, IService)
        return s
