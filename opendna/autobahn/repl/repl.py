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
from functools import partial
from os import environ
import os.path

import txaio
from opendna.common.decorators import with_uvloop_if_possible
from pathlib import Path
from ptpython.repl import embed, run_config, PythonRepl

from opendna.autobahn.repl.mixins import ManagesNamesProxy
from opendna.autobahn.repl.utils import get_class


DEFAULT_HISTORY_FILE = str(Path.home() / 'autobahn_python_repl.history.txt')
DEFAULT_CONFIG_FILE = str(Path.home() / 'autobahn_python_repl.config.py')


def default_configure(repl: PythonRepl):
    """
    Default REPL configuration function

    :param repl:
    :return:
    """
    repl.show_signature = True
    repl.show_docstring = True
    repl.show_status_bar = True
    repl.show_sidebar_help = True
    repl.highlight_matching_parenthesis = True
    repl.wrap_lines = True
    repl.complete_while_typing = True
    repl.vi_mode = False
    repl.paste_mode = False
    repl.prompt_style = 'classic'  # 'classic' or 'ipython'
    repl.insert_blank_line_after_output = False
    repl.enable_history_search = False
    repl.enable_auto_suggest = False
    repl.enable_open_in_editor = True
    repl.enable_system_bindings = False
    repl.confirm_exit = True
    repl.enable_input_validation = True


@asyncio.coroutine
def start_repl(loop: asyncio.AbstractEventLoop):
    """
    Start the REPL and attach it to the provided event loop
    :param loop:
    :return:
    """
    config_file = environ.get('config_file', DEFAULT_CONFIG_FILE)
    if os.path.exists(config_file):
        configure = partial(run_config, config_file=config_file)
    else:
        configure = default_configure
    manager_class = get_class(environ['connection_manager'])
    manager = manager_class(loop)
    yield from embed(
        globals={},
        locals={
            'connect': manager,
            'connect_to': manager,
            'connections': ManagesNamesProxy(manager),
        },
        title='AutoBahn-Python REPL',
        return_asyncio_coroutine=True,
        patch_stdout=True,
        configure=configure,
        history_filename=environ.get('history_file', DEFAULT_HISTORY_FILE)
    )


@with_uvloop_if_possible
def main():
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
    parser.add_argument('--history-file', dest='history_file', default=DEFAULT_HISTORY_FILE)
    parser.add_argument('--config-file', dest='config_file', default=DEFAULT_CONFIG_FILE)
    args = parser.parse_args()
    environ.update({
        key: value
        for key, value in vars(args).items()
        if key in dest__class or key in {'history_file', 'config_file'}
    })
    loop = asyncio.get_event_loop()
    txaio.use_asyncio()
    txaio.config.loop = loop
    loop.run_until_complete(start_repl(loop))
    loop.stop()


if __name__ == '__main__':
    main()
