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
    AbstractSession,
    AbstractSubscription,
    AbstractSubscribe,
    AbstractSubscribeManager
)
from opendna.autobahn.repl.mixins import ManagesNames, HasSession, HasName
from opendna.autobahn.repl.utils import Keep

__author__ = 'Adam Jorgensen <adam.jorgensen.za@gmail.com>'


class Publication(AbstractPublication):
    def __init__(self, publisher: Uniom[MaagesNames, AbstractPublisher],
                 args: Iterable, kwargs: Dict[str, Any]):
        super(Publication, self).__init__(
            publisher=publisher, args=args, kwargs=kwargs
        )
        self.__init_has_name__(publisher)

        def invoke(future: asyncio.Future):
            loop = publisher.manager.session.connection.manager.loop
            try:
                result = future.result()
                self._future = asyncio.ensure_future(self._invoke(), loop=loop)
            except Exception as e:
                print(e)
        publisher.manager.session.future.add_done_callback(invoke)

    async def _invoke(self):
        topic = self._publisher.topic
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
            print(f'Publication to {topic} with name {self.name} starting')
            self._result = session.publish(
                topic=topic,
                *self._args,
                options=options,
                **self._kwargs
            )
            if self._result is not None and self._publisher.acknowledge:
                self._result = await self._result
            print(f'Publication to {topic} with name {self.name} succeeded')
        except Exception as e:
            print(f'Publication to {topic} with name {self.name} failed')
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


class Publisher(HasName, ManagesNames, AbstractPublisher):
    def __init__(self, manager: Union[ManagesNames, AbstractPublisherManager],
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
        super().__init__(
            manager=manager, topic=topic, acknowledge=acknowledge,
            exclude_me=exclude_me, exclude=exclude,
            exclude_authid=exclude_authid, exclude_authrole=exclude_authrole,
            eligible=eligible, eligible_authid=eligible_authid,
            eligible_authrole=eligible_authrole, retain=retain
        )
        self.__init_has_name__(manager)
        self.__init_manages_names__()

    def name_for(self, item):
        # TODO: Allow custom Publication class
        assert isinstance(item, Publication)
        return super().name_for(id(item))

    def __call__(self, *args, **kwargs) -> AbstractPublication:
        name = self._generate_name()
        # TODO: Allow custom Publication class
        publication = Publication(publisher=self, args=args, kwargs=kwargs)
        publication_id = id(publication)
        self._items[publication_id] = publication
        self._items__names[publication_id] = name
        self._names__items[name] = publication_id
        return publication


class PublisherManager(ManagesNames, HasSession, AbstractPublisherManager):

    def __init__(self, session: AbstractSession):
        self.__init_manages_names__()
        self.__init_has_session__(session)

    def name_for(self, item):
        # TODO: Allow custom Publisher. class
        assert isinstance(item, Publisher)
        return super().name_for(id(item))

    @ManagesNames.with_name
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
        self._items__names[publisher_id] = name
        self._names__items[name] = publisher_id
        return publisher


class Subscription(AbstractSubscription):
    pass


class Subscribe(AbstractSubscribe):
    pass


class SubscribeManager(HasSession, ManagesNames, AbstractSubscribeManager):
    def __init__(self, session: AbstractSession):
        self.__init_has_session__(session)
        self.__init_manages_names__()
