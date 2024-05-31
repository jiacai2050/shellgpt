from enum import Enum
from typing import Optional
from datetime import datetime
import re, platform, os, fileinput, sys

IS_VERBOSE = False
TEST_PROMPT = "tell me how to get current disk usage by shell command"
OS_NAME = platform.system()

def get_shell_type():
    if OS_NAME in ("Windows", "nt"):
        is_powershell = len(getenv("PSModulePath", "").split(pathsep)) >= 3
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
    script_blocks = re.findall('```(.*?)\n(.*?)```', text, re.DOTALL)
    if len(script_blocks) == 0:
        return None
    else:
        return script_blocks[0][1].strip()


def now_ms():
    return int(datetime.now().timestamp() * 1000)


def read_stdin():
    if sys.stdin.isatty() is False:
        buf = ''
        for line in sys.stdin:
            buf += line

        return buf
    else:
        return None
