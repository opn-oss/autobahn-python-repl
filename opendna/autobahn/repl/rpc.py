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
from opendna.autobahn.repl.mixins import HasSession, ManagesNames, HasName
from opendna.autobahn.repl.utils import Keep

__author__ = 'Adam Jorgensen <adam.jorgensen.za@gmail.com>'


class Invocation(HasName, AbstractInvocation):

    def __init__(self,
                 call: Union[ManagesNames, AbstractCall],
                 args: Iterable,
                 kwargs: Dict[str, Any]):
        super(Invocation, self).__init__(call=call, args=args, kwargs=kwargs)
        self.__init_has_name__(call)

        def invoke(future: asyncio.Future):
            loop = call.manager.session.connection.manager.loop
            try:
                result = future.result()
                self._future = asyncio.ensure_future(self._invoke(), loop=loop)
            except Exception as e:
                print(e)
        call.manager.session.future.add_done_callback(invoke)

    def _default_on_progress(self, value):
        print(f'Invocation of {self._call.procedure} with name {self.name} has progress')
        super()._default_on_progress(value)
        if callable(self._call.on_progress):
            self._call.on_progress(value)

    async def _invoke(self):
        procedure = self._call.procedure
        try:
            options = CallOptions(
                on_progress=self._default_on_progress,
                timeout=self._call.timeout
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
        args = [
            arg if new_arg == Keep else new_arg
            for arg, new_arg in zip(args, new_args)
        ]
        kwargs = deepcopy(self._kwargs)
        kwargs.update(new_kwargs)
        return self._call(*args, **kwargs)


class Call(ManagesNames, AbstractCall):
    def __init__(self, manager: AbstractCallManager,
                 procedure: str, on_progress: Callable=None,
                 timeout: Union[int, float, None]=None):
        self.__init_manages_names__()
        super().__init__(
            manager=manager, procedure=procedure, on_progress=on_progress,
            timeout=timeout
        )

    def name_for(self, item):
        # TODO: Allow custom Invocation class
        assert isinstance(item, Invocation)
        return super().name_for(id(item))

    def __call__(self, *args, **kwargs) -> AbstractInvocation:
        name = self._generate_name()
        print(f'Invoking {self.procedure} with name {name}')
        # TODO: Allow custom Invocation class
        invocation = Invocation(call=self, args=args, kwargs=kwargs)
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
        # TODO: Allow custom Call class
        assert isinstance(item, Call)
        return super().name_for(id(item))

    @ManagesNames.with_name
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
        self._items__names[call_id] = name
        self._names__items[name] = call_id
        return call


class Registration(HasName, ManagesNames, AbstractRegistration):
    Hit = namedtuple('Hit', ('timestamp', 'args', 'kwargs'))

    def __init__(self, manager: Union[ManagesNames, AbstractRegistrationManager],
                 procedure: str, endpoint: Callable = None, prefix: str = None,
                 register_options_kwargs: dict = None):
        super().__init__(manager, procedure, endpoint, prefix,
                         register_options_kwargs)
        self.__init_manages_names__()
        self.__init_has_name__(manager)
        self._future = None
        self._registration: Optional[IRegistration] = None

        def invoke(future: asyncio.Future):
            loop = manager.session.connection.manager.loop
            try:
                result = future.result()
                self._future = asyncio.ensure_future(self._register(), loop=loop)
            except Exception as e:
                print(e)
        manager.session.future.add_done_callback(invoke)

    @property
    def registration(self) -> Optional[IRegistration]:
        return self._registration

    def unregister(self):
        if self._registration is None:
            raise Exception(f'{self._procedure} is not registered yet')
        loop = self._manager.session.connection.manager.loop
        asyncio.ensure_future(self._unregister(), loop=loop)

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

    async def _unregister(self):
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
                endpoint=self._endpoint,
                procedure=self._procedure,
                options=options,
                prefix=self._prefix
            )
            print(f'Registration of {self._procedure} with name {self.name} succeeded')
        except Exception as e:
            print(f'Registration of {self._procedure} with name {self.name} failed')
            self._exception = e

    async def _endpoint(self, *args, **kwargs):
        name = self._generate_name()
        now = datetime.now()
        self._items.append(self.Hit(now, args, kwargs))
        hit_id = len(self._items) - 1
        self._names__items[name] = hit_id
        print(f'{self._procedure} with name {self.name} hit at {now} with '
              f'ID {hit_id} and hit name {name} stored')
        if callable(self._endpoint):
            return await self._endpoint(*args, **kwargs)


class RegistrationManager(HasSession, ManagesNames, AbstractRegistrationManager):
    def __init__(self, session: AbstractSession):
        self.__init_has_session__(session)
        self.__init_manages_names__()

    def name_for(self, item):
        # TODO: Allow custom Registration class
        assert isinstance(item, Registration)
        return super().name_for(id(item))

    @ManagesNames.with_name
    def __call__(self,
                 procedure: str,
                 endpoint: Callable=None,
                 prefix: str=None,
                 *, name: str=None,
                 **register_options_kwargs) -> AbstractRegistration:
        print(f'Generating registration for {procedure} with name {name}')
        # TODO: Allow custom Registration class
        registration = Registration(
            manager=self, procedure=procedure, endpoint=endpoint, prefix=prefix,
            register_options_kwargs=register_options_kwargs
        )
        register_id = id(registration)
        self._items[register_id] = registration
        self._items__names[register_id] = name
        self._names__items[name] = register_id
        return registration
