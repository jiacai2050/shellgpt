from enum import Enum
from typing import Optional
from datetime import datetime
import re
import platform
import os
import subprocess
import sys
import pyperclip

IS_VERBOSE = False
OS_NAME = platform.system()
IS_TTY = sys.stdin.isatty()


def get_shell_type():
    if OS_NAME in ("Windows", "nt"):
        is_powershell = len(os.getenv("PSModulePath", "").split(os.pathsep)) >= 3
        return "powershell.exe" if is_powershell else "cmd.exe"
    return os.path.basename(os.getenv("SHELL", "/bin/sh"))


SHELL = get_shell_type()


def set_verbose(v):
    global IS_VERBOSE
    IS_VERBOSE = v


def debug_print(msg):
    if IS_VERBOSE:
        print(msg)


def get_executable_script(text: str) -> Optional[str]:
    script_blocks = re.findall("```(.*?)\n(.*?)```", text, re.DOTALL)
    if len(script_blocks) == 0:
        return None
    else:
        return script_blocks[0][1].strip()


def now_ms():
    return int(datetime.now().timestamp() * 1000)


def read_stdin():
    if IS_TTY:
        return None
    else:
        buf = ""
        for line in sys.stdin:
            buf += line

        return buf


def copy_text(text):
    pyperclip.copy(text)


def execute_cmd(cmd):
    return subprocess.getoutput(cmd)


class AppMode(Enum):
    Direct = (1,)
    TUI = (2,)
    REPL = (3,)
