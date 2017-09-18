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
from copy import deepcopy

from autobahn.wamp import PublishOptions
from typing import Union, List, Iterable, Dict, Any

from opendna.autobahn.repl.abc import (
    AbstractPublication,
    AbstractPublisher,
    AbstractPublisherManager,
    AbstractSession
)
from opendna.autobahn.repl.mixins import HasNames, HasSession
from opendna.autobahn.repl.utils import Keep

__author__ = 'Adam Jorgensen <adam.jorgensen.za@gmail.com>'


class Publication(AbstractPublication):
    def __init__(self, publisher: AbstractPublisher,
                 args: Iterable, kwargs: Dict[str, Any]):
        super(Publication, self).__init__(
            publisher=publisher, args=args, kwargs=kwargs
        )

        def invoke(future: asyncio.Future):
            loop = publisher.manager.session.connection.manager.loop
            try:
                result = future.result()
                self.__future = asyncio.ensure_future(self.__invoke(), loop=loop)
            except Exception as e:
                print(e)
        publisher.manager.session.future.add_done_callback(invoke)

    async def __invoke(self):
        try:
            options = PublishOptions(
                acknowledge=self._publisher.acknowledge,
                exclude_me=self._publisher.exclude_me,
                exclude=self._publisher.exclude,
                exclude_authid=self._publisher.exclude_authid,
                exclude_authrole=self._publisher.exclude_authrole,
                eligible=self._publisher.eligible,
                eligible_authid=self._publisher.eligibile_authid,
                eligible_authrole=self._publisher.eligible_authrole,
                retain=self._publisher.retain
            )
            session = self._publisher.manager.session.application_session
            self._result = session.publish(
                topic=self._publisher.topic,
                *self._args,
                options=options,
                **self._kwargs
            )
            if self._result is not None and self._publisher.acknowledge:
                self._result = await self._result
        except Exception as e:
            self._exception = e

    def __call__(self, *new_args, **new_kwargs) -> AbstractPublication:
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
        return self._publisher(*args, **kwargs)


class Publisher(HasNames, AbstractPublisher):
    def __init__(self, manager: AbstractPublisherManager,
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
        self.__init_has_names__()
        super().__init__(
            manager=manager, topic=topic, acknowledge=acknowledge,
            exclude_me=exclude_me, exclude=exclude,
            exclude_authid=exclude_authid, exclude_authrole=exclude_authrole,
            eligible=eligible, eligible_authid=eligible_authid,
            eligible_authrole=eligible_authrole, retain=retain
        )

    def __call__(self, *args, **kwargs) -> AbstractPublication:
        name = self._generate_name()
        publication = Publication(publisher=self, args=args, kwargs=kwargs)
        publication_id = id(publication)
        self._items[publication_id] = publication
        self._names__items[name] = publication_id
        return publication


class PublisherManager(HasNames, HasSession, AbstractPublisherManager):

    def __init__(self, session: AbstractSession):
        self.__init_has_names__()
        self.__init_has_session__(session)

    @HasNames.with_name
    def __call__(self,
                 topic: str,
                 acknowledge: bool=None,
                 exclude_me: bool=None,
                 exclude: Union[int, List[int]]=None,
                 exclude_authid: Union[str, List[str]]=None,
                 exclude_authrole: Union[str, List[str]]=None,
                 eligible: Union[int, List[int]]=None,
                 eligible_authid: Union[str, List[str]]=None,
                 eligible_authrole: Union[str, List[str]]=None,
                 retain: bool=None, *,
                 name: str=None) -> AbstractPublisher:
        print(f'Generating publish to {topic} with name {name}')
        publisher = Publisher(
            manager=self, topic=topic, acknowledge=acknowledge,
            exclude_me=exclude_me, exclude=exclude,
            exclude_authid=exclude_authid, exclude_authrole=exclude_authrole,
            eligible=eligible, eligible_authid=eligible_authid,
            eligible_authrole=eligible_authrole, retain=retain
        )
        publisher_id = id(publisher)
        self._items[publisher_id] = publisher
        self._names__items[name] = publisher_id
        return publisher
