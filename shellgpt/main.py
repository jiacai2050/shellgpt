import argparse
from os import environ, makedirs
from smartinput import sinput
from shellgpt.api.ollama import Ollama
from shellgpt.version import __version__
from shellgpt.utils.conf import *
from shellgpt.utils.common import set_verbose
from shellgpt.tui.app import ShellGPTApp


class ShellGPT(object):
    def __init__(self, url, model, timeout):
        makedirs(CONF_PATH, exist_ok=True)
        self.llm = Ollama(url, model, timeout)

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
            promt = sinput("> ")
            if promt != "":
                try:
                    self.infer(promt, False)
                except Exception as e:
                    print(f"Error when infer: ${e}")

    def infer(self, promt, only_cmd):
        for r in self.llm.generate(promt, only_cmd=only_cmd):
            print(r, end='')
        print()


def main():
    parser = argparse.ArgumentParser(
        prog='sg',
        description='Make Shell easy to use with power of LLM!')
    parser.add_argument('-V', '--version', action='version', version='%(prog)s ' + __version__)
    parser.add_argument('-l', '--repl', action='store_true', help='Start interactive REPL')
    parser.add_argument('--timeout', type=int, help='Timeout for each inference request', default=INFER_TIMEOUT)
    parser.add_argument('--ollama-url', default=OLLAMA_URL, help='Ollama URL')
    parser.add_argument('--ollama-model', default='llama3', help='Ollama model')
    parser.add_argument('-v', '--verbose', action='store_true', help='verbose mode')
    parser.add_argument('promt', metavar='<promt>', nargs='*')
    args = parser.parse_args()
    set_verbose(args.verbose)
    promt = ' '.join(args.promt)

    sg = ShellGPT(args.ollama_url, args.ollama_model, args.timeout)
    if args.repl:
        sg.repl()
    elif len(args.promt) == 0:
        sg.tui()
    else:
        sg.infer(promt, True)


if __name__ == '__main__':
    main()
