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

from autobahn.wamp import ComponentConfig, RegisterOptions
from autobahn.wamp.types import IRegistration, ISubscription
from autobahn.wamp.interfaces import ISerializer, ISession

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
    def __init__(self,
                 connection: AbstractConnection,
                 authmethods: Union[str, List[str]]= 'anonymous',
                 authid: str=None,
                 authrole: str=None,
                 authextra: dict=None,
                 resumable: bool=None,
                 resume_session: int=None,
                 resume_token: str=None,
                 **session_kwargs):
        authmethods = [authmethods] if isinstance(authmethods, str) else authmethods
        self._connection = connection
        self._authmethods = authmethods
        self._authid = authid
        self._authrole = authrole
        self._authextra = authextra
        self._resumable = resumable
        self._resume_session = resume_session
        self._resume_token = resume_token
        self._session_kwargs = session_kwargs
        self._application_session = None

    @property
    def connection(self) -> AbstractConnection:
        return self._connection

    @property
    def authmethods(self) -> str:
        return self._authmethods

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
    def session_kwargs(self) -> Dict[str, Any]:
        return self._session_kwargs

    @property
    def application_session(self) -> ISession:
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
    def __init__(self,
                 manager: AbstractCallManager,
                 procedure: str,
                 on_progress: Callable=None,
                 call_options_kwargs: dict=None):
        assert isinstance(manager, AbstractCallManager)
        self._manager = manager
        self._procedure = procedure
        self._on_progress = on_progress
        self._call_options_kwargs = call_options_kwargs

    @property
    def manager(self) -> AbstractCallManager:
        return self._manager

    @property
    def procedure(self) -> str:
        return self._procedure

    @property
    def on_progress(self) -> Optional[Callable]:
        return self._on_progress

    @property
    def call_options_kwargs(self) -> Optional[dict]:
        return self._call_options_kwargs

    def __call__(self, *args, **kwargs) -> 'AbstractInvocation':
        raise NotImplementedError

    def __getitem__(self, item) -> 'AbstractInvocation':
        raise NotImplementedError

    def __getattr__(self, item) -> 'AbstractInvocation':
        raise NotImplementedError


class AbstractInvocation(object):
    def __init__(self,
                 call: 'AbstractCall',
                 args: Iterable,
                 kwargs: Dict[str, Any]):
        self._call = call
        self._args = args
        self._kwargs = kwargs
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
        raise NotImplementedError

    async def _invoke(self):
        raise NotImplementedError

    def __call__(self, *args, **kwargs):
        raise NotImplementedError


class AbstractRegistrationManager(object):
    @property
    def session(self) -> AbstractSession:
        raise NotImplementedError

    def __call__(self, *args, **kwargs) -> 'AbstractRegistration':
        raise NotImplementedError

    def __getitem__(self, item) -> 'AbstractRegistration':
        raise NotImplementedError

    def __getattr__(self, item) -> 'AbstractRegistration':
        raise NotImplementedError


class AbstractRegistration(object):
    def __init__(self,
                 manager: AbstractRegistrationManager,
                 procedure: str,
                 endpoint: Callable=None,
                 prefix: str=None,
                 register_options_kwargs: dict=None):
        assert isinstance(manager, AbstractRegistrationManager)
        self._manager = manager
        self._procedure = procedure
        self._endpoint = endpoint
        self._prefix = prefix
        self._register_options_kwargs = register_options_kwargs
        self._registration = None
        self._exception = None

    @property
    def manager(self) -> AbstractRegistrationManager:
        return self._manager

    @property
    def procedure(self) -> str:
        return self._procedure

    @property
    def endpoint(self) -> Optional[Callable]:
        return self._endpoint

    @property
    def prefix(self) -> Optional[str]:
        return self._prefix

    @property
    def register_options_kwargs(self) -> Optional[dict]:
        return self._register_options_kwargs

    @property
    def registration(self) -> Optional[IRegistration]:
        return self._registration

    @property
    def exception(self) -> Optional[Exception]:
        return self._exception

    def deregister(self):
        raise NotImplementedError

    async def _deregister(self):
        raise NotImplementedError

    async def _register(self):
        raise NotImplementedError

    async def _endpoint_wrapper(self, *args, **kwargs):
        raise NotImplementedError

    def __call__(self, *args, **kwargs):
        raise NotImplementedError


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
                 publish_options_kwargs: dict=None):
        assert isinstance(manager, AbstractPublisherManager)
        self._manager = manager
        self._topic = topic
        self._publish_options_kwargs = publish_options_kwargs

    @property
    def manager(self) -> AbstractPublisherManager:
        return self._manager

    @property
    def topic(self) -> str:
        return self._topic

    @property
    def publish_options_kwargs(self) -> Optional[dict]:
        return self._publish_options_kwargs

    def __call__(self, *args, **kwargs) -> 'AbstractPublication':
        raise NotImplementedError

    def __getitem__(self, item) -> 'AbstractPublication':
        raise NotImplementedError

    def __getattr__(self, item) -> 'AbstractPublication':
        raise NotImplementedError


class AbstractPublication(object):
    def __init__(self,
                 publisher: AbstractPublisher,
                 args: Iterable,
                 kwargs: Dict[str, Any]):
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


class AbstractSubscriptionManager(object):
    @property
    def session(self) -> AbstractSession:
        raise NotImplementedError

    def __call__(self, *args, **kwargs) -> 'AbstractSubscription':
        raise NotImplementedError

    def __getitem__(self, item) -> 'AbstractSubscription':
        raise NotImplementedError

    def __getattr__(self, item) -> 'AbstractSubscription':
        raise NotImplementedError


class AbstractSubscription(object):
    def __init__(self,
                 manager: AbstractSubscriptionManager,
                 topic: str,
                 handler: Callable=None,
                 subscribe_options_kwargs: dict=None):
        self._manager = manager
        self._topic = topic
        self._handler = handler
        self._subscribe_options_kwargs = subscribe_options_kwargs
        self._subscription = None
        self._exception = None

    @property
    def manager(self) -> AbstractSubscriptionManager:
        return self._manager

    @property
    def topic(self) -> str:
        return self._topic

    @property
    def handler(self) -> Optional[Callable]:
        return self._handler

    @property
    def subscribe_options_kwargs(self) -> Optional[dict]:
        return self._subscribe_options_kwargs

    @property
    def subscription(self) -> Optional[ISubscription]:
        return self._subscription

    @property
    def exception(self) -> Optional[Exception]:
        return self._exception

    def unsubscribe(self):
        raise NotImplementedError

    async def _unsubscribe(self):
        raise NotImplementedError

    async def _subscribe(self):
        raise NotImplementedError

    async def _handler_wrapper(self, *args, **kwargs):
        raise NotImplementedError

    def __call__(self, *args, **kwargs):
        raise NotImplementedError

