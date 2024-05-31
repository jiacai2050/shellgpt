from enum import Enum
from typing import Optional
from datetime import datetime
import re, platform, os

IS_VERBOSE = False
TEST_PROMPT = "tell me how to get current disk usage by shell command"
OS_NAME = platform.system()

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
