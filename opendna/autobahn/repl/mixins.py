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
from decorator import decorator

from opendna.autobahn.repl.abc import AbstractSession
from opendna.autobahn.repl.utils import generate_name


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
    Meta-class used by HasNames to provide the with_name decorator
    """
    def __with_name(cls, f, self: 'HasNames', *args, **kwargs):
        kwargs['name'] = self._generate_name(kwargs.get('name'))
        return f(self, *args, **kwargs)

    def with_name(cls, f):
        return decorator(cls.__with_name, f)


class HasNames(object, metaclass=HasNamesMeta):
    """
    Mix-in providing item and attribute access to specific data stored
    the class instance. Also provides with HasNames.with_name decorator
    """
    def __init_has_names__(self):
        self._items = {}
        self._names__items = {}

    def _generate_name(self, name=None):
        name = generate_name(name)
        while name in self:
            name = generate_name(length=len(name) + 1)
        return name

    def __getitem__(self, item):
        item = self._names__items.get(item, item)
        return self._items[item]

    def __getattr__(self, item):
        return self[item]

    def __contains__(self, item):
        return item in self._items or item in self._names__items



