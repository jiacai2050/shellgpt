from shellgpt.api.ollama import Ollama
import argparse
from os import environ

class ShellGPT(object):
    def __init__(self, llm):
        self.llm = llm

    def repl(self):
        print(r'''
__      __   _                    _         ___ _        _ _  ___ ___ _____
\ \    / /__| |__ ___ _ __  ___  | |_ ___  / __| |_  ___| | |/ __| _ \_   _|
 \ \/\/ / -_) / _/ _ \ '  \/ -_) |  _/ _ \ \__ \ ' \/ -_) | | (_ |  _/ | |
  \_/\_/\___|_\__\___/_|_|_\___|  \__\___/ |___/_||_\___|_|_|\___|_|   |_|
''')
        while True:
            promt = input("> ")
            if promt != "":
                try:
                    resp = self.llm.generate(promt)
                    print(resp)
                except Exception as e:
                    print(f"Error get resp: ${e}")

    def infer(self, promt):
        resp = self.llm.generate(promt)
        print(resp)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog='shellgpt',
        description='Make Shell easy to use with power of LLM!')
    parser.add_argument('-v', '--version', action='version', version='%(prog)s 0.1')
    parser.add_argument('-r', '--repl', action='store_true', help='Start ShellGPT REPL')
    parser.add_argument('--timeout', type=int, help='Timeout for each inference request', default=10)
    parser.add_argument('--ollama-url', default=environ.get('SG_OLLAMA_URL', 'http://127.0.0.1:11434'), help='Ollama URL')
    parser.add_argument('--verbose', action='store_true', help='verbose mode')
    parser.add_argument('promt', metavar='<promt>', nargs='*')
    args = parser.parse_args()
    promt = ' '.join(args.promt)

    sg = ShellGPT(Ollama(args.ollama_url, timeout=args.timeout))
    if len(args.promt) == 0 or args.repl:
        sg.repl()
    else:
        print(sg.infer(promt))
