# $Id$
#
# Copyright 2010 Doug Winter
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

""" Provision of manhole debugging. """

__author__ = 'Doug Winter <doug.winter@isotoma.com>'
__docformat__ = 'restructuredtext en'
__version__ = '$Revision$'[11:-2]

from zope.interface import implements

from twisted.conch.manhole_ssh import ConchFactory, TerminalRealm
from twisted.conch.insults import insults
from twisted.conch.manhole import ColoredManhole, Manhole

from twisted.internet import protocol
from twisted.application import internet, service
from twisted.application import strports
from twisted.cred import checkers, portal

from axiom.item import Item
from axiom.attributes import inmemory, text

from squeal.isqueal import *

class ManholeService(Item, service.Service):
    implements(IManholeService)
    powerupInterfaces = (IManholeService,)

    running = inmemory()
    name = inmemory()
    parent = inmemory()
    services = inmemory()
    namedServices = inmemory()
    listen = text()
    username = text()
    password = text()

    def __init__(self, config, store):
        Item.__init__(self, store=store)
        self.listen = unicode(config.get("ManholeService", "listen"))
        self.username = unicode(config.get("ManholeService", "username"))
        self.password = unicode(config.get("ManholeService", "password"))

    def startService(self):
        def getManhole():
            return Manhole({'store': self.store})

        def chainedProtocolFactory():
            protocol = insults.ServerProtocol(ColoredManhole)
            protocol.protocolFactory = getManhole
            return protocol

        checker = checkers.InMemoryUsernamePasswordDatabaseDontUse(**{str(self.username): self.password})
        realm = TerminalRealm()
        realm.chainedProtocolFactory = chainedProtocolFactory
        p = portal.Portal(realm, [checker])
        strports.service(self.listen, ConchFactory(p)).setServiceParent(self.parent)



#def makeService(args):
    #checker = checkers.InMemoryUsernamePasswordDatabaseDontUse(username="password")

    #f = protocol.ServerFactory()
    #f.protocol = lambda: TelnetTransport(TelnetBootstrapProtocol,
                                         #insults.ServerProtocol,
                                         #args['protocolFactory'],
                                         #*args.get('protocolArgs', ()),
                                         #**args.get('protocolKwArgs', {}))
    #tsvc = internet.TCPServer(args['telnet'], f)

    #def chainProtocolFactory():
        #return insults.ServerProtocol(
            #args['protocolFactory'],
            #*args.get('protocolArgs', ()),
            #**args.get('protocolKwArgs', {}))

    #rlm = TerminalRealm()
    #rlm.chainedProtocolFactory = chainProtocolFactory
    #ptl = portal.Portal(rlm, [checker])
    #f = ConchFactory(ptl)
    #csvc = internet.TCPServer(args['ssh'], f)

    #m = service.MultiService()
    #tsvc.setServiceParent(m)
    #csvc.setServiceParent(m)
    #return m

#application = service.Application("Interactive Python Interpreter")

#makeService({'protocolFactory': ColoredManhole,
             #'protocolArgs': (None,),
             #'telnet': 6023,
             #'ssh': 6022}).setServiceParent(application)
