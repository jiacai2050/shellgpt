import json, os
from ..utils.http import TimeoutSession
from ..utils.common import *
from ..utils.conf import *

HIST_SEP = '=========='
CONTENT = {
    'default': f'You are a shell script assistant on {OS_NAME}, output the best matching shell command',
    'only-cmd': f'You are a shell script assistant on {OS_NAME}, output the best matching shell command only, without any other information, or any quotes',
}

# https://github.com/ollama/ollama/blob/main/docs/api.md#generate-a-completion
class Ollama(object):
    def __init__(self, base_url, model='ollama3', timeout=10):
        self.base_url = base_url
        self.http_session = TimeoutSession(timeout=timeout)
        self.history_file = open(os.path.join(CONF_PATH, 'history'), 'a+')
        self.model = model

    def generate(self, prompt, stream=True, only_cmd=False):
        url = self.base_url + '/api/chat'
        debug_print(f"generate: {prompt} to {url} with model {self.model} and stream {stream}")
        system_content = CONTENT['only-cmd'] if only_cmd else CONTENT['default']
        payload = {
            'messages': [
                {'role': 'system', 'content': system_content},
                {'role': 'user', 'content': prompt},
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
