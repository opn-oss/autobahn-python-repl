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
from os import environ

from typing import Union, List

from autobahn.wamp import ComponentConfig

from opendna.autobahn.repl.abc import (
    AbstractSession,
    AbstractConnection
)
from opendna.autobahn.repl.mixins import ManagesNames, HasName, HasFuture, \
    ManagesNamesProxy
from opendna.autobahn.repl.utils import get_class

__author__ = 'Adam Jorgensen <adam.jorgensen.za@gmail.com>'


class Session(HasFuture, HasName, AbstractSession):
    def __init__(self,
                 connection: Union[ManagesNames, AbstractConnection],
                 authmethods: Union[str, List[str]]= 'anonymous',
                 authid: str=None,
                 authrole: str=None,
                 authextra: dict=None,
                 resumable: bool=None,
                 resume_session: int=None,
                 resume_token: str=None,
                 **session_kwargs):
        super().__init__(
            connection=connection, authmethods=authmethods, authid=authid,
            authrole=authrole, authextra=authextra, resumable=resumable,
            resume_session=resume_session, resume_token=resume_token,
            **session_kwargs
        )
        self.__init_has_name__(connection)
        self.__init_has_future__(connection.manager.loop.create_future())
        call_manager_class = get_class(environ['call_manager'])
        self._call_manager = call_manager_class(self)
        self._call_manager_proxy = ManagesNamesProxy(self._call_manager)
        registration_manager_class = get_class(environ['registration_manager'])
        self._register_manager = registration_manager_class(self)
        self._register_manager_proxy = ManagesNamesProxy(self._register_manager)
        publisher_manager_class = get_class(environ['publisher_manager'])
        self._publisher_manager = publisher_manager_class(self)
        self._publisher_manager_proxy = ManagesNamesProxy(self._publisher_manager)
        subscription_manager_class = get_class(environ['subscription_manager'])
        self._subscribe_manager = subscription_manager_class(self)
        self._subscribe_manager_proxy = ManagesNamesProxy(self._subscribe_manager)
        application_runner_class = get_class(environ['application_runner'])
        runner = application_runner_class(
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
        application_session_class = get_class(environ['application_session'])
        self._application_session = application_session_class(
            self, self._future, config
        )
        return self._application_session

    @property
    def calls(self) -> ManagesNamesProxy:
        return self._call_manager_proxy

    @property
    def registrations(self) -> ManagesNamesProxy:
        return self._register_manager_proxy

    @property
    def publishers(self):
        return self._publisher_manager_proxy

    @property
    def subscriptions(self) -> ManagesNamesProxy:
        return self._subscribe_manager_proxy

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
