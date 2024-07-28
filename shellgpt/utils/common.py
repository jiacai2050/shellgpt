from enum import Enum
from typing import Optional
from datetime import datetime
import re
import base64
import os
import subprocess
import sys
import pyperclip
import json

from shellgpt.utils.conf import DEFAULT_IMAGE_DIR, IS_TTY, SYSTEM_CONTENT, CONF_PATH

IS_VERBOSE = False


class AppMode(Enum):
    Direct = (1,)
    TUI = (2,)
    REPL = (3,)


def set_verbose(v):
    global IS_VERBOSE
    IS_VERBOSE = v


def is_verbose():
    return IS_VERBOSE


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
    if text is None:
        print('No text to copy!')
    else:
        pyperclip.copy(text)


def execute_cmd(cmd, ask=False):
    if 'y' == input(f'Type y to run: `{cmd}`> '):
        return subprocess.getoutput(cmd)


def base64_image(image_path: str) -> str:
    with open(image_path, 'rb') as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


# https://www.debuggex.com/r/6b2cfvu8bb_stYGu
FILE_PATH_RE = re.compile(r' (\/|@@)(.*?)\.(jpg|png)(?:\s|$)')


def extract_paths(txt):
    r = re.findall(FILE_PATH_RE, txt)
    return r


def gen_path(prefix, left, suffix):
    name = left + '.' + suffix
    if prefix == '/':
        return prefix + name
    else:
        return os.path.join(DEFAULT_IMAGE_DIR, name)


def prepare_prompt(raw):
    imgs = [
        gen_path(prefix, path, suffix) for (prefix, path, suffix) in extract_paths(raw)
    ]
    after = raw if len(imgs) == 0 else re.sub(FILE_PATH_RE, '', raw)
    return after, imgs


def load_contents_from_config(throw_ex=False):
    try:
        conf_file = os.path.join(CONF_PATH, 'contents.json')
        with open(conf_file) as r:
            contents = json.loads(r.read())
            global SYSTEM_CONTENT
            SYSTEM_CONTENT.update(contents)
    except Exception as e:
        debug_print(f'Error when load contents: ${e}')
        if throw_ex:
            raise e
