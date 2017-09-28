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
from typing import Callable, Union, List, Iterable, Dict, Any, Optional

from autobahn.wamp import ComponentConfig
from autobahn.wamp.interfaces import ISerializer


__author__ = 'Adam Jorgensen <adam.jorgensen.za@gmail.com>'


class AbstractConnectionManager(object):
    @property
    def loop(self) -> AbstractEventLoop:
        raise NotImplementedError

    def __call__(self, *args, **kwargs) -> 'AbstractConnection':
        raise NotImplementedError


class AbstractConnection(object):
    def __init__(self, manager: AbstractConnectionManager, uri: str, realm: str,
                 extra: dict=None, serializers: List[ISerializer]=None,
                 ssl: Union[SSLContext, bool]=None, proxy: dict=None,
                 headers: dict=None):
        assert isinstance(manager, AbstractConnectionManager)
        assert isinstance(uri, str)
        assert realm is None or isinstance(realm, str)
        assert extra is None or isinstance(extra, dict)
        assert serializers is None or isinstance(serializers, list)
        assert ssl is None or isinstance(ssl, (SSLContext, bool))
        assert proxy is None or isinstance(proxy, dict)
        assert headers is None or isinstance(headers, dict)
        self._manager = manager
        self._uri = uri
        self._realm = realm
        self._extra = extra
        self._serializers = serializers
        self._ssl = ssl
        self._proxy = proxy
        self._headers = headers

    @property
    def manager(self) -> AbstractConnectionManager:
        return self._manager

    @property
    def uri(self):
        return self._uri

    @property
    def realm(self):
        return self._realm

    @property
    def extra(self):
        return self._extra

    @property
    def serializers(self):
        return self._serializers

    @property
    def ssl(self):
        return self._ssl

    @property
    def proxy(self):
        return self._proxy

    @property
    def headers(self):
        return self._headers

    def session(self, authmethod: str, authid: str=None,
                authrole: str=None, authextra: dict=None, resumable: bool=None,
                resume_session: int=None, resume_token: str=None,
                *, name: str=None) -> 'AbstractSession':
        raise NotImplementedError


class AbstractSession(object):
    def __init__(self, connection: AbstractConnection,
                 authmethod: str='anonymous', authid: str=None,
                 authrole: str=None, authextra: dict=None, resumable: bool=None,
                 resume_session: int=None, resume_token: str=None):
        self._connection = connection
        self._authmethod = authmethod
        self._authid = authid
        self._authrole = authrole
        self._authextra = authextra
        self._resumable = resumable
        self._resume_session = resume_session
        self._resume_token = resume_token
        self._application_session = None
        self._future: asyncio.Future = connection.manager.loop.create_future()

    @property
    def connection(self) -> AbstractConnection:
        return self._connection

    @property
    def authmethod(self) -> str:
        return self._authmethod

    @property
    def authid(self) -> Optional[str]:
        return self._authid

    @property
    def authrole(self) -> Optional[str]:
        return self._authrole

    @property
    def authextra(self) -> Optional[dict]:
        return self._authextra

    @property
    def resumable(self) -> Optional[bool]:
        return self._resumable

    @property
    def resume_session(self) -> Optional[int]:
        return self._resume_session

    @property
    def resume_token(self) -> Optional[str]:
        return self._resume_token

    @property
    def future(self) -> asyncio.Future:
        return self._future

    @property
    def application_session(self):
        return self._application_session

    def _factory(self, config: ComponentConfig):
        raise NotImplementedError

    @property
    def call(self):
        raise NotImplementedError

    @property
    def register(self):
        raise NotImplementedError

    @property
    def publish(self):
        raise NotImplementedError

    @property
    def subscribe(self):
        raise NotImplementedError


class AbstractCallManager(object):
    @property
    def session(self) -> AbstractSession:
        raise NotImplementedError

    def __call__(self, *args, **kwargs) -> 'AbstractCall':
        raise NotImplementedError

    def __getitem__(self, item) -> 'AbstractCall':
        raise NotImplementedError

    def __getattr__(self, item) -> 'AbstractCall':
        raise NotImplementedError


class AbstractCall(object):
    def __init__(self, manager: AbstractCallManager,
                 procedure: str, on_progress: Callable=None,
                 timeout: Union[int, float, None]=None):
        assert isinstance(manager, AbstractCallManager)
        self._manager = manager
        self._procedure = procedure
        self._on_progress = on_progress
        self._timeout = timeout

    @property
    def manager(self) -> AbstractCallManager:
        return self._manager

    @property
    def procedure(self) -> str:
        return self._procedure

    @property
    def on_progress(self) -> Callable:
        return self._on_progress

    @property
    def timeout(self) -> Union[int, float, None]:
        return self._timeout

    def __call__(self, *args, **kwargs) -> 'AbstractInvocation':
        raise NotImplementedError

    def __getitem__(self, item) -> 'AbstractInvocation':
        raise NotImplementedError

    def __getattr__(self, item) -> 'AbstractInvocation':
        raise NotImplementedError


class AbstractInvocation(object):
    def __init__(self, call: 'AbstractCall', args: Iterable,
                 kwargs: Dict[str, Any]):
        self._call = call
        self._args = args
        self._kwargs = kwargs
        self._progress = []
        self._result = None
        self._exception = None

    @property
    def result(self) -> Optional[Any]:
        return self._result

    @property
    def progress(self) -> list:
        return self._progress

    @property
    def exception(self) -> Optional[Exception]:
        return self._exception

    def _default_on_progress(self, value):
        self._progress.append(value)

    async def _invoke(self):
        raise NotImplementedError

    def __call__(self, *args, **kwargs):
        raise NotImplementedError


class AbstractRegisterManager(object):
    @property
    def session(self) -> AbstractSession:
        raise NotImplementedError

    def __call__(self, *args, **kwargs) -> 'AbstractRegister':
        raise NotImplementedError

    def __getitem__(self, item) -> 'AbstractRegister':
        raise NotImplementedError

    def __getattr__(self, item) -> 'AbstractRegister':
        raise NotImplementedError


class AbstractRegister(object):
    pass


class AbstractRegistration(object):
    pass


class AbstractPublisherManager(object):
    @property
    def session(self) -> AbstractSession:
        raise NotImplementedError

    def __call__(self, *args, **kwargs) -> 'AbstractPublisher':
        raise NotImplementedError

    def __getitem__(self, item) -> 'AbstractPublisher':
        raise NotImplementedError

    def __getattr__(self, item) -> 'AbstractPublisher':
        raise NotImplementedError


class AbstractPublisher(object):
    def __init__(self,
                 manager: AbstractPublisherManager,
                 topic: str,
                 acknowledge: bool=None,
                 exclude_me: bool=None,
                 exclude: Union[int, List[int]]=None,
                 exclude_authid: Union[str, List[str]]=None,
                 exclude_authrole: Union[str, List[str]]=None,
                 eligible: Union[int, List[int]]=None,
                 eligible_authid: Union[str, List[str]]=None,
                 eligible_authrole: Union[str, List[str]]=None,
                 retain: bool=None):
        assert isinstance(manager, AbstractPublisherManager)
        self._manager = manager
        self._topic = topic
        self._acknowledge = acknowledge
        self._exclude_me = exclude_me
        self._exclude = exclude
        self._exclude_authid = exclude_authid
        self._exclude_authrole = exclude_authrole
        self._eligible = eligible
        self._eligible_authid = eligible_authid
        self._eligible_authrole = eligible_authrole
        self._retain = retain

    @property
    def manager(self) -> AbstractPublisherManager:
        return self._manager

    @property
    def topic(self) -> str:
        return self._topic

    @property
    def acknowledge(self):
        return self._acknowledge

    @property
    def exclude_me(self) -> bool:
        return self._exclude_me

    @property
    def exclude(self) -> Union[int, List[int]]:
        return self._exclude

    @property
    def exclude_authid(self) -> Union[str, List[str]]:
        return self._exclude_authid

    @property
    def exclude_authrole(self) -> Union[str, List[str]]:
        return self._exclude_authrole

    @property
    def eligible(self) -> Union[int, List[int]]:
        return self._eligible

    @property
    def eligible_authid(self) -> Union[str, List[str]]:
        return self._eligible_authid

    @property
    def eligible_authrole(self) -> Union[str, List[str]]:
        return self._eligible_authrole

    @property
    def retain(self) -> bool:
        return self._retain

    def __call__(self, *args, **kwargs) -> 'AbstractPublication':
        raise NotImplementedError

    def __getitem__(self, item) -> 'AbstractPublication':
        raise NotImplementedError

    def __getattr__(self, item) -> 'AbstractPublication':
        raise NotImplementedError


class AbstractPublication(object):
    def __init__(self, publisher: AbstractPublisher,
                 args: Iterable, kwargs: Dict[str, Any]):
        assert isinstance(publisher, AbstractPublisher)
        self._publisher = publisher
        self._args = args
        self._kwargs = kwargs
        self._result = None
        self._exception = None

    @property
    def result(self) -> Optional[Any]:
        return self._result

    @property
    def exception(self) -> Exception:
        return self._exception

    async def _invoke(self):
        raise NotImplementedError

    def __call__(self, *args, **kwargs) -> 'AbstractPublication':
        raise NotImplementedError


class AbstractSubscribeManager(object):
    @property
    def session(self) -> AbstractSession:
        raise NotImplementedError

    def __call__(self, *args, **kwargs) -> 'AbstractSubscribe':
        raise NotImplementedError

    def __getitem__(self, item) -> 'AbstractSubscribe':
        raise NotImplementedError

    def __getattr__(self, item) -> 'AbstractSubscribe':
        raise NotImplementedError


class AbstractSubscribe(object):
    pass


class AbstractSubscription(object):
    pass
