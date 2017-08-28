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

__author__ = 'Adam Jorgensen <adam.jorgensen.za@gmail.com>'


class REPLApplicationSession(ApplicationSession):

    def __init__(self, future: asyncio.Future, config: ComponentConfig=None):
        self.__future = future
        super().__init__(config)

    def onJoin(self, details):
        super().onJoin(details)
        self.__future.set_result(self)

    def onChallenge(self, challenge):
        try:
            return super().onChallenge(challenge)
        except Exception as e:
            self.__future.set_exception(e)
            raise

    def onOpen(self, transport):
        try:
            super().onOpen(transport)
        except Exception as e:
            self.__future.set_exception(e)
            raise

    def onConnect(self):
        try:
            super().onConnect()
        except Exception as e:
            self.__future.set_exception(e)
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
