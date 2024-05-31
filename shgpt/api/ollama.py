import json, os
from ..utils.http import TimeoutSession
from ..utils.common import *
from ..utils.conf import *

HIST_SEP = '=========='
CONTENT = {
    'default': f'''You are programming and system administration assistant.
    You are managing {OS_NAME} operating system with {SHELL} shell.
    ''',
    'shell': f'''
    You are a shell script assistant on {OS_NAME} running {SHELL},
    Output the best matching shell commands without any other information, or any quotes.
    Make sure it's valid shell command.
    ''',
    # commit message
    'cm': f'''
    Generate git commit message for this changes.
    ''',
}

# https://github.com/ollama/ollama/blob/main/docs/api.md#generate-a-completion
class Ollama(object):
    def __init__(self, base_url, model, role, timeout):
        self.base_url = base_url
        self.http_session = TimeoutSession(timeout=timeout)
        self.history_file = open(os.path.join(CONF_PATH, 'history'), 'a+')
        self.model = model
        self.role = role

    def generate(self, prompt, stream=True):
        url = self.base_url + '/api/chat'
        debug_print(f"generate: {prompt} to {url} with model {self.model} and stream {stream}")
        system_content = CONTENT.get(self.role, self.role)
        payload = {
            'messages': [
                {'role': 'system', 'content': system_content, 'name': 'ShellGPT'},
                {'role': 'user', 'content': prompt, 'name': 'user'},
            ],
            'model': self.model,
            'stream': stream
        }
        debug_print(f'Infer message: {payload}')
        r = self.http_session.post(url, json=payload, stream=stream)
        if r.status_code != 200:
            raise Exception("Error: " + r.text)

        answer = ''
        for item in r.iter_content(chunk_size=None):
            debug_print(f"Infer resp item: {item}\n")
            resp = json.loads(item)
            if resp['done'] is False:
                content = resp['message']['content']
                answer += content
                yield content
            else:
                self.history_file.write(fr'''{now_ms()},{resp['eval_duration']},{resp['eval_count']}
{prompt}
{HIST_SEP}
{answer}
{HIST_SEP}
''')
