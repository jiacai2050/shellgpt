import argparse, sys
from os import environ, makedirs
from smartinput import sinput
from .api.ollama import Ollama
from .version import __version__
from .utils.conf import *
from .utils.common import *
from .tui.app import ShellGPTApp


class ShellGPT(object):
    def __init__(self, url, model, role, timeout):
        makedirs(CONF_PATH, exist_ok=True)
        self.llm = Ollama(url, model, role, timeout)

    def tui(self):
        app = ShellGPTApp(self.llm)
        app.run()

    def repl(self):
        print(r'''
__      __   _                    _         ___ _        _ _  ___ ___ _____
\ \    / /__| |__ ___ _ __  ___  | |_ ___  / __| |_  ___| | |/ __| _ \_   _|
 \ \/\/ / -_) / _/ _ \ '  \/ -_) |  _/ _ \ \__ \ ' \/ -_) | | (_ |  _/ | |
  \_/\_/\___|_\__\___/_|_|_\___|  \__\___/ |___/_||_\___|_|_|\___|_|   |_|
''')
        while True:
            prompt = sinput("> ")
            if prompt != "":
                try:
                    self.infer(prompt, False, True)
                except Exception as e:
                    print(f"Error when infer: ${e}")

    def infer(self, prompt):
        for r in self.llm.generate(prompt):
            print(r, end='')
        print()

        # r = sinput("Execute, Yank, Continue", hints=['e', 'y', 'c'])
        # print(r)


def main():
    prog = sys.argv[0]
    parser = argparse.ArgumentParser(
        prog=prog,
        description='Make Shell easy to use with power of LLM!')
    parser.add_argument('-V', '--version', action='version', version='%(prog)s ' + __version__)
    parser.add_argument('-s', '--shell', action='store_true', help='Infer shell command')
    parser.add_argument('-r', '--role', default='default', help='System role message')
    parser.add_argument('-l', '--repl', action='store_true', help='Start interactive REPL')
    parser.add_argument('--timeout', type=int, help='Timeout for each inference request', default=INFER_TIMEOUT)
    parser.add_argument('--ollama-url', default=OLLAMA_URL, help='Ollama URL')
    parser.add_argument('-m', '--ollama-model', default='llama3', help='Ollama model')
    parser.add_argument('-v', '--verbose', action='store_true', help='verbose mode')
    parser.add_argument('prompt', metavar='<prompt>', nargs='*')
    args = parser.parse_args()
    set_verbose(args.verbose)

    sin = read_stdin()
    prompt = ' '.join(args.prompt)
    if sin is not None:
        prompt = f'{sin}\n\n{prompt}'

    role = args.role
    if args.shell:
        role = 'shell'
    elif len(prompt) == 0:
        # tui default to shell role
        role = 'shell'

    sg = ShellGPT(args.ollama_url, args.ollama_model, role, args.timeout)
    if args.repl:
        sg.repl()
    elif len(prompt) == 0:
        sg.tui()
    else:
        sg.infer(prompt)


if __name__ == '__main__':
    main()
