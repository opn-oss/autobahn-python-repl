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

__author__ = 'Adam Jorgensen <adam.jorgensen.za@gmail.com>'


class AbstractCall(object):
    def __call__(self, *args, **kwargs):
        raise NotImplementedError

    @property
    def application_session(self):
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


class AbstractCallManager(object):
    def __call__(self, *args, **kwargs):
        raise NotImplementedError

    def __getitem__(self, item):
        raise NotImplementedError

    def __getattr__(self, item):
        raise NotImplementedError


class AbstractRegister(object):
    pass


class AbstractPublish(object):
    pass


class AbstractSubscribe(object):
    pass


class AbstractSession(object):
    pass


class AbstractSessionManager(object):
    pass
