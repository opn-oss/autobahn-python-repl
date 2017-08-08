import asyncio
from asyncio import AbstractEventLoop
from functools import partial

from autobahn.asyncio.wamp import ApplicationSession, ApplicationRunner
from autobahn.wamp import ComponentConfig


class Session(object):
    """
    The Session implements a synchronous interface interacting with an
    enclosed ApplicationSession instance
    """
    def __init__(self, loop: AbstractEventLoop, name: str,
                 application_session: ApplicationSession):
        self.__loop = loop
        self.__name = name
        self.__application_session = application_session

    def call(self):
        raise NotImplementedError

    def register(self):
        raise NotImplementedError

    def publish(self):
        raise NotImplementedError

    def subscribe(self):
        raise NotImplementedError


class SessionManager(object):
    """
    The SessionManager implements an interface for creating and interacting
    with asyncio WAMP sessions. Custom SessionManager implementations should
    inherit from this class
    """
    def __init__(self, loop: AbstractEventLoop, session_class: type):
        """
        Constructor for WAMP Session Manager class

        :param loop: An asyncio event loop instance
        :param session_class:
        """
        assert issubclass(session_class, Session)
        self.__loop = loop
        self.__sessions = {}
        self.__session_name__sessions = {}
        self.__session_class = session_class

    @property
    def loop(self):
        return self.__loop

    def __factory(self, config: ComponentConfig, name: str):
        if name is None:
            # TODO: Generate fake-name
            pass
        # TODO: ApplicationSession class should be customisable using command-line arguments or environment variables
        application_session = ApplicationSession(config)
        session = self.__session_class(self.__loop, name, application_session)
        session_id = id(session)
        self.__sessions[session_id] = session
        self.__session_name__sessions[name] = session_id
        return application_session

    def create(self, uri: str, realm: str, name: str=None):
        runner = ApplicationRunner(uri, realm)
        coro = runner.run(
            partial(self.__factory, name=name),
            start_loop=False
        )
        return asyncio.ensure_future(coro)

    def __getitem__(self, item: str):
        """
        Provides item-style access to a Session by name or session ID
        :param item:
        :return:
        """
        if item in self.__session_name__sessions:
            item = self.__session_name__sessions[item]
        return self.__sessions[item]

    def __getattr__(self, item: str):
        """
        Provides attribute-style access to a Session via name

        :param item:
        :return:
        """
        return self[item]
