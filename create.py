#!/usr/bin/env python

try:
    import wingdbstub
except ImportError:
    pass

from axiom.store import Store

from twisted.application.service import IService

#from squeal.library.service import Library
from squeal.web.service import WebService
from squeal.net.slimproto import SlimService
from squeal.net.discovery import DiscoveryService
from squeal.playlist.service import Playlist
from squeal.event import EventReactor
#from squeal.manhole import ManholeService
from squeal.extension import PluginManager

from squeal.isqueal import *

store = Store("db")

services = (
    EventReactor,
    #Library,
    WebService,
    SlimService,
    DiscoveryService,
    Playlist,
    #ManholeService,
    PluginManager,
)

for srv in services:
    s = srv(store=store)
    for iface in s.powerupInterfaces:
        store.powerUp(s, iface)
    store.powerUp(s, IService)
