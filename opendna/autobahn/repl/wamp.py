################################################################################
# MIT License
#
# Copyright (c) 2017 OpenDNA Ltd.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
################################################################################
import asyncio

from autobahn.asyncio.wamp import ApplicationSession
from autobahn.wamp import ComponentConfig, auth

from opendna.autobahn.repl.abc import AbstractSession

__author__ = 'Adam Jorgensen <adam.jorgensen.za@gmail.com>'


class REPLApplicationSession(ApplicationSession):

    def __init__(self, session: AbstractSession, future: asyncio.Future,
                 config: ComponentConfig=None):
        self._session = session
        self._future = future
        super().__init__(config)

    def onJoin(self, details):
        super().onJoin(details)
        self._future.set_result(self)

    def handle_ticket_challenge(self, challenge):
        """
        Default handler for WAMP-Ticket authentication

        Returns the `ticket` keyword-argument value supplied to the constructor
        of the opendna.autobahn.repl.abc.AbstractSession instance that is the
        parent of this opendna.autobahn.repl.wamp.REPLApplicationSession instance

        :param challenge:
        :return:
        """
        return self._session.session_kwargs['ticket']

    def handle_wampcra_challenge(self, challenge):
        """
        Default handler for WAMP-CRA authentication

        Uses the `secret` keyword-argument value supplied to the constructor
        of the opendna.autobahn.repl.abc.AbstractSession instance that is the
        parent of this opendna.autobahn.repl.wamp.REPLApplicationSession instance
        in order to generate an authentication signature

        :param challenge:
        :return:
        """
        secret = self._session.session_kwargs['secret']
        if 'salt' in challenge.extra:
            secret = auth.derive_key(
                self._session.session_kwargs['secret'],
                challenge.extra['salt'],
                challenge.extra['iterations'],
                challenge.extra['keylen']
            )
        signature = auth.compute_wcs(secret, challenge.extra['challenge'])
        return signature

    def handle_cryptosign_challenge(self, challenge):
        """
        Default handler for WAML-Cryptosign authentication

        Uses the `key` keyword-argument value supplied to the constructor of the
        opendna.autobahn.repl.abc.AbstractSession instance that is the
        parent of this opendna.autobahn.repl.wamp.REPLApplicationSession instance
        in order to cryptographically sign an authentication challenge.

        `key` needs to be an instance of autobahn.wamp.cryptosign.SigningKey

        :param challenge:
        :return:
        """
        return self._session.session_kwargs['key'].sign_challenge(
            self, challenge
        )

    def onChallenge(self, challenge):
        """
        Default handler for Challenge-based authentication. Farms out handling
        of WAMP-Ticket, WAMP-CRA and WAMP-Cryptosign authentication challenges
        to the relevant companion methods on this class

        :param challenge:
        :return:
        """
        try:
            if challenge.method == 'ticket':
                return self.handle_ticket_challenge(challenge)
            elif challenge.method == 'wampcra':
                return self.handle_wampcra_challenge(challenge)
            elif challenge.method == 'cryptosign':
                return self.handle_cryptosign_challenge(challenge)
            return super().onChallenge(challenge)
        except Exception as e:
            self._future.set_exception(e)
            raise

    def onOpen(self, transport):
        try:
            super().onOpen(transport)
        except Exception as e:
            self._future.set_exception(e)
            raise

    def onConnect(self):
        try:
            self.join(
                realm=self._session.connection.realm,
                authmethods=self._session.authmethods,
                authid=self._session.authid,
                authrole=self._session.authrole,
                authextra=self._session.authextra,
                resumable=self._session.resumable,
                resume_session=self._session.resume_session,
                resume_token=self._session.resume_token
            )
        except Exception as e:
            self._future.set_exception(e)
            raise

    def onDisconnect(self):
        super().onDisconnect()

    def onClose(self, wasClean):
        super().onClose(wasClean)

    def onLeave(self, details):
        return super().onLeave(details)

    def onUserError(self, fail, msg):
        super().onUserError(fail, msg)

    def onMessage(self, msg):
        super().onMessage(msg)
