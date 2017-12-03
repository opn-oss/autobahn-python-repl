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

from autobahn.wamp.types import IRegistration
from datetime import datetime
from collections import namedtuple
from copy import deepcopy

from autobahn.wamp import CallOptions, RegisterOptions
from typing import Callable, Union, Any, Dict, Iterable, Optional

from opendna.autobahn.repl.abc import (
    AbstractInvocation,
    AbstractCall,
    AbstractCallManager,
    AbstractSession,
    AbstractRegistrationManager,
    AbstractRegistration
)
from opendna.autobahn.repl.mixins import (
    HasSession,
    ManagesNames,
    HasName,
    HasFuture,
    ManagesNamesProxy)
from opendna.autobahn.repl.utils import Keep, get_class

__author__ = 'Adam Jorgensen <adam.jorgensen.za@gmail.com>'


class Invocation(HasName, HasFuture, AbstractInvocation):

    def __init__(self,
                 call: Union[ManagesNames, AbstractCall],
                 args: Iterable,
                 kwargs: Dict[str, Any]):
        super(Invocation, self).__init__(call=call, args=args, kwargs=kwargs)
        self.__init_has_name__(call)
        self.__init_has_future__()
        self._progress = []

        def invoke(future: asyncio.Future):
            loop = call.manager.session.connection.manager.loop
            try:
                result = future.result()
                self._future = asyncio.ensure_future(self._invoke(), loop=loop)
            except Exception as e:
                print(e)
        # TODO: Fix this type confusion
        call.manager.session.future.add_done_callback(invoke)

    @property
    def progress(self) -> list:
        return self._progress

    def _default_on_progress(self, value):
        print(f'Invocation of {self._call.procedure} with name {self.name} has progress')
        self._progress.append(value)
        if callable(self._call.on_progress):
            self._call.on_progress(value)

    async def _invoke(self):
        procedure = self._call.procedure
        try:
            options = CallOptions(
                on_progress=self._default_on_progress,
                **self._call.call_options_kwargs
            )
            session = self._call.manager.session.application_session
            print(f'Invocation of {procedure} with name {self.name} starting')
            self._result = await session.call(
                procedure,
                *self._args,
                options=options,
                **self._kwargs
            )
            print(f'Invocation of {procedure} with name {self.name} succeeded')
        except Exception as e:
            print(f'Invocation of {procedure} with name {self.name} failed')
            self._exception = e

    def __call__(self, *new_args, **new_kwargs) -> AbstractInvocation:
        """

        :param new_args:
        :param new_kwargs:
        :return:
        """
        args = deepcopy(self._args)
        new_args_len = len(new_args)
        args_len = len(args)
        if new_args_len < args_len:
            new_args = list(new_args) + args[new_args_len:]
        elif new_args_len > args_len:
            new_args = new_args[:args_len]
        args = [
            arg if new_arg == Keep else new_arg
            for arg, new_arg in zip(args, new_args)
        ]
        kwargs = deepcopy(self._kwargs)
        kwargs.update(new_kwargs)
        return self._call(*args, **kwargs)


class Call(ManagesNames, AbstractCall):
    def __init__(self,
                 manager: AbstractCallManager,
                 procedure: str,
                 on_progress: Callable=None,
                 call_options_kwargs: dict=None):
        self.__init_manages_names__()
        super().__init__(
            manager=manager,
            procedure=procedure,
            on_progress=on_progress,
            call_options_kwargs=call_options_kwargs
        )
        self._proxy = ManagesNamesProxy(self)

    @property
    def invocations(self) -> ManagesNamesProxy:
        return self._proxy

    def name_for(self, item):
        invocation_class = get_class(environ['invocation'])
        assert isinstance(item, invocation_class)
        return super().name_for(id(item))

    def __call__(self, *args, **kwargs) -> AbstractInvocation:
        name = self._generate_name()
        print(f'Invoking {self.procedure} with name {name}')
        invocation_class = get_class(environ['invocation'])
        invocation = invocation_class(call=self, args=args, kwargs=kwargs)
        invocation_id = id(invocation)
        self._items[invocation_id] = invocation
        self._items__names[invocation_id] = name
        self._names__items[name] = invocation_id
        return invocation


class CallManager(HasSession, ManagesNames, AbstractCallManager):
    def __init__(self, session: AbstractSession):
        self.__init_has_session__(session)
        self.__init_manages_names__()

    def name_for(self, item):
        call_class = get_class(environ['call'])
        assert isinstance(item, call_class)
        return super().name_for(id(item))

    @ManagesNames.with_name
    def __call__(self,
                 procedure: str,
                 on_progress: Callable=None,
                 *,
                 name: str=None,
                 **call_options_kwargs) -> AbstractCall:
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
        call_class = get_class(environ['call'])
        call = call_class(
            manager=self,
            procedure=procedure,
            on_progress=on_progress,
            call_options_kwargs=call_options_kwargs
        )
        call_id = id(call)
        self._items[call_id] = call
        self._items__names[call_id] = name
        self._names__items[name] = call_id
        return call


class Registration(HasName, ManagesNames, HasFuture, AbstractRegistration):
    Hit = namedtuple('Hit', ('timestamp', 'args', 'kwargs'))

    def __init__(self, manager: Union[ManagesNames, AbstractRegistrationManager],
                 procedure: str, endpoint: Callable = None, prefix: str = None,
                 register_options_kwargs: dict = None):
        super().__init__(manager, procedure, endpoint, prefix,
                         register_options_kwargs)
        self.__init_manages_names__()
        self.__init_has_name__(manager)
        self.__init_has_future__()
        self._proxy = ManagesNamesProxy(self)

        def invoke(future: asyncio.Future):
            loop = manager.session.connection.manager.loop
            try:
                result = future.result()
                self._future = asyncio.ensure_future(self._register(), loop=loop)
            except Exception as e:
                print(e)
        # TODO: Fix this type confusion
        manager.session.future.add_done_callback(invoke)

    @property
    def hits(self) -> ManagesNamesProxy:
        return self._proxy

    @property
    def registration(self) -> Optional[IRegistration]:
        return self._registration

    def deregister(self):
        if self._registration is None:
            raise Exception(f'{self._procedure} is not registered yet')
        loop = self._manager.session.connection.manager.loop
        asyncio.ensure_future(self._deregister(), loop=loop)

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

    async def _deregister(self):
        try:
            print(f'Deregistration of {self._procedure} with name {self.name} starting')
            await self._registration.unregister()
            print(f'Deregistration of {self._procedure} with name {self.name} succeeded')
        except Exception as e:
            print(f'Deregistration of {self._procedure} with name {self.name} failed')
            self._exception = e

    async def _register(self):
        try:
            options = RegisterOptions(**self._register_options_kwargs)
            session = self._manager.session.application_session
            print(f'Registration of {self._procedure} with name {self.name} starting')
            self._registration = await session.register(
                endpoint=self._endpoint_wrapper,
                procedure=self._procedure,
                options=options,
                prefix=self._prefix
            )
            print(f'Registration of {self._procedure} with name {self.name} succeeded')
        except Exception as e:
            print(f'Registration of {self._procedure} with name {self.name} failed')
            self._exception = e

    async def _endpoint_wrapper(self, *args, **kwargs):
        name = self._generate_name()
        now = datetime.now()
        hit_id = len(self._items)
        self._items[hit_id] = self.Hit(now, args, kwargs)
        self._items__names[hit_id] = name
        self._names__items[name] = hit_id
        print(f'End-point {self._procedure} named {self.name} hit at {now}. '
              f'Hit named {name} stored')
        if asyncio.iscoroutinefunction(self._endpoint):
            return await self._endpoint(*args, **kwargs)
        if callable(self._endpoint):
            return self._endpoint(*args, **kwargs)


class RegistrationManager(HasSession, ManagesNames, AbstractRegistrationManager):
    def __init__(self, session: AbstractSession):
        self.__init_has_session__(session)
        self.__init_manages_names__()

    def name_for(self, item):
        registration_class = get_class(environ['registration'])
        assert isinstance(item, registration_class)
        return super().name_for(id(item))

    @ManagesNames.with_name
    def __call__(self,
                 procedure: str,
                 endpoint: Callable=None,
                 prefix: str=None,
                 *, name: str=None,
                 **register_options_kwargs) -> AbstractRegistration:
        print(f'Generating registration for {procedure} with name {name}')
        registration_class = get_class(environ['registration'])
        registration = registration_class(
            manager=self, procedure=procedure, endpoint=endpoint, prefix=prefix,
            register_options_kwargs=register_options_kwargs
        )
        register_id = id(registration)
        self._items[register_id] = registration
        self._items__names[register_id] = name
        self._names__items[name] = register_id
        return registration
