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

from formlet import form
from formlet import field

setup_form = form.Form("manhole-setup", action="install")
field.StringField(form=setup_form, name="listen", label="Listen", value="tcp:2222")
field.StringField(form=setup_form, name="username", label="Username")
field.StringField(form=setup_form, type_="password", name="password", label="Password")
field.SubmitButton(form=setup_form, name="submit", label="Configure manhole")

class ManholeService(Item, service.Service):
    implements(IManholeService)
    powerupInterfaces = (IManholeService,)

    running = inmemory()
    name = inmemory()
    parent = inmemory()
    services = inmemory()
    namedServices = inmemory()
    listen = text(default="tcp:2222")
    username = text()
    password = text()
    setup_form = setup_form

    def startService(self):
        def chainedProtocolFactory():
            def getManhole():
                return Manhole({'store': self.store})
            protocol = insults.ServerProtocol(ColoredManhole)
            protocol.protocolFactory = getManhole
            return protocol

        checker = checkers.InMemoryUsernamePasswordDatabaseDontUse(**{str(self.username): self.password})
        realm = TerminalRealm()
        realm.chainedProtocolFactory = chainedProtocolFactory
        p = portal.Portal(realm, [checker])
        strports.service(self.listen, ConchFactory(p)).setServiceParent(self.parent)
