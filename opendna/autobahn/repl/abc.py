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
from asyncio import AbstractEventLoop, Future

from autobahn.wamp import ComponentConfig

__author__ = 'Adam Jorgensen <adam.jorgensen.za@gmail.com>'


class AbstractSessionManager(object):

    @property
    def loop(self) -> AbstractEventLoop:
        raise NotImplementedError

    def __call__(self, *args, **kwargs):
        raise NotImplementedError

    def __getitem__(self, item):
        raise NotImplementedError

    def __getattr__(self, item):
        raise NotImplementedError


class AbstractSession(object):

    def __factory(self, config: ComponentConfig):
        raise NotImplementedError

    @property
    def session_manager(self) -> AbstractSessionManager:
        raise NotImplementedError

    @property
    def future(self) -> Future:
        raise NotImplementedError

    @property
    def uri(self):
        raise NotImplementedError

    @property
    def realm(self):
        raise NotImplementedError

    @property
    def extra(self):
        raise NotImplementedError

    @property
    def serializers(self):
        raise NotImplementedError

    @property
    def ssl(self):
        raise NotImplementedError

    @property
    def proxy(self):
        raise NotImplementedError

    @property
    def headers(self):
        raise NotImplementedError

    @property
    def application_session(self):
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


class AbstractWAMPManager(object):
    def __init__(self, session: AbstractSession):
        assert isinstance(session, AbstractSession)
        self.__session: AbstractSession = session

    @property
    def session(self) -> AbstractSession:
        return self.__session


class AbstractCallManager(AbstractWAMPManager):

    def __call__(self, *args, **kwargs):
        raise NotImplementedError

    def __getitem__(self, item):
        raise NotImplementedError

    def __getattr__(self, item):
        raise NotImplementedError


class AbstractCall(object):

    @property
    def call_manager(self) -> AbstractCallManager:
        raise NotImplementedError

    @property
    def procedure(self):
        raise NotImplementedError

    @property
    def on_progress(self):
        raise NotImplementedError

    @property
    def timeout(self):
        raise NotImplementedError

    def __call__(self, *args, **kwargs):
        raise NotImplementedError

    def __getitem__(self, item):
        raise NotImplementedError

    def __getattr__(self, item):
        raise NotImplementedError


class AbstractInvocation(object):

    @property
    def result(self):
        raise NotImplementedError

    @property
    def progress(self):
        raise NotImplementedError

    @property
    def exception(self):
        raise NotImplementedError

    def __default_on_progress(self, value):
        raise NotImplementedError

    async def __invoke(self):
        raise NotImplementedError

    def __call__(self, *args, **kwargs):
        raise NotImplementedError


class AbstractRegister(object):
    pass


class AbstractPublisherManager(AbstractWAMPManager):
    pass


class AbstractPublisher(object):
    pass


class AbstractPublication(object):
    pass


class AbstractSubscribe(object):
    pass




