import json
import os
from ..utils.http import TimeoutSession
from ..utils.common import *
from ..utils.conf import *
from .history import DummyHistory, FileHistory

HIST_SEP = "=========="


# https://github.com/ollama/ollama/blob/main/docs/api.md#generate-a-completion
class Ollama(object):
    def __init__(self, base_url, model, role, timeout):
        self.base_url = base_url
        self.http_session = TimeoutSession(timeout=timeout)
        if ENABLE_HISTORY:
            self.history_file = FileHistory(os.path.join(CONF_PATH, "history"))
        else:
            self.history_file = DummyHistory()
        self.model = model
        self.role = role

    def generate(self, prompt, stream=True):
        url = self.base_url + "/api/chat"
        debug_print(
            f"generate: {prompt} to {url} with model {self.model} role {self.role} and stream {stream}"
        )
        system_content = ROLE_CONTENT.get(self.role, self.role)
        payload = {
            "messages": [
                {"role": "system", "content": system_content, "name": "ShellGPT"},
                {"role": "user", "content": prompt, "name": "user"},
            ],
            "model": self.model,
            "stream": stream,
        }
        debug_print(f"Infer message: {payload}")
        r = self.http_session.post(url, json=payload, stream=stream)
        if r.status_code != 200:
            raise Exception("Error: " + r.text)

        answer = ""
        for item in r.iter_content(chunk_size=None):
            resp = json.loads(item)
            if resp["done"] is False:
                content = resp["message"]["content"]
                answer += content
                yield content
            else:
                self.history_file.write(rf"""{now_ms()},{resp['eval_duration']},{resp['eval_count']}
{prompt}
{HIST_SEP}
{answer}
{HIST_SEP}
""")
