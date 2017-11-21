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
from argparse import ArgumentParser
from os import environ

import txaio
from opendna.common.decorators import with_uvloop_if_possible
from ptpython.repl import embed, run_config, PythonRepl

from opendna.autobahn.repl.utils import get_class


@asyncio.coroutine
def _start_repl(loop):
    manager_class = get_class(environ['connection_manager'])
    manager = manager_class(loop)
    yield from embed(
        globals={},
        locals={
            'connect': manager,
            'connect_to': manager,
            'connections': manager,
        },
        title='AutoBahn-Python REPL',
        return_asyncio_coroutine=True,
        patch_stdout=True
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
    prefix = 'opendna.autobahn.repl'
    dest__class = {
        'connection_manager': f'{prefix}.connections.ConnectionManager',
        'connection': f'{prefix}.connections.Connection',
        'session': f'{prefix}.sessions.Session',
        'call_manager': f'{prefix}.rpc.CallManager',
        'call': f'{prefix}.rpc.Call',
        'invocation': f'{prefix}.rpc.Invocation',
        'registration_manager': f'{prefix}.rpc.RegistrationManager',
        'registration': f'{prefix}.rpc.Registration',
        'publisher_manager': f'{prefix}.pubsub.PublisherManager',
        'publisher': f'{prefix}.pubsub.Publisher',
        'publication': f'{prefix}.pubsub.Publication',
        'subscription_manager': f'{prefix}.pubsub.SubscriptionManager',
        'subscription': f'{prefix}.pubsub.Subscription',
        'application_runner': 'autobahn.asyncio.wamp.ApplicationRunner',
        'application_session': f'{prefix}.wamp.REPLApplicationSession'
    }
    parser = ArgumentParser(description='Python REPL for interacting with Crossbar')
    for dest, class_ in dest__class.items():
        parser.add_argument(
            f'--{dest.replace("_", "-")}', default=class_, dest=dest
        )
    # TODO: Add parameter for history file
    # TODO: Add parameter for config module
    args = parser.parse_args()
    environ.update({
        key: value
        for key, value in vars(args).items()
        if key in dest__class
    })
    main()
