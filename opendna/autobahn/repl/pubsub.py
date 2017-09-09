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
from typing import Union, List

from opendna.autobahn.repl.abc import (
    AbstractPublication,
    AbstractPublisher,
    AbstractPublisherManager,
    AbstractSession
)
from opendna.autobahn.repl.mixins import HasNames, HasSession
from opendna.autobahn.repl.utils import generate_name

__author__ = 'Adam Jorgensen <adam.jorgensen.za@gmail.com>'


class Publication(AbstractPublication):
    pass


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
        assert isinstance(manager, AbstractPublisherManager)
        self.__manager = manager
        self.__topic = topic
        self.__acknowledge = acknowledge
        self.__exclude_me = exclude_me
        self.__exclude = exclude
        self.__exclude_authid = exclude_authid
        self.__exclude_authrole = exclude_authrole
        self.__eligible = eligible
        self.__eligible_authid = eligible_authid
        self.__eligible_authrole = eligible_authrole
        self.__retain = retain

    def __call__(self, *args, **kwargs) -> AbstractPublication:
        name = generate_name()
        while name in self:
            name = generate_name(length=len(name) + 1)
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
