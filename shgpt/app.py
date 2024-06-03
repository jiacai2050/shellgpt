import argparse
import sys
from os import makedirs
from .api.ollama import Ollama
from .version import __version__
from .utils.conf import (
    load_roles_from_config,
    INFER_TIMEOUT,
    OLLAMA_URL,
    OLLAMA_TEMPERATURE,
    ROLE_CONTENT,
    CONF_PATH,
    IS_TTY,
)
from .utils.common import (
    execute_cmd,
    copy_text,
    read_stdin,
    extract_code,
    set_verbose,
    debug_print,
    AppMode,
)
from .tui.app import ShellGPTApp
from .history import History


def init_app():
    print(f'Create {CONF_PATH}...')
    makedirs(CONF_PATH, exist_ok=True)


class ShellGPT(object):
    def __init__(self, url, model, role, temperature, timeout):
        self.is_shell = role == 'shell'
        self.llm = Ollama(url, model, role, temperature, timeout)

    def tui(self, history, initial_prompt):
        app = ShellGPTApp(self.llm, history, initial_prompt)
        app.run()

    def repl(self, initial_prompt):
        print(r"""
__      __   _                    _         ___ _        _ _  ___ ___ _____
\ \    / /__| |__ ___ _ __  ___  | |_ ___  / __| |_  ___| | |/ __| _ \_   _|
 \ \/\/ / -_) / _/ _ \ '  \/ -_) |  _/ _ \ \__ \ ' \/ -_) | | (_ |  _/ | |
  \_/\_/\___|_\__\___/_|_|_\___|  \__\___/ |___/_||_\___|_|_|\___|_|   |_|
""")
        self.infer(initial_prompt)
        while True:
            prompt = input('> ')
            if 'exit' == prompt:
                sys.exit(0)

            self.infer(prompt)

    def infer(self, prompt):
        if prompt == '':
            return

        buf = ''
        try:
            for r in self.llm.chat(prompt):
                buf += r
                if self.is_shell is False:
                    print(r, end='')

            if self.is_shell:
                shell = extract_code(buf)
                if shell is not None:
                    buf = shell
                print(buf)
            else:
                print()

            if self.is_shell:
                self.repl_action(buf)
        except Exception as e:
            print(f'Error when infer: ${e}')

    def repl_action(self, cmd):
        if IS_TTY:
            action = input('(R)un, (Y)ank, (E)xplain: ')
            action = action.upper()
            if action == 'E':
                for r in self.llm.generate(f'Explain this command: {cmd}'):
                    print(r, end='')
                print()
            elif action == 'R':
                print(execute_cmd(cmd))
            elif action == 'Y':
                copy_text(cmd)


def main():
    parser = argparse.ArgumentParser(
        prog='shgpt',
        description='Chat with LLM in your terminal, be it shell generator, story teller, linux-terminal, etc.',
    )

    parser.add_argument(
        '-V', '--version', action='version', version='%(prog)s ' + __version__
    )
    parser.add_argument(
        '-s',
        '--shell',
        action='store_true',
        help='System role set to `shell`',
    )
    parser.add_argument(
        '-c',
        '--code',
        action='store_true',
        help='System role set to `code`',
    )
    parser.add_argument(
        '-r',
        '--role',
        default='default',
        help='System role to use, (default: %(default)s)',
    )
    parser.add_argument(
        '-l', '--repl', action='store_true', help='Start interactive REPL'
    )
    parser.add_argument('-t', '--tui', action='store_true', help='Start TUI mode')
    parser.add_argument('--init', action='store_true', help='Init config')
    parser.add_argument(
        '--timeout',
        type=int,
        help='Timeout in seconds for each inference request (default: %(default)d)',
        default=INFER_TIMEOUT,
    )
    parser.add_argument(
        '--ollama-url', default=OLLAMA_URL, help='Ollama URL (default: %(default)s)'
    )
    parser.add_argument(
        '-m',
        '--ollama-model',
        default='llama3',
        help='Ollama model (default: %(default)s)',
    )
    parser.add_argument(
        '--temperature',
        default=OLLAMA_TEMPERATURE,
        type=float,
        help='The temperature of the model. Increasing the temperature will make the model answer more creatively. (default: %(default).2f)',
    )
    parser.add_argument('-v', '--verbose', action='store_true', help='verbose mode')
    parser.add_argument('prompt', metavar='<prompt>', nargs='*')
    args = parser.parse_args()
    set_verbose(args.verbose)

    if args.init:
        init_app()
        sys.exit(0)

    sin = read_stdin()
    prompt = ' '.join(args.prompt)
    if sin is not None:
        prompt = f'{sin}\n\n{prompt}'

    if args.repl:
        app_mode = AppMode.REPL
    elif args.tui:
        app_mode = AppMode.TUI
    else:
        app_mode = AppMode.TUI if len(prompt) == 0 else AppMode.Direct

    role = args.role
    # tui default to shell role
    if args.shell or app_mode == AppMode.TUI:
        role = 'shell'
    elif args.code:
        role = 'code'

    if role not in ROLE_CONTENT:
        try:
            load_roles_from_config()
        except Exception as e:
            debug_print(f'Error when load roles: ${e}')

    if role not in ROLE_CONTENT:
        print(f"Error: role '{role}' not found in config!")
        sys.exit(1)

    sg = ShellGPT(
        args.ollama_url, args.ollama_model, role, args.temperature, args.timeout
    )
    history = History()
    if prompt != '':
        history.add(prompt)

    if app_mode == AppMode.Direct:
        sg.infer(prompt)
    elif app_mode == AppMode.TUI:
        sg.tui(history, prompt)
    else:
        sg.repl(prompt)
