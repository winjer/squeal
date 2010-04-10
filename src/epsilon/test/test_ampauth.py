# Copyright (c) 2008 Divmod.  See LICENSE for details.

"""
Tests for L{epsilon.ampauth}.
"""

import epsilon.hotfix
epsilon.hotfix.require('twisted', 'loopbackasync_reentrancy')

from sha import sha

from zope.interface import implements
from zope.interface.verify import verifyObject

from twisted.python.failure import Failure
from twisted.internet.error import ConnectionDone
from twisted.cred.error import UnauthorizedLogin
from twisted.cred.checkers import InMemoryUsernamePasswordDatabaseDontUse
from twisted.cred.credentials import UsernamePassword
from twisted.cred.portal import Portal
from twisted.protocols.amp import IBoxReceiver, BinaryBoxProtocol, CommandLocator, AMP
from twisted.protocols.loopback import loopbackAsync
from twisted.trial.unittest import TestCase

from epsilon.ampauth import (
    _AMPOneTimePad, _AMPUsernamePassword, _calcResponse, UnhandledCredentials,
    CredReceiver, PasswordLogin, OTPLogin, PasswordChallengeResponse,
    OneTimePadChecker, CredAMPServerFactory, login)

__metaclass__ = type



class StubRealm:
    def __init__(self, avatar):
        self.avatar = avatar
        self.loggedOut = 0
        self.requests = []


    def requestAvatar(self, avatarId, mind, *interfaces):
        self.requests.append((avatarId, mind, interfaces))
        return interfaces[0], self.avatar, self.logout


    def logout(self):
        self.loggedOut += 1



class StubAvatar:
    """
    An L{IBoxReceiver} implementation which can be used as an avatar by the
    L{CredReceiver} tests.
    """
    implements(IBoxReceiver)

    def startReceivingBoxes(self, sender):
        self.boxSender = sender


    def ampBoxReceived(self, box):
        pass


    def stopReceivingBoxes(self, reason):
        pass

verifyObject(IBoxReceiver, StubAvatar())



class CredReceiverTests(TestCase):
    """
    Tests for L{CredReceiver}, an L{IBoxReceiver} which integrates with
    L{twisted.cred} to provide authentication and authorization of AMP
    connections.
    """
    def setUp(self):
        """
        Create a L{CredReceiver} hooked up to a fake L{IBoxSender} which
        records boxes sent through it.
        """
        self.username = 'alice@example.com'
        self.password = 'foo bar baz'
        self.checker = InMemoryUsernamePasswordDatabaseDontUse()
        self.checker.addUser(self.username, self.password)
        self.avatar = StubAvatar()
        self.realm = StubRealm(self.avatar)
        self.portal = Portal(self.realm, [self.checker])
        self.server = CredReceiver()
        self.server.portal = self.portal
        self.client = AMP()
        self.finished = loopbackAsync(self.server, self.client)


    def test_otpLogin(self):
        """
        L{CredReceiver.otpLogin} returns without error if the pad is valid.
        """
        PAD = 'test_otpLogin'
        self.portal.registerChecker(OneTimePadChecker({PAD: 'user'}))
        d = self.server.otpLogin(PAD)
        def cbLoggedIn(result):
            self.assertEqual(result, {})
        d.addCallback(cbLoggedIn)
        return d


    def test_otpLoginUnauthorized(self):
        """
        L{CredReceiver.otpLogin} should fail with L{UnauthorizedLogin} if an
        invalid pad is received.
        """
        self.portal.registerChecker(OneTimePadChecker({}))
        return self.assertFailure(
            self.server.otpLogin('test_otpLoginUnauthorized'),
            UnauthorizedLogin)


    def test_otpLoginNotImplemented(self):
        """
        L{CredReceiver.otpLogin} should fail with L{NotImplementedError} if
        the realm raises L{NotImplementedError} when asked for the avatar.
        """
        def noAvatar(avatarId, mind, *interfaces):
            raise NotImplementedError()
        self.realm.requestAvatar = noAvatar

        PAD = 'test_otpLoginNotImplemented'
        self.portal.registerChecker(OneTimePadChecker({PAD: 'user'}))
        return self.assertFailure(
            self.server.otpLogin(PAD), NotImplementedError)


    def test_otpLoginResponder(self):
        """
        L{CredReceiver} responds to the L{OTPLogin} command.
        """
        PAD = 'test_otpLoginResponder'
        self.portal.registerChecker(OneTimePadChecker({PAD: 'user'}))
        d = self.client.callRemote(OTPLogin, pad=PAD)
        def cbLoggedIn(result):
            self.assertEqual(result, {})
        d.addCallback(cbLoggedIn)
        return d


    def test_passwordLoginDifferentChallenges(self):
        """
        L{CredReceiver.passwordLogin} returns a new challenge each time it is
        called.
        """
        first = self.server.passwordLogin(self.username)
        second = self.server.passwordLogin(self.username)
        self.assertNotEqual(first['challenge'], second['challenge'])


    def test_passwordLoginResponder(self):
        """
        L{CredReceiver} responds to the L{PasswordLogin} L{Command} with a
        challenge.
        """
        d = self.client.callRemote(PasswordLogin, username=self.username)
        def cbLogin(result):
            self.assertIn('challenge', result)
        d.addCallback(cbLogin)
        return d


    def test_determineFromDifferentNonces(self):
        """
        Each time L{PasswordChallengeResponse.determineFrom} is used, it
        generates a different C{cnonce} value.
        """
        first = PasswordChallengeResponse.determineFrom('a', 'b')
        second = PasswordChallengeResponse.determineFrom('a', 'b')
        self.assertNotEqual(first['cnonce'], second['cnonce'])


    def test_passwordChallengeResponse(self):
        """
        L{CredReceiver.passwordChallengeResponse} returns without error if the
        response is valid.
        """
        challenge = self.server.passwordLogin(self.username)['challenge']
        cnonce = '123abc'
        cleartext = '%s %s %s' % (challenge, cnonce, self.password)
        response = sha(cleartext).digest()
        d = self.server.passwordChallengeResponse(cnonce, response)
        def cbLoggedIn(result):
            self.assertEqual(result, {})
        d.addCallback(cbLoggedIn)
        return d


    def test_passwordChallengeResponseResponder(self):
        """
        L{CredReceiver} responds to the L{PasswordChallengeResponse} L{Command}
        with an empty box if the response supplied is valid.
        """
        challenge = self.server.passwordLogin(self.username)['challenge']
        d = self.client.callRemote(
            PasswordChallengeResponse, **PasswordChallengeResponse.determineFrom(
                challenge, self.password))
        def cbResponded(result):
            self.assertEqual(result, {})
        d.addCallback(cbResponded)
        return d


    def test_response(self):
        """
        L{PasswordChallengeResponse.determineFrom} generates the correct
        response to a challenge issued by L{CredReceiver.passwordLogin}.
        """
        challenge = self.server.passwordLogin(self.username)['challenge']
        result = PasswordChallengeResponse.determineFrom(
            challenge, self.password)
        d = self.server.passwordChallengeResponse(**result)
        def cbLoggedIn(ignored):
            [(avatarId, mind, interfaces)] = self.realm.requests
            self.assertEqual(avatarId, self.username)
            self.assertEqual(interfaces, (IBoxReceiver,))

            # The avatar is now the protocol's box receiver.
            self.assertIdentical(self.server.boxReceiver, self.avatar)

            # And the avatar has been started up with the protocol's
            # IBoxSender.
            self.assertIdentical(self.avatar.boxSender, self.server.boxSender)

            # After the connection is lost, the logout function should be
            # called.
            self.assertEqual(self.realm.loggedOut, 0)
            self.server.connectionLost(
                Failure(ConnectionDone("test connection lost")))
            self.assertEqual(self.realm.loggedOut, 1)

        d.addCallback(cbLoggedIn)
        return d


    def test_invalidResponse(self):
        """
        L{CredReceiver.passwordChallengeResponse} returns a L{Deferred} which
        fails with L{UnauthorizedLogin} if it is passed a response which is not
        valid.
        """
        challenge = self.server.passwordLogin(self.username)['challenge']
        return self.assertFailure(
            self.server.passwordChallengeResponse(cnonce='bar', response='baz'),
            UnauthorizedLogin)


    def test_connectionLostWithoutAvatar(self):
        """
        L{CredReceiver.connectionLost} does not raise an exception if no login
        has occurred when it is called.
        """
        self.server.connectionLost(
            Failure(ConnectionDone("test connection lost")))


    def test_unrecognizedCredentialsLogin(self):
        """
        L{login} raises L{UnhandledCredentials} if passed a credentials object
        which provides no interface explicitly supported by that function,
        currently L{IUsernamePassword}.
        """
        self.assertRaises(UnhandledCredentials, login, None, None)


    def test_passwordChallengeLogin(self):
        """
        L{login} issues the commands necessary to authenticate against
        L{CredReceiver} when given an L{IUsernamePassword} provider with its
        C{username} and C{password} attributes set to valid credentials.
        """
        loginDeferred = login(
            self.client, UsernamePassword(self.username, self.password))

        def cbLoggedIn(clientAgain):
            self.assertIdentical(self.client, clientAgain)
            self.assertIdentical(self.server.boxReceiver, self.avatar)
        loginDeferred.addCallback(cbLoggedIn)
        return loginDeferred


    def test_passwordChallengeInvalid(self):
        """
        L{login} returns a L{Deferred} which fires with L{UnauthorizedLogin} if
        the L{UsernamePassword} credentials object given does not contain valid
        authentication information.
        """
        boxReceiver = self.server.boxReceiver
        loginDeferred = login(
            self.client, UsernamePassword(self.username + 'x', self.password))
        self.assertFailure(loginDeferred, UnauthorizedLogin)
        def cbFailed(ignored):
            self.assertIdentical(self.server.boxReceiver, boxReceiver)
        loginDeferred.addCallback(cbFailed)
        return loginDeferred


    def test_noAvatar(self):
        """
        L{login} returns a L{Deferred} which fires with L{NotImplementedError}
        if the realm raises L{NotImplementedError} when asked for the avatar.
        """
        def noAvatar(avatarId, mind, *interfaces):
            raise NotImplementedError()
        self.realm.requestAvatar = noAvatar

        loginDeferred = login(
            self.client, UsernamePassword(self.username, self.password))
        return self.assertFailure(loginDeferred, NotImplementedError)



class AMPUsernamePasswordTests(TestCase):
    """
    Tests for L{_AMPUsernamePasswordTests}, a credentials type which works with
    username/challenge/nonce/responses of the form used by L{PasswordLogin}.
    """
    def setUp(self):
        self.username = 'user name'
        password = u'foo bar\N{LATIN SMALL LETTER E WITH ACUTE}'
        self.password = password.encode('utf-8')
        self.challenge = '123xyzabc789'
        self.nonce = '1 2 3 4 5'
        self.response = _calcResponse(
            self.challenge, self.nonce, self.password)
        self.credentials = _AMPUsernamePassword(
            self.username, self.challenge, self.nonce, self.response)

    def test_checkPasswordString(self):
        """
        L{_AMPUsernamePassword} accepts a C{str} for the known correct
        password and returns C{True} if the response matches it.
        """
        self.assertTrue(self.credentials.checkPassword(self.password))


    def test_checkInvalidPasswordString(self):
        """
        L{_AMPUsernamePassword} accepts a C{str} for the known correct
        password and returns C{False} if the response does not match it.
        """
        self.assertFalse(self.credentials.checkPassword('quux'))


    def test_checkPasswordUnicode(self):
        """
        L{_AMPUsernamePassword} accepts a C{unicode} for the known correct
        password and returns C{True} if the response matches the UTF-8 encoding
        of it.
        """
        self.assertTrue(
            self.credentials.checkPassword(self.password.decode('utf-8')))


    def test_checkInvalidPasswordUnicode(self):
        """
        L{_AMPUsernamePassword} accepts a C{unicode} for the known correct
        password and returns C{False} if the response does not match the UTF-8
        encoding of it.
        """
        self.assertFalse(
            self.credentials.checkPassword(
                u'\N{LATIN SMALL LETTER E WITH ACUTE}'))



class CredAMPServerFactoryTests(TestCase):
    """
    Tests for L{CredAMPServerFactory}.
    """
    def test_buildProtocol(self):
        """
        L{CredAMPServerFactory.buildProtocol} returns a L{CredReceiver}
        instance with its C{portal} attribute set to the portal object passed
        to L{CredAMPServerFactory.__init__}.
        """
        portal = object()
        factory = CredAMPServerFactory(portal)
        proto = factory.buildProtocol(None)
        self.assertIsInstance(proto, CredReceiver)
        self.assertIdentical(proto.portal, portal)



class OneTimePadCheckerTests(TestCase):
    """
    Tests for L{OneTimePadChecker}.
    """
    def test_requestAvatarId(self):
        """
        L{OneTimePadChecker.requestAvatarId} should return the username in the
        case the pad is valid.
        """
        PAD = 'test_requestAvatarId'
        USERNAME = 'test_requestAvatarId username'
        checker = OneTimePadChecker({PAD: USERNAME})
        self.assertEqual(
            checker.requestAvatarId(_AMPOneTimePad(PAD)), USERNAME)


    def test_requestAvatarIdUnauthorized(self):
        """
        L{OneTimePadChecker.requestAvatarId} should throw L{UnauthorizedLogin}
        if an unknown pad is given.
        """
        checker = OneTimePadChecker({})
        self.assertRaises(
            UnauthorizedLogin,
            lambda: checker.requestAvatarId(_AMPOneTimePad(None)))


    def test_oneTimePad(self):
        """
        L{OneTimePadChecker.requestAvatarId} should invalidate the pad if a
        login is successful.
        """
        PAD = 'test_requestAvatarId'
        checker = OneTimePadChecker({PAD: 'username'})
        checker.requestAvatarId(_AMPOneTimePad(PAD))
        self.assertRaises(
            UnauthorizedLogin,
            lambda: checker.requestAvatarId(_AMPOneTimePad(PAD)))
