from os import path, environ

# Configuration
CONF_PATH = path.expanduser(environ.get('SHELLGPT_CONF_DIR', '~/.shellgpt'))
OLLAMA_URL = environ.get('SHELLGPT_OLLAMA_URL', "http://127.0.0.1:11434")
OLLAMA_MODEL = environ.get('SHELLGPT_OLLAMA_MODEL', 'llama3')
INFER_TIMEOUT = int(environ.get('SHELLGPT_INFER_TIMEOUT', '15'))  # seconds
