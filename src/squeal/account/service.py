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
from twisted.cred.checkers import ICredentialsChecker
from twisted.cred.credentials import UsernamePassword

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

    def activate(self):
        self.sessions = []

    def connected(self, page):
        """ Record that a user has connected, and store a reference to the
        page that they are viewing """
        def disconnected(reason):
            self.disconnected(page, reason)
        log.msg("Connection registered for %r" % page, system="squeal.account.service.AccountService")
        self.sessions.append(page)
        page.notifyOnDisconnect().addErrback(disconnected)

    def disconnected(self, page, reason):
        """ Record that a user has disconnected, with the page that they are
        no longer viewing """
        log.msg("Disconnection registered for %r" % page, system="squeal.account.service.AccountService")
        self.sessions.remove(page)

    @property
    def checker(self):
        for s in self.store.powerupsFor(ICredentialsChecker):
            return s

    def login(self, username, password):
        log.msg("Attempt to login as %s" % username, system="squeal.web.jukebox.Account")
        # we only ever use the domain "default" for real users
        username = "%s@default" % username.split("@", 1)[0]
        credentials = UsernamePassword(username, password)
        avatarID = self.checker.requestAvatarId(credentials)
        # Interface is a bit of a cheat here!
        iface, avatar, logout = self.checker.requestAvatar(avatarID, None, isqueal.ISquealAccount)
        return avatar

    def users(self):
        u = set()
        for p in self.sessions:
            if p.avatar is None:
                u.add("Anonymous")
            else:
                u.add(p.avatar.username)
        return u
