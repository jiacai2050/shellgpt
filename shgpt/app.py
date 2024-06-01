import argparse
import sys
from os import makedirs
from .api.ollama import Ollama
from .version import __version__
from .utils.conf import *
from .utils.common import *
from .tui.app import ShellGPTApp


def init_app():
    print(f"Create {CONF_PATH}...")
    makedirs(CONF_PATH, exist_ok=True)


def read_action(cmd):
    if IS_TTY:
        action = input("(E)xecute, (Y)ank or Continue(default): ")
        action = action.upper()
        if action == "E":
            print(execute_cmd(cmd))
        elif action == "Y":
            copy_text(cmd)


class ShellGPT(object):
    def __init__(self, url, model, role, timeout):
        self.role = role
        self.llm = Ollama(url, model, role, timeout)

    def tui(self, initial_prompt):
        app = ShellGPTApp(self.llm, initial_prompt)
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
            prompt = input("> ")
            if "exit" == prompt:
                sys.exit(0)

            self.infer(prompt)

    def infer(self, prompt):
        if prompt == "":
            return

        buf = ""
        try:
            for r in self.llm.generate(prompt):
                buf += r
                print(r, end="")

            print()
            if self.role == "shell":
                read_action(buf)
        except Exception as e:
            print(f"Error when infer: ${e}")


def main():
    prog = sys.argv[0]
    parser = argparse.ArgumentParser(
        prog=prog,
        description="Chat with LLM in your terminal, be it shell generator, story teller, linux-terminal, etc.",
    )
    parser.add_argument(
        "-V", "--version", action="version", version="%(prog)s " + __version__
    )
    parser.add_argument(
        "-s",
        "--shell",
        action="store_true",
        help="System role set to `shell`",
    )
    parser.add_argument(
        "-c",
        "--code",
        action="store_true",
        help="System role set to `code`",
    )
    parser.add_argument("-r", "--role", default="default", help="System role to use")
    parser.add_argument(
        "-l", "--repl", action="store_true", help="Start interactive REPL"
    )
    parser.add_argument("-t", "--tui", action="store_true", help="Start TUI mode")
    parser.add_argument("--init", action="store_true", help="Init config")
    parser.add_argument(
        "--timeout",
        type=int,
        help="Timeout for each inference request",
        default=INFER_TIMEOUT,
    )
    parser.add_argument("--ollama-url", default=OLLAMA_URL, help="Ollama URL")
    parser.add_argument("-m", "--ollama-model", default="llama3", help="Ollama model")
    parser.add_argument("-v", "--verbose", action="store_true", help="verbose mode")
    parser.add_argument("prompt", metavar="<prompt>", nargs="*")
    args = parser.parse_args()
    set_verbose(args.verbose)

    if args.init:
        init_app()
        sys.exit(0)

    sin = read_stdin()
    prompt = " ".join(args.prompt)
    if sin is not None:
        prompt = f"{sin}\n\n{prompt}"

    if args.repl:
        app_mode = AppMode.REPL
    elif args.tui:
        app_mode = AppMode.TUI
    else:
        app_mode = AppMode.TUI if len(prompt) == 0 else AppMode.Direct

    role = args.role
    # tui default to shell role
    if args.shell or app_mode == AppMode.TUI:
        role = "shell"
    elif args.code:
        role = "code"

    if role not in ROLE_CONTENT:
        try:
            load_roles_from_config()
        except Exception as e:
            debug_print(f"Error when load roles: ${e}")

    if role not in ROLE_CONTENT:
        print(f"Error: role '{role}' not found in config!")
        sys.exit(1)

    sg = ShellGPT(args.ollama_url, args.ollama_model, role, args.timeout)
    if app_mode == AppMode.Direct:
        sg.infer(prompt)
    elif app_mode == AppMode.TUI:
        sg.tui(prompt)
    else:
        sg.repl(prompt)
