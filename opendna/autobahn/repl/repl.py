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

import txaio
from opendna.common.decorators import with_uvloop_if_possible
from ptpython.repl import embed, run_config, PythonRepl

from opendna.autobahn.repl.connections import ConnectionManager


@asyncio.coroutine
def _start_repl(loop):
    yield from embed(
        globals={},
        locals={
            'connections': ConnectionManager(loop),
        },
        title='AutoBahn-Python REPL',
        return_asyncio_coroutine=True, patch_stdout=True
        # TODO: Handle configure parameter
        # TODO: Handle history_filename parameter
    )


@with_uvloop_if_possible
def main():
    loop = asyncio.get_event_loop()
    txaio.use_asyncio()
    txaio.config.loop = loop
    loop.run_until_complete(_start_repl(loop))
    loop.stop()


if __name__ == '__main__':
    # TODO: Implement argument parser
    main()
