import argparse
import sys
from os import makedirs
from .api.llm import LLM
from .utils.conf import (
    API_KEY,
    MAX_CHAT_MESSAGES,
    MODEL,
    INFER_TIMEOUT,
    API_URL,
    TEMPERATURE,
    SYSTEM_CONTENT,
    CONF_PATH,
    IS_TTY,
)
from .utils.common import (
    load_contents_from_config,
    execute_cmd,
    copy_text,
    read_stdin,
    extract_code,
    set_verbose,
    AppMode,
)
from .tui.app import ShellGPTApp
from .history import History

__version__ = '0.5.0'


def init_app():
    print(f'Create {CONF_PATH}...')
    makedirs(CONF_PATH, exist_ok=True)


def list_content():
    load_contents_from_config(True)
    for n in SYSTEM_CONTENT:
        print(n)


class ShellGPT(object):
    def __init__(
        self, url, key, model, system_content, temperature, timeout, max_messages
    ):
        self.is_shell = system_content == 'shell'
        self.last_answer = None
        self.llm = LLM(
            url, key, model, system_content, temperature, timeout, max_messages
        )

    def tui(self, history, initial_prompt):
        app = ShellGPTApp(self.llm, history, initial_prompt)
        app.run()

    # return true when prompt is a set command
    def repl_action(self, prompt):
        if 'exit' == prompt:
            sys.exit(0)

        if prompt.upper() == 'C':
            copy_text(self.last_answer)
            return True

        # Following parse set command
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
            self.is_shell = sc == 'shell'
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

Type "exit" to exit; "c" to copy last answer
""")
        self.infer(initial_prompt)
        while True:
            prompt = input(f'{self.llm.system_content}@{self.llm.model}> ')
            if IS_TTY and self.repl_action(prompt):
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

            self.last_answer = buf
            if self.is_shell:
                self.shell_action(buf)
        except Exception as e:
            print(f'Error when infer: ${e}')

    def shell_action(self, cmd):
        if IS_TTY:
            action = input('(R)un, (C)opy, (E)xplain> ')
            action = action.upper()
            buf = ''
            if action == 'E':
                for r in self.llm.chat(
                    f'Explain this command: {cmd}', add_system_message=False
                ):
                    buf += r
                    print(r, end='', flush=True)
                print()
                self.last_answer = buf
            elif action == 'R':
                print(execute_cmd(cmd))
            elif action == 'C':
                copy_text(cmd)
            else:
                self.infer(action)


def load_system_content_when_necessary(sc):
    if sc in SYSTEM_CONTENT:
        return True

    load_contents_from_config()
    return sc in SYSTEM_CONTENT


def main():
    parser = argparse.ArgumentParser(
        prog='sg',
        description='Chat with LLM in your terminal, be it shell generator, story teller, linux-terminal, etc.',
    )

    parser.add_argument(
        '-r', '--repl', action='store_true', help='enter interactive REPL'
    )
    parser.add_argument('-t', '--tui', action='store_true', help='enter TUI mode')
    parser.add_argument(
        '-s',
        '--shell',
        action='store_true',
        help='system content set to `shell`',
    )
    parser.add_argument(
        '-c',
        '--content',
        default='default',
        help='content for system role (default: %(default)s)',
    )
    parser.add_argument(
        '--timeout',
        type=int,
        help='timeout in seconds for each inference (default: %(default)d)',
        default=INFER_TIMEOUT,
    )
    parser.add_argument(
        '--api-url', default=API_URL, help='base API URL (default: %(default)s)'
    )
    parser.add_argument(
        '--api-key', default=API_KEY, help='API Key (default: %(default)s)'
    )
    parser.add_argument(
        '-m',
        '--model',
        default=MODEL,
        help='model (default: %(default)s)',
    )
    parser.add_argument(
        '-M',
        '--max-messages',
        type=int,
        default=MAX_CHAT_MESSAGES,
        help='max history messages (default: %(default)s)',
    )
    parser.add_argument(
        '--temperature',
        default=TEMPERATURE,
        type=float,
        help='increasing the temperature will make the model answer more creatively. (default: %(default).2f)',
    )
    parser.add_argument(
        '--init', action='store_true', help='create required directories'
    )
    parser.add_argument('--list', action='store_true', help='list known system content')
    parser.add_argument('-v', '--verbose', action='store_true', help='verbose mode')
    parser.add_argument(
        '-V', '--version', action='version', version='%(prog)s ' + __version__
    )
    parser.add_argument('prompt', metavar='<prompt>', nargs='*')
    args = parser.parse_args()
    set_verbose(args.verbose)

    if args.init:
        init_app()
        sys.exit(0)
    elif args.list:
        list_content()
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

    system_content = args.content
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
