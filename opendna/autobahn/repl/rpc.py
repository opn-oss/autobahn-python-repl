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
from datetime import datetime
from collections import namedtuple
from copy import deepcopy

from autobahn.wamp import CallOptions, RegisterOptions
from typing import Callable, Union, Any, Dict, Iterable

from opendna.autobahn.repl.abc import (
    AbstractInvocation,
    AbstractCall,
    AbstractCallManager,
    AbstractSession,
    AbstractRegistrationManager,
    AbstractRegistration
)
from opendna.autobahn.repl.mixins import HasSession, HasNames
from opendna.autobahn.repl.utils import Keep

__author__ = 'Adam Jorgensen <adam.jorgensen.za@gmail.com>'


class Invocation(AbstractInvocation):

    def __init__(self,
                 call: AbstractCall,
                 args: Iterable,
                 kwargs: Dict[str, Any]):
        super(Invocation, self).__init__(call=call, args=args, kwargs=kwargs)

        def invoke(future: asyncio.Future):
            loop = call.manager.session.connection.manager.loop
            try:
                result = future.result()
                self._future = asyncio.ensure_future(self._invoke(), loop=loop)
            except Exception as e:
                print(e)
        call.manager.session.future.add_done_callback(invoke)

    async def _invoke(self):
        try:
            options = CallOptions(
                on_progress=(
                    self._call.on_progress if callable(self._call.on_progress)
                    else self._default_on_progress
                ),
                timeout=self._call.timeout
            )
            session = self._call.manager.session.application_session
            self._result = await session.call(
                self._call.procedure,
                *self._args,
                options=options,
                **self._kwargs
            )
        except Exception as e:
            self._exception = e

    def __call__(self, *new_args, **new_kwargs) -> AbstractInvocation:
        """

        :param new_args:
        :param new_kwargs:
        :return:
        """
        args = deepcopy(self._args)
        args = [
            arg if new_arg == Keep else new_arg
            for arg, new_arg in zip(args, new_args)
        ]
        kwargs = deepcopy(self._kwargs)
        kwargs.update(new_kwargs)
        return self._call(*args, **kwargs)


class Call(HasNames, AbstractCall):
    def __init__(self, manager: AbstractCallManager,
                 procedure: str, on_progress: Callable=None,
                 timeout: Union[int, float, None]=None):
        self.__init_has_names__()
        super().__init__(
            manager=manager, procedure=procedure, on_progress=on_progress,
            timeout=timeout
        )

    def __call__(self, *args, **kwargs) -> AbstractInvocation:
        name = self._generate_name()
        print(f'Invoking {self.procedure} with name {name}')
        # TODO: Allow custom Invocation class
        invocation = Invocation(call=self, args=args, kwargs=kwargs)
        invocation_id = id(invocation)
        self._items[invocation_id] = invocation
        self._names__items[name] = invocation_id
        return invocation


class CallManager(HasSession, HasNames, AbstractCallManager):
    def __init__(self, session: AbstractSession):
        self.__init_has_session__(session)
        self.__init_has_names__()

    @HasNames.with_name
    def __call__(self,
                 procedure: str,
                 on_progress: Callable=None,
                 timeout: Union[int, float]=None, *,
                 name: str=None) -> AbstractCall:
        """
        Generates a Callable which can be called to initiate an asynchronous
        request to the WAMP router this Session is connected to

        :param procedure:
        :param on_progress:
        :param timeout:
        :param name: Optional. Keyword-only argument.
        :return:
        """
        # while name is None or name in self.__call_name__calls:
        #     name = generate_name(name)
        print(f'Generating call to {procedure} with name {name}')
        # TODO: Allow custom Call class
        call = Call(
            manager=self, procedure=procedure, on_progress=on_progress,
            timeout=timeout
        )
        call_id = id(call)
        self._items[call_id] = call
        self._names__items[name] = call_id
        return call


class Registration(HasNames, AbstractRegistration):
    Hit = namedtuple('Hit', ('timestamp', 'args', 'kwargs'))

    def __init__(self, manager: AbstractRegistrationManager, procedure: str,
                 endpoint: Callable = None, prefix: str = None,
                 register_options_kwargs: dict = None):
        super().__init__(manager, procedure, endpoint, prefix,
                         register_options_kwargs)
        self.__init_has_names__()

        def invoke(future: asyncio.Future):
            loop = manager.session.connection.manager.loop
            try:
                result = future.result()
                self._future = asyncio.ensure_future(self._register(), loop=loop)
            except Exception as e:
                print(e)
        manager.session.future.add_done_callback(invoke)

    def __call__(self,
                 procedure: str=None,
                 endpoint: Callable=None,
                 prefix: str=None,
                 **new_register_options_kwargs) -> AbstractRegistration:
        register_options_kwargs = deepcopy(self._register_options_kwargs)
        register_options_kwargs.update(new_register_options_kwargs)
        return self._manager(
            procedure or self._procedure,
            endpoint or self._endpoint,
            prefix or self._prefix,
            **register_options_kwargs
        )

    async def _register(self):
        try:
            options = RegisterOptions(**self._register_options_kwargs)
            session = self._manager.session.application_session
            self._registration = await session.register(
                endpoint=self._endpoint,
                procedure=self._procedure,
                options=options,
                prefix=self._prefix
            )
        except Exception as e:
            self._exception = e

    async def _endpoint(self, *args, **kwargs):
        name = self._generate_name()
        now = datetime.now()
        self._items.append(self.Hit(now, args, kwargs))
        hit_id = len(self._items) - 1
        self._names__items[name] = hit_id
        print(f'{self._procedure} hit at {now} with ID {hit_id} and '
              f'name {name} stored')
        if callable(self._endpoint):
            return await self._endpoint(*args, **kwargs)


class RegistrationManager(HasSession, HasNames, AbstractRegistrationManager):
    def __init__(self, session: AbstractSession):
        self.__init_has_session__(session)
        self.__init_has_names__()

    @HasNames.with_name
    def __call__(self,
                 procedure: str,
                 endpoint: Callable=None,
                 prefix: str=None,
                 *, name: str=None,
                 **register_options_kwargs) -> AbstractRegistration:
        print(f'Generating register for {procedure} with name {name}')
        register = Registration(
            manager=self, procedure=procedure, endpoint=endpoint, prefix=prefix,
            register_options_kwargs=register_options_kwargs
        )
        register_id = id(register)
        self._items[register_id] = register
        self._names__items[name] = register_id
        return register
