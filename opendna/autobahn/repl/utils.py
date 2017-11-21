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
from random import choice, choices
from importlib import import_module
import string

__author__ = 'Adam Jorgensen <adam.jorgensen.za@gmail.com>'


def generate_name(name: str=None, length: int=8):
    """
    Generate a name if the input name is None. The generated name will start
    with an ASCII letter and be followed by length-1 ASCII letters and/or numbers

    :param name:
    :param length:
    :return:
    """
    if name is None:
        name = (
            choice(string.ascii_letters)
            + ''.join(choices(string.ascii_letters + string.digits, k=length-1))
        )
    return name


Keep = type('Keep', (object,), {})()


def get_class(fully_qualified_classpath: str, package: str=None) -> type:
    """
    Given a classpath, returns the class referenced

    :param fully_qualified_classpath:
    :param package:
    :return:
    """
    path = fully_qualified_classpath.split('.')
    class_name = path.pop()
    module_ = import_module('.'.join(path), package)
    return getattr(module_, class_name)
