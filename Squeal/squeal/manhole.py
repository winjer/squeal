
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
