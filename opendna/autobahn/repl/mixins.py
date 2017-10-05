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
from asyncio import AbstractEventLoop

from decorator import decorator

from opendna.autobahn.repl.abc import AbstractSession
from opendna.autobahn.repl.utils import generate_name


class HasLoop(object):
    """
    Mix-in providing read-only access to an AbstractEventLoop instance
    """
    def __init_has_loop__(self, loop: AbstractEventLoop):
        assert isinstance(loop, AbstractEventLoop)
        self._loop = loop

    @property
    def loop(self):
        return self._loop


class HasSession(object):
    """
    Mix-in providing read-only access to an AbstractSession instance
    """
    def __init_has_session__(self, session: AbstractSession):
        assert isinstance(session, AbstractSession)
        self._session: AbstractSession = session

    @property
    def session(self) -> AbstractSession:
        return self._session


class HasNamesMeta(type):
    """
    Meta-class used by ManagesNames to provide the with_name decorator
    """
    def __with_name(cls, f, self: 'ManagesNames', *args, **kwargs):
        kwargs['name'] = self._generate_name(kwargs.get('name'))
        return f(self, *args, **kwargs)

    def with_name(cls, f):
        return decorator(cls.__with_name, f)


class ManagesNames(object, metaclass=HasNamesMeta):
    """
    Mix-in providing item and attribute access to specific data stored
    the class instance. Also provides with ManagesNames.with_name decorator
    """
    def __init_manages_names__(self):
        self._items = {}
        self._names__items = {}
        self._items__names = {}

    def _generate_name(self, name=None):
        name = generate_name(name)
        while name in self:
            name = generate_name(length=len(name) + 1)
        return name

    def name_for(self, item):
        return self._items__names[item]

    def __getitem__(self, item):
        item = self._names__items.get(item, item)
        return self._items[item]

    def __getattr__(self, item):
        return self[item]

    def __contains__(self, item):
        return item in self._items or item in self._names__items


class HasName(object):
    """
    Mix-in providing access to the name for a class instance managed by the
    ManagesNames mix-in
    """
    def __init_has_name__(self, name_provider: ManagesNames):
        self._name_provider = name_provider

    @property
    def name(self):
        return self._name_provider.name_for(self)
