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

""" Keep track of logged in users. """

__author__ = "Doug Winter <doug.winter@isotoma.com>"
__docformat__ = "restructuredtext en"

from zope.interface import implements
from twisted.python import log
from twisted.application import service
from axiom.item import Item
from axiom.attributes import reference, inmemory, text, integer, timestamp

from squeal import isqueal

class AccountService(Item, service.Service):

    implements(isqueal.IAccountService)
    powerupInterfaces = (isqueal.IAccountService,
                         service.IService)

    dummy = text(default=u"")
    sessions = inmemory()
    parent = inmemory()
    running = inmemory()

    def connected(self, page):
        """ Record that a user has connected, and store a reference to the
        page that they are viewing """
        def disconnected(reason):
            self.disconnected(page, reason)
        log.msg("Connection registered for %r" % page, system="squeal.account.service.AccountService")
        page.notifyOnDisconnect().addErrback(disconnected)

    def disconnected(self, page, reason):
        """ Record that a user has disconnected, with the page that they are
        no longer viewing """
        log.msg("Disconnection registered for %r" % page, system="squeal.account.service.AccountService")

