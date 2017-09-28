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

from autobahn.asyncio.wamp import ApplicationRunner
from autobahn.wamp import ComponentConfig

from opendna.autobahn.repl.abc import (
    AbstractSession,
    AbstractConnection
)
from opendna.autobahn.repl.pubsub import PublisherManager, SubscribeManager
from opendna.autobahn.repl.rpc import CallManager, RegisterManager
from opendna.autobahn.repl.wamp import REPLApplicationSession

__author__ = 'Adam Jorgensen <adam.jorgensen.za@gmail.com>'


class Session(AbstractSession):
    def __init__(self, connection: AbstractConnection,
                 authmethod: str='anonymous', authid: str=None,
                 authrole: str=None, authextra: dict=None, resumable: bool=None,
                 resume_session: int=None, resume_token: str=None):
        super().__init__(
            connection=connection, authmethod=authmethod, authid=authid,
            authrole=authrole, authextra=authextra, resumable=resumable,
            resume_session=resume_session, resume_token=resume_token
        )
        # TODO: Support custom manager classes
        self._call_manager = CallManager(self)
        self._register_manager = RegisterManager(self)
        self._publisher_manager = PublisherManager(self)
        self._subscribe_manager = SubscribeManager(self)
        # TODO: Support custom application runner class?
        runner = ApplicationRunner(
            connection.uri, connection.realm, connection.extra,
            connection.serializers, connection.ssl, connection.proxy,
            connection.headers
        )
        asyncio.ensure_future(
            runner.run(
                make=self._factory,
                start_loop=False,
                log_level='info'  # TODO: Support custom log levels?
            ),
            loop=connection.manager.loop
        )

    def _factory(self, config: ComponentConfig):
        # TODO: Support custom ApplicationSession class
        self._application_session = REPLApplicationSession(
            self, self._future, config
        )
        return self._application_session

    @property
    def call(self):
        return self._call_manager

    @property
    def register(self):
        return self._register_manager

    @property
    def publish(self):
        return self._publisher_manager

    @property
    def subscribe(self):
        return self._subscribe_manager
