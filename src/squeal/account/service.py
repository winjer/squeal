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
from twisted.cred.portal import IRealm
from twisted.cred.credentials import UsernameHashedPassword


from axiom.item import Item
from axiom.attributes import reference, inmemory, text, integer, timestamp

from squeal import isqueal
from squeal.event import EventReactor

from user import UserDetails

import hashlib

class LoginEvent(object):
    pass

class AccountService(Item, service.Service):

    implements(isqueal.IAccountService)
    powerupInterfaces = (isqueal.IAccountService,
                         service.IService)

    dummy = text(default=u"")
    sessions = inmemory()
    parent = inmemory()
    running = inmemory()

    def hash_password(self, password):
        h = hashlib.sha1()
        h.update(password)
        return unicode(h.hexdigest())

    def activate(self):
        self.sessions = []

    def add_account(self, name, username, password):
        """ Create the account, with a hashed password """
        hashed = self.hash_password(password)
        acct = self.realm.addAccount(username, "default", hashed)
        avatar = acct.avatars.open()
        u = UserDetails(store=avatar, username=username, name=name)
        avatar.powerUp(u)

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
    def evreactor(self):
        return self.store.findFirst(EventReactor)

    @property
    def checker(self):
        for s in self.store.powerupsFor(ICredentialsChecker):
            return s

    @property
    def realm(self):
        for r in self.store.powerupsFor(IRealm):
            return r

    def hashed_login(self, username, hashed):
        """ Log in to squeal, returns the avatar and triggers appropriate events. """
        log.msg("Attempt to login as %s" % username, system="squeal.web.jukebox.Account")
        # we only ever use the domain "default" for real users
        username = "%s@default" % username.split("@", 1)[0]
        credentials = UsernameHashedPassword(username, hashed)
        avatarID = self.checker.requestAvatarId(credentials)
        iface, avatar, logout = self.checker.requestAvatar(avatarID, None, isqueal.ISquealAccount)
        self.evreactor.fireEvent(LoginEvent(), isqueal.ILogin)
        return avatar

    def login(self, username, password):
        """ Log in to squeal, returns the avatar and triggers appropriate events. """
        hashed = self.hash_password(password)
        return self.hashed_login(username, hashed)

    def users(self):
        """ Return a sorted list of the users connected. No matter how many
        connections a user has, they will be shown only once """
        u = set()
        for p in self.sessions:
            if p.avatar is None:
                u.add(u"Anonymous")
            else:
                u.add(p.avatar.username)
        return sorted(u)
