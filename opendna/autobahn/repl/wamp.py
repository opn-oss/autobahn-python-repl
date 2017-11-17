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
from autobahn.wamp import ComponentConfig

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

    def handleTicketChallenge(self, challenge):
        return self._session.session_kwargs['ticket']

    def handleWAMPCRAChallenge(self, challenge):
        raise NotImplementedError

    def handleCryptosignChallenge(self, challenge):
        raise NotImplementedError

    def onChallenge(self, challenge):
        try:
            if challenge.method == 'ticket':
                return self.handleTicketChallenge(challenge)
            elif challenge.method == 'wampcra':
                return self.handleWAMPCRAChallenge(challenge)
            elif challenge.method == 'cryptosign':
                return self.handleCryptosignChallenge(challenge)
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
