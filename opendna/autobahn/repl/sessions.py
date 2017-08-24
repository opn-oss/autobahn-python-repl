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
from asyncio import AbstractEventLoop, Future
from functools import partial
from typing import Type

import txaio
from autobahn.asyncio.wamp import ApplicationSession, ApplicationRunner
from autobahn.wamp import ComponentConfig

from opendna.autobahn.repl.abc import (
    AbstractSession,
    AbstractSessionManager
)
from opendna.autobahn.repl.rpc import CallManager
from opendna.autobahn.repl.utils import generate_name

__author__ = 'Adam Jorgensen <adam.jorgensen.za@gmail.com>'


class Session(AbstractSession):
    """
    The Session implements a synchronous interface interacting with an
    enclosed ApplicationSession instance
    """
    def __init__(self, manager: AbstractSessionManager,
                 application_session: ApplicationSession):
        assert isinstance(manager, AbstractSessionManager)
        assert isinstance(application_session, ApplicationSession)
        self.__manager = manager
        self.__application_session = application_session
        self.__call_manager = CallManager(self)

    @property
    def session_manager(self) -> AbstractSessionManager:
        return self.__manager

    @property
    def application_session(self) -> ApplicationSession:
        return self.__application_session

    @property
    def call(self):
        return self.__call_manager

    def register(self):
        raise NotImplementedError

    def publish(self):
        raise NotImplementedError

    def subscribe(self):
        raise NotImplementedError


class SessionManager(AbstractSessionManager):
    """
    The SessionManager implements an interface for creating and interacting
    with asyncio WAMP sessions. Custom SessionManager implementations should
    inherit from this class
    """
    logger = txaio.make_logger()

    def __init__(self, loop: AbstractEventLoop,
                 session_class: Type[AbstractSession]):
        """
        Constructor for WAMP Session Manager class

        :param loop: An asyncio event loop instance
        :param session_class:
        """
        assert isinstance(loop, AbstractEventLoop)
        assert issubclass(session_class, AbstractSession)
        self.__loop = loop
        self.__sessions = {}
        self.__session_name__sessions = {}
        self.__session_class = session_class

    @property
    def loop(self):
        return self.__loop

    def __factory(self, config: ComponentConfig, name: str):
        # TODO: ApplicationSession class should be customisable using command-line arguments or environment variables
        application_session = ApplicationSession(config)
        session = self.__session_class(self, application_session)
        session_id = id(session)
        self.__sessions[session_id] = session
        self.__session_name__sessions[name] = session_id
        return application_session

    def __call__(self, uri: str, realm: str, name: str=None) -> Future:
        while name is None or name in self.__session_name__sessions:
            name = generate_name(name)
        self.logger.info(
            'Creating new Session named {name} connecting to {realm} at {uri}',
            name=name, realm=realm, uri=uri
        )
        runner = ApplicationRunner(uri, realm)
        coro = runner.run(
            partial(self.__factory, name=name),
            start_loop=False
        )
        # TODO: Find a way to return the session itself?
        return asyncio.ensure_future(coro)

    def __getitem__(self, item: str):
        """
        Provides item-style access to a Session by name or session ID
        :param item:
        :return:
        """
        item = self.__session_name__sessions.get(item, item)
        return self.__sessions[item]

    def __getattr__(self, item: str):
        """
        Provides attribute-style access to a Session via name

        :param item:
        :return:
        """
        return self[item]
