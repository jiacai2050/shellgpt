from os import path, environ, pathsep
import sys
import platform

# Configuration
CONF_PATH = path.expanduser(environ.get('SHELLGPT_CONF_DIR', '~/.shellgpt'))
API_URL = environ.get('SHELLGPT_API_URL', 'http://127.0.0.1:11434')
API_KEY = environ.get('SHELLGPT_API_KEY', '')
MODEL = environ.get('SHELLGPT_MODEL', 'llama3')
IMAGE_MODEL = environ.get('SHELLGPT_IMAGE_MODEL', 'llava')
TEMPERATURE = float(environ.get('SHELLGPT_TEMPERATURE', '0.8'))
DEFAULT_IMAGE_DIR = path.expanduser(environ.get('SHELLGPT_IMAGE_DIR', '~/Pictures'))
INFER_TIMEOUT = int(environ.get('SHELLGPT_INFER_TIMEOUT', '15'))  # seconds
MAX_HISTORY = int(environ.get('SHELLGPT_MAX_HISTORY', '1000'))
MAX_CHAT_MESSAGES = int(environ.get('SHELLGPT_MAX_CHAT_MESSAGES', '5'))

# Auto determined configs
OS_NAME = platform.system()
IS_TTY = sys.stdin.isatty()


def get_shell_type():
    if OS_NAME in ('Windows', 'nt'):
        is_powershell = len(environ.get('PSModulePath', '').split(pathsep)) >= 3
        return 'powershell.exe' if is_powershell else 'cmd.exe'
    return path.basename(environ.get('SHELL', '/bin/sh'))


SHELL = get_shell_type()


# Built-in system content for different user cases.
SYSTEM_CONTENT = {
    'default': None,
    'code': """
Provide only code as output without any description.
Provide only code in plain text format without Markdown formatting.
Do not include symbols such as ``` or ```python.
If there is a lack of details, provide most logical solution.
You are not allowed to ask for more details.
For example if the prompt is "Hello world Python", you should return "print('Hello world')".
    """,
    'shell': """
    You are a shell script assistant on {os_name} running {shell},
    Output the best matching shell commands without any other information, or any quotes.
    Make sure it's valid shell command.
    """.format(os_name=OS_NAME, shell=SHELL),
    'commit': "You are now a git commit message writer. I'll give you a list of changes, and you'll reply with a commit message that summarizes these changes in a clear and concise way, keeping the original formatting.",
    'typo': """
    You are now an article correction assistant. You need to find out the input text in the spelling errors, incoherent places, can only return the corrected text, without any explanation. The output keeps the original format and language output, don't modify the style, and keey the code blocks unchanged.
    """,
    'slug': 'You are now a slug generator. I will give you some sentences, and you will reply with a slug version of those sentences. A slug is a URL-friendly version of a title, where spaces are replaced with hyphens, and all characters are lowercased. Do not include any special characters, and keep the output in English.',
}
