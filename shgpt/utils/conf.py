from os import path, environ
import json
from .common import OS_NAME, SHELL

# Configuration
CONF_PATH = path.expanduser(environ.get("SHELLGPT_CONF_DIR", "~/.shellgpt"))
OLLAMA_URL = environ.get("SHELLGPT_OLLAMA_URL", "http://127.0.0.1:11434")
OLLAMA_MODEL = environ.get("SHELLGPT_OLLAMA_MODEL", "llama3")
INFER_TIMEOUT = int(environ.get("SHELLGPT_INFER_TIMEOUT", "15"))  # seconds
ENABLE_HISTORY = int(environ.get("SHELLGPT_ENABLE_HISTORY", "0")) == 1

# There are different roles for different types of prompts
ROLE_CONTENT = {
    "default": "",
    "code": """
Provide only code as output without any description.
Provide only code in plain text format without Markdown formatting.
Do not include symbols such as ``` or ```python.
If there is a lack of details, provide most logical solution.
You are not allowed to ask for more details.
For example if the prompt is "Hello world Python", you should return "print('Hello world')".
    """,
    "shell": """
    You are a shell script assistant on {os_name} running {shell},
    Output the best matching shell commands without any other information, or any quotes.
    Make sure it's valid shell command.
    """.format(os_name=OS_NAME, shell=SHELL),
    # commit message
    "cm": """
    Generate git commit message for this changes.
    """,
}


def load_roles_from_config():
    conf_file = path.join(CONF_PATH, "roles.json")
    with open(conf_file) as r:
        roles = json.loads(r.read())
        global ROLE_CONTENT
        ROLE_CONTENT.update(roles)
