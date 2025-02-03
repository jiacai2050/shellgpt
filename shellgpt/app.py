import argparse
import sys
import readline
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
    is_verbose,
    load_contents_from_config,
    execute_cmd,
    copy_text,
    read_stdin,
    extract_code,
    set_verbose,
    AppMode,
)
from .history import History

__version__ = '0.5.5-dev'


def init_app():
    print(f'Create {CONF_PATH}...')
    makedirs(CONF_PATH, exist_ok=True)


def list_content():
    load_contents_from_config(True)
    for n in SYSTEM_CONTENT:
        print(n)


# List of commands for autocompletion
commands = ['exit', 'clear', 'editor', 'set', 'copy', 'explain', 'run', 'clear']


def completer(text, state):
    options = [cmd for cmd in commands if cmd.startswith(text)]
    if state < len(options):
        return options[state]
    else:
        return None


def repl_setup():
    readline.set_completer(completer)
    # Use Tab for completion
    if sys.platform == 'darwin':
        readline.parse_and_bind('bind ^I rl_complete')
    else:
        readline.parse_and_bind('tab: complete')

    # Enable case-insensitive completion
    readline.set_completer_delims(r' \t\n;')


class ShellGPT(object):
    def __init__(
        self,
        url,
        key,
        model,
        system_content,
        temperature,
        timeout,
        max_messages,
        history,
    ):
        self.is_shell = system_content == 'shell'
        self.last_answer = None
        self.history = history
        self.num_prompt = 0
        self.llm = LLM(
            url, key, model, system_content, temperature, timeout, max_messages
        )

    def tui(self, history, initial_prompt):
        try:
            from .tui.app import ShellGPTApp

            app = ShellGPTApp(self.llm, history, initial_prompt)
            app.run()
        except ImportError:
            print(
                'TUI dependencies are NOT installed. Please install them with: pip install shgpt[tui]'
            )
            sys.exit(1)

    def editor(self):
        print('// Entering editor mode (Ctrl+D to finish, Ctrl+C to cancel)')
        prompt = None
        while True:
            try:
                if prompt is None:
                    prompt = input('')
                else:
                    prompt += input('')
            except KeyboardInterrupt:  # Ctrl+C to cancel
                return None
            except EOFError:  # Ctrl+D to finish
                return prompt

    # return true when prompt is a set command
    def repl_action(self, prompt):
        if 'exit' == prompt:
            self.history.remove_last()
            raise EOFError
        elif prompt in ['c', 'copy']:
            copy_text(self.last_answer)
            return True
        elif prompt == 'clear':
            self.llm.messages.clear()
            copy_text(self.last_answer)
            return True
        elif prompt in ['ed', 'editor']:
            new_prompt = self.editor()
            if new_prompt is not None:
                self.infer(new_prompt)
            return True
        elif prompt in ['clear']:
            self.llm.messages = []
            return True

        if self.is_shell:
            if prompt in ['e', 'explain']:
                self.explain_cmd(self.last_answer)
                return True
            elif prompt in ['r', 'run']:
                print(execute_cmd(self.last_answer, ask=True))
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
            self.llm.system_content = sc
            return True

        return False

    def repl(self, initial_prompt):
        print(
            r"""
__      __   _                    _         ___ _        _ _  ___ ___ _____
\ \    / /__| |__ ___ _ __  ___  | |_ ___  / __| |_  ___| | |/ __| _ \_   _|
 \ \/\/ / -_) / _/ _ \ '  \/ -_) |  _/ _ \ \__ \ ' \/ -_) | | (_ |  _/ | |
  \_/\_/\___|_\__\___/_|_|_\___|  \__\___/ |___/_||_\___|_|_|\___|_|   |_|

Type "exit" or ctrl-d to exit; ctrl-c to stop response; "c" to copy last answer;
     "clear" to reset history messages; "ed" to enter editor mode.
When system content is shell , type "e" to explain, "r" to run last command.
""",
            end='',
        )

        repl_setup()
        try:
            self.repl_inner(initial_prompt)
        except EOFError:
            print(f'\n{self.num_prompt} questions asked this time, bye...')
            sys.exit(0)

    def repl_inner(self, initial_prompt):
        while True:
            try:
                self.infer(initial_prompt)
                prompt = input(f'{self.llm.system_content}@{self.llm.model}> ')
                if IS_TTY and self.repl_action(prompt):
                    self.history.remove_last()
                    continue

                self.infer(prompt)
            except KeyboardInterrupt:
                print()

    def infer(self, prompt):
        if prompt == '':
            return

        self.num_prompt += 1
        self.last_answer = ''
        try:
            for r in self.llm.chat(prompt):
                self.last_answer += r
                if self.is_shell is False:
                    print(r, end='', flush=True)

            if self.is_shell:
                shell = extract_code(self.last_answer)
                if shell is not None:
                    self.last_answer = shell
                print(self.last_answer)
            else:
                print()
        except Exception as e:
            print(f'Error when infer: ${e}')
            if is_verbose():
                raise e

    def explain_cmd(self, cmd):
        self.last_answer = ''
        for r in self.llm.chat(
            f'Explain this command: {cmd}', add_system_message=False
        ):
            self.last_answer += r
            print(r, end='', flush=True)
        print()


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
        '-S',
        '--shell',
        action='store_true',
        help='system content set to `shell`',
    )
    parser.add_argument(
        '-s',
        '--system',
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

    system_content = args.system
    if args.shell or app_mode == AppMode.TUI:
        system_content = 'shell'

    load_contents_from_config(False)

    history = History()
    sg = ShellGPT(
        args.api_url,
        args.api_key,
        args.model,
        system_content,
        args.temperature,
        args.timeout,
        args.max_messages,
        history,
    )
    if prompt != '':
        history.add(prompt)

    if app_mode == AppMode.Direct:
        sg.infer(prompt)
    elif app_mode == AppMode.TUI:
        sg.tui(history, prompt)
    else:
        sg.repl(prompt)
