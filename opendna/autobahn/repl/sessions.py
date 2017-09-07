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
from asyncio import AbstractEventLoop
from ssl import SSLContext

from autobahn.asyncio.wamp import ApplicationSession, ApplicationRunner
from autobahn.wamp import ComponentConfig
from autobahn.wamp.interfaces import ISerializer
from typing import Type, List, Union

from opendna.autobahn.repl.abc import (
    AbstractSession,
    AbstractSessionManager
)
from opendna.autobahn.repl.mixins import HasNames
from opendna.autobahn.repl.pubsub import PublisherManager
from opendna.autobahn.repl.rpc import CallManager
from opendna.autobahn.repl.wamp import REPLApplicationSession

__author__ = 'Adam Jorgensen <adam.jorgensen.za@gmail.com>'


class Session(AbstractSession):
    """
    The Session implements a synchronous interface interacting with an
    enclosed ApplicationSession instance
    """
    def __init__(self, manager: AbstractSessionManager, uri: str, realm: str,
                 extra: dict=None, serializers: List[ISerializer]=None,
                 ssl: Union[SSLContext, bool]=None, proxy: dict=None,
                 headers: dict=None):
        assert isinstance(manager, AbstractSessionManager)
        assert isinstance(uri, str)
        assert realm is None or isinstance(realm, str)
        assert extra is None or isinstance(extra, dict)
        assert serializers is None or isinstance(serializers, list)
        assert ssl is None or isinstance(ssl, (SSLContext, bool))
        assert proxy is None or isinstance(proxy, dict)
        assert headers is None or isinstance(headers, dict)
        self.__manager = manager
        self.__uri = uri
        self.__realm = realm
        self.__extra = extra
        self.__serializers = serializers
        self.__ssl = ssl
        self.__proxy = proxy
        self.__headers = headers
        self.__call_manager = CallManager(self)
        self.__publisher_manager = PublisherManager(self)
        self.__application_session = None
        runner = ApplicationRunner(
            uri, realm, extra, serializers, ssl, proxy, headers
        )
        self.__future: asyncio.Future = manager.loop.create_future()
        asyncio.ensure_future(
            runner.run(
                make=self.__factory,
                start_loop=False,
                log_level='info'  # TODO: Support custom log levels?
            ),
            loop=manager.loop
        )

    def __factory(self, config: ComponentConfig):
        # TODO: Support custom ApplicationSession class
        self.__application_session = REPLApplicationSession(
            self.__future, config
        )
        return self.__application_session

    @property
    def session_manager(self) -> AbstractSessionManager:
        return self.__manager

    @property
    def future(self) -> asyncio.Future:
        return self.__future

    @property
    def uri(self):
        return self.__uri

    @property
    def realm(self):
        return self.__realm

    @property
    def extra(self):
        return self.__extra

    @property
    def serializers(self):
        return self.__serializers

    @property
    def ssl(self):
        return self.__ssl

    @property
    def proxy(self):
        return self.__proxy

    @property
    def headers(self):
        return self.__headers

    @property
    def application_session(self) -> ApplicationSession:
        return self.__application_session

    @property
    def call(self) -> CallManager:
        return self.__call_manager

    @property
    def register(self):
        raise NotImplementedError

    @property
    def publish(self) -> PublisherManager:
        return self.__publisher_manager

    @property
    def subscribe(self):
        raise NotImplementedError


class SessionManager(HasNames, AbstractSessionManager):
    """
    The SessionManager implements an interface for creating and interacting
    with asyncio WAMP sessions. Custom SessionManager implementations should
    inherit from this class
    """
    def __init__(self, loop: AbstractEventLoop,
                 session_class: Type[AbstractSession]):
        """
        Constructor for WAMP Session Manager class

        :param loop: An asyncio event loop instance
        :param session_class:
        """
        assert isinstance(loop, AbstractEventLoop)
        assert issubclass(session_class, AbstractSession)
        self.__init_has_names__()
        self.__loop = loop
        self.__session_class = session_class

    @property
    def loop(self):
        return self.__loop

    @HasNames.with_name
    def __call__(self, uri: str, realm: str=None, extra=None,
                 serializers=None, ssl=None, proxy=None, headers=None, *,
                 name: str=None) -> AbstractSession:
        print(f'Generating session to {realm}@{uri} with name {name}')
        session = Session(
            self, uri, realm, extra, serializers, ssl, proxy, headers
        )
        session_id = id(session)
        self._items[session_id] = session
        self._names__items[name] = session_id
        return session
