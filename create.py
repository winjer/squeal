#!/usr/bin/env python

try:
    import wingdbstub
except ImportError:
    pass

from axiom.store import Store

from twisted.application.service import IService

from squeal.library.service import Library
from squeal.web.service import WebService
from squeal.net.slimproto import SlimService
from squeal.net.discovery import DiscoveryService
from squeal.playlist.service import Playlist
from squeal.event import EventReactor
from squeal.manhole import ManholeService
from squeal.streaming.service import Spotify

from squeal.isqueal import *

from ConfigParser import ConfigParser

store = Store("db")

conf = ConfigParser()
conf.read("squeal.ini")

services = (
    EventReactor,
    Library,
    WebService,
    SlimService,
    DiscoveryService,
    Playlist,
    ManholeService,
    Spotify,
)

for srv in services:
    s = srv(conf, store=store)
    for iface in s.powerupInterfaces:
        store.powerUp(s, iface)
    store.powerUp(s, IService)
