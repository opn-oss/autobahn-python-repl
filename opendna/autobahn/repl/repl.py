import asyncio

import txaio
from opendna.common.decorators import with_uvloop_if_possible
from ptpython.repl import embed, run_config, PythonRepl

from opendna.autobahn.repl.sessions import SessionManager, Session


@asyncio.coroutine
def _start_repl(loop):
    yield from embed(
        globals={},
        locals={
            # TODO: SessionManager class and Session class should be customisable using command-line arguments or environment variables
            'sessions': SessionManager(loop, Session),
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
