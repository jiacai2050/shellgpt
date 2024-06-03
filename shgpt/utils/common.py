from enum import Enum
from typing import Optional
from datetime import datetime
import re
import base64
import os
import subprocess
import sys
import pyperclip

from shgpt.utils.conf import DEFAULT_IMAGE_DIR, IS_TTY

IS_VERBOSE = False


class AppMode(Enum):
    Direct = (1,)
    TUI = (2,)
    REPL = (3,)


def set_verbose(v):
    global IS_VERBOSE
    IS_VERBOSE = v


def debug_print(msg):
    if IS_VERBOSE:
        print(msg)


def extract_code(text: str) -> Optional[str]:
    code = re.findall('```(?:.*?)\n(.*?)```', text, re.DOTALL)
    if len(code) == 0:
        return None
    else:
        return code[0].strip()


def now_ms():
    return int(datetime.now().timestamp() * 1000)


def read_stdin():
    if IS_TTY:
        return None
    else:
        buf = ''
        for line in sys.stdin:
            buf += line

        return buf


def copy_text(text):
    pyperclip.copy(text)


def execute_cmd(cmd):
    return subprocess.getoutput(cmd)


def base64_image(image_path: str) -> str:
    with open(image_path, 'rb') as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


# https://www.debuggex.com/r/6b2cfvu8bb_stYGu
FILE_PATH_RE = re.compile(r' (\/|@@)(.*?)(?:\s|$)', re.I | re.M)


def extract_paths(txt):
    return re.findall(FILE_PATH_RE, txt)


def gen_path(prefix, left):
    if prefix == '/':
        return prefix + left
    else:
        return os.path.join(DEFAULT_IMAGE_DIR, left)


def prepare_prompt(raw):
    imgs = [gen_path(prefix, path) for (prefix, path) in extract_paths(raw)]
    after = raw if len(imgs) == 0 else re.sub(FILE_PATH_RE, '', raw)
    return after, imgs
