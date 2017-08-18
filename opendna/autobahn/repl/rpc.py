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
from typing import Callable, Union

from autobahn.asyncio import ApplicationSession
from autobahn.wamp import CallOptions

from opendna.autobahn.repl.abc import AbstractCall, AbstractCallManager
from opendna.autobahn.repl.utils import generate_name

__author__ = 'Adam Jorgensen <adam.jorgensen.za@gmail.com>'


class Call(AbstractCall):
    def __init__(self, loop: AbstractEventLoop,
                 application_session: ApplicationSession,
                 procedure: str, on_progress: Callable=None,
                 timeout: Union[int, float]=None):
        assert isinstance(loop, AbstractEventLoop)
        assert isinstance(application_session, ApplicationSession)
        self.__loop = loop
        self.__application_session = application_session
        self.__procedure = procedure
        self.__on_progress = on_progress
        self.__timeout = timeout
        self.__results = {}
        self.__exceptions = {}
        self.__progressive_results = {}

    @property
    def application_session(self):
        return self.__application_session

    @property
    def procedure(self):
        return self.__procedure

    @property
    def on_progress(self):
        return self.__on_progress

    @property
    def timeout(self):
        return self.__timeout

    def __call__(self, *args, **kwargs) -> int:
        async def call():
            on_progress = self.__on_progress
            if not callable(on_progress):
                def on_progress(value):
                    progress = self.__progressive_results.setdefault(call_id, [])
                    progress.append(value)
            try:
                result = await self.__application_session.call(
                    self.__procedure,
                    *args,
                    options=CallOptions(on_progress, self.__timeout),
                    **kwargs
                )
                results = self.__results.setdefault(call_id, [])
                results.append(result)
            except Exception as e:
                self.__exceptions[call_id] = e

        call_id = id(call)
        asyncio.ensure_future(call(), loop=self.__loop)
        return call_id


class CallManager(AbstractCallManager):
    def __init__(self, loop: AbstractEventLoop,
                 application_session: ApplicationSession):
        self.__loop = loop
        self.__application_session = application_session
        self.__call_name__calls = {}
        self.__calls = {}

    def __call__(self,
                 procedure: str,
                 name: str=None,
                 on_progress: Callable=None,
                 timeout: Union[int, float]=None) -> AbstractCall:
        """
        Generates a Callable which can be called to initiate an asynchronous
        request to the WAMP router this Session is connected to

        :param procedure:
        :param name:
        :param on_progress:
        :param timeout:
        :return:
        """
        name = generate_name(name)
        # TODO: Call class custom
        call = Call(
            self.__loop, self.__application_session, procedure, on_progress,
            timeout
        )
        call_id = id(call)
        self.__calls[call_id] = call
        self.__call_name__calls[name] = call_id
        return call

    def __getitem__(self, item: str):
        item = self.__call_name__calls.get(item, item)
        return self.__calls[item]

    def __getattr__(self, item: str):
        return self[item]
