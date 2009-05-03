#!/usr/bin/env python
import wingdbstub
from axiom.store import Store

from twisted.application.service import IService

from squeal.library.service import Library
from squeal.web.service import WebService
from squeal.net.slimproto import SlimService
from squeal.net.discovery import DiscoveryService
from squeal.playlist.service import Playlist
from squeal.event import EventReactor

from squeal.isqueal import *

from ConfigParser import ConfigParser

store = Store("db")

conf = ConfigParser()
conf.read("squeal.ini")

services = (
    (EventReactor, IEventReactor),
    (Library, ILibrary),
    (WebService, IWebService),
    (SlimService, ISlimPlayerService),
    (DiscoveryService, IDiscoveryService),
    (Playlist, IPlaylist),
)

for srv, iface in services:
    s = srv(conf, store=store)
    store.powerUp(s, iface)
    store.powerUp(s, IService)
