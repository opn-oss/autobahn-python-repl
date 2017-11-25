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
from asyncio import AbstractEventLoop
from os import environ
from ssl import SSLContext
from typing import List, Union, Iterable

from autobahn.wamp.interfaces import ISerializer

from opendna.autobahn.repl.abc import (
    AbstractConnection,
    AbstractConnectionManager,
    AbstractSession
)
from opendna.autobahn.repl.mixins import ManagesNames, HasLoop, HasName, \
    ManagesNamesProxy
from opendna.autobahn.repl.utils import get_class

__author__ = 'Adam Jorgensen <adam.jorgensen.za@gmail.com>'


class Connection(HasName, ManagesNames, AbstractConnection):
    def __init__(self,
                 manager: Union[ManagesNames, AbstractConnectionManager],
                 uri: str,
                 realm: str,
                 extra: dict=None,
                 serializers: List[ISerializer]=None,
                 ssl: Union[SSLContext, bool]=None,
                 proxy: dict=None,
                 headers: dict=None):
        super().__init__(
            manager=manager, uri=uri, realm=realm, extra=extra,
            serializers=serializers, ssl=ssl, proxy=proxy, headers=headers
        )
        self.__init_has_name__(manager)
        self.__init_manages_names__()
        self._sessions_proxy = ManagesNamesProxy(self)

    @property
    def sessions(self) -> ManagesNamesProxy:
        return self._sessions_proxy

    def name_for(self, item):
        session_class = get_class(environ['session'])
        assert isinstance(item, session_class)
        return super().name_for(id(item))

    @ManagesNames.with_name
    def session(self,
                authmethods: Union[str, List[str]]= 'anonymous',
                authid: str=None,
                authrole: str=None,
                authextra: dict=None,
                resumable: bool=None,
                resume_session: int=None,
                resume_token: str=None,
                *,
                name: str=None,
                **session_kwargs) -> AbstractSession:
        print(
            f'Generating {authmethods} session to {self._realm}@{self._uri} '
            f'with name {name}'
        )
        session_class = get_class(environ['session'])
        session = session_class(
            connection=self, authmethods=authmethods, authid=authid,
            authrole=authrole, authextra=authextra, resumable=resumable,
            resume_session=resume_session, resume_token=resume_token,
            **session_kwargs
        )
        session_id = id(session)
        self._items[session_id] = session
        self._items__names[session_id] = name
        self._names__items[name] = session_id
        return session

    def __call__(self,
                 authmethods: Union[str, List[str]]= 'anonymous',
                 authid: str=None,
                 authrole: str=None,
                 authextra: dict=None,
                 resumable: bool=None,
                 resume_session: int=None,
                 resume_token: str=None,
                 *,
                 name: str=None,
                 **session_kwargs):
        return self.session(
            authmethods, authid, authrole, authextra, resumable, resume_session,
            resume_token, name=name, **session_kwargs
        )


class ConnectionManager(ManagesNames, HasLoop, AbstractConnectionManager):

    def __init__(self, loop: AbstractEventLoop):
        super().__init__()
        self.__init_manages_names__()
        self.__init_has_loop__(loop)

    def name_for(self, item):
        connection_class = get_class(environ['connection'])
        assert isinstance(item, connection_class)
        return super().name_for(id(item))

    @ManagesNames.with_name
    def __call__(self,
                 uri: str,
                 realm: str=None,
                 extra=None,
                 serializers=None,
                 ssl=None,
                 proxy=None,
                 headers=None,
                 *,
                 name: str=None) -> AbstractConnection:

        print(f'Generating connection to {realm}@{uri} with name {name}')
        connection_class = get_class(environ['connection'])
        connection = connection_class(
            manager=self, uri=uri, realm=realm, extra=extra,
            serializers=serializers, ssl=ssl, proxy=proxy, headers=headers
        )
        connection_id = id(connection)
        self._items[connection_id] = connection
        self._items__names[connection_id] = name
        self._names__items[name] = connection_id
        return connection


