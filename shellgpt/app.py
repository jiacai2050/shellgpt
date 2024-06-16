import argparse
import sys
from os import makedirs
from .api.ollama import Ollama
from .utils.conf import (
    API_KEY,
    MAX_CHAT_MESSAGES,
    MODEL,
    load_contents_from_config,
    INFER_TIMEOUT,
    API_URL,
    TEMPERATURE,
    SYSTEM_CONTENT,
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

__version__ = '0.5.0'


def init_app():
    print(f'Create {CONF_PATH}...')
    makedirs(CONF_PATH, exist_ok=True)


class ShellGPT(object):
    def __init__(
        self, url, key, model, system_content, temperature, timeout, max_messages
    ):
        self.is_shell = system_content == 'shell'
        self.llm = Ollama(
            url, key, model, system_content, temperature, timeout, max_messages
        )

    def tui(self, history, initial_prompt):
        app = ShellGPTApp(self.llm, history, initial_prompt)
        app.run()

    # return true when prompt is a set command
    def repl_action(self, prompt):
        if 'exit' == prompt:
            sys.exit(0)
        if prompt.startswith('set') is False:
            return False

        args = prompt.split(' ')
        if len(args) != 3:
            return False

        sub_cmd = args[1]
        if sub_cmd == 'model':
            self.llm.model = args[2]
            return True
        elif sub_cmd == 'system':
            sc = args[2]
            if load_system_content_when_necessary(sc):
                self.llm.system_content = sc
            else:
                print(f'No such system content "{sc}"')

            return True

        return False

    def repl(self, initial_prompt):
        print(r"""
__      __   _                    _         ___ _        _ _  ___ ___ _____
\ \    / /__| |__ ___ _ __  ___  | |_ ___  / __| |_  ___| | |/ __| _ \_   _|
 \ \/\/ / -_) / _/ _ \ '  \/ -_) |  _/ _ \ \__ \ ' \/ -_) | | (_ |  _/ | |
  \_/\_/\___|_\__\___/_|_|_\___|  \__\___/ |___/_||_\___|_|_|\___|_|   |_|
""")
        self.infer(initial_prompt)
        while True:
            prompt = input(f'{self.llm.system_content}@{self.llm.model}> ')
            if self.repl_action(prompt):
                continue

            self.infer(prompt)

    def infer(self, prompt):
        if prompt == '':
            return

        buf = ''
        try:
            for r in self.llm.chat(prompt):
                buf += r
                if self.is_shell is False:
                    print(r, end='', flush=True)

            if self.is_shell:
                shell = extract_code(buf)
                if shell is not None:
                    buf = shell
                print(buf)
            else:
                print()

            if self.is_shell:
                self.shell_action(buf)
        except Exception as e:
            print(f'Error when infer: ${e}')

    def shell_action(self, cmd):
        if IS_TTY:
            action = input('(R)un, (Y)ank, (E)xplain> ')
            action = action.upper()
            if action == 'E':
                for r in self.llm.chat(
                    f'Explain this command: {cmd}', add_system_message=False
                ):
                    print(r, end='', flush=True)
                print()
            elif action == 'R':
                print(execute_cmd(cmd))
            elif action == 'Y':
                copy_text(cmd)
            else:
                self.infer(action)


def load_system_content_when_necessary(sc):
    if sc in SYSTEM_CONTENT:
        return True

    try:
        load_contents_from_config()
    except Exception as e:
        debug_print(f'Error when load contents: ${e}')

    return sc in SYSTEM_CONTENT


def main():
    parser = argparse.ArgumentParser(
        prog='sg',
        description='Chat with LLM in your terminal, be it shell generator, story teller, linux-terminal, etc.',
    )

    parser.add_argument(
        '-V', '--version', action='version', version='%(prog)s ' + __version__
    )
    parser.add_argument(
        '-s',
        '--shell',
        action='store_true',
        help='System content set to `shell`',
    )
    parser.add_argument(
        '-c',
        '--system-content',
        default='default',
        help='System content to use, (default: %(default)s)',
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
        '--api-url', default=API_URL, help='API base URL (default: %(default)s)'
    )
    parser.add_argument(
        '--api-key', default=API_KEY, help='API Key (default: %(default)s)'
    )
    parser.add_argument(
        '-m',
        '--model',
        default=MODEL,
        help='Ollama model (default: %(default)s)',
    )
    parser.add_argument(
        '-M',
        '--max-messages',
        type=int,
        default=MAX_CHAT_MESSAGES,
        help='Max history messages (default: %(default)s)',
    )
    parser.add_argument(
        '--temperature',
        default=TEMPERATURE,
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
        app_mode = AppMode.REPL if len(prompt) == 0 else AppMode.Direct

    system_content = args.system_content
    if args.shell or app_mode == AppMode.TUI:
        system_content = 'shell'

    if load_system_content_when_necessary(system_content) is False:
        print(f"Error: system_content '{system_content}' not found in config!")
        sys.exit(1)

    sg = ShellGPT(
        args.api_url,
        args.api_key,
        args.model,
        system_content,
        args.temperature,
        args.timeout,
        args.max_messages,
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
