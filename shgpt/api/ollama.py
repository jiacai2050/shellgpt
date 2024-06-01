import json
from ..utils.http import TimeoutSession
from ..utils.common import *
from ..utils.conf import *


# https://github.com/ollama/ollama/blob/main/docs/api.md#generate-a-completion
class Ollama(object):
    def __init__(self, base_url, model, role, timeout):
        self.base_url = base_url
        self.http_session = TimeoutSession(timeout=timeout)
        self.model = model
        self.role = role
        self.system_message = (
            None
            if role == "default"
            else {"role": "system", "content": ROLE_CONTENT.get(self.role)}
        )
        self.messages = []

    def chat(self, prompt, stream=True):
        url = self.base_url + "/api/chat"
        debug_print(
            f"generate: {prompt} to {url} with model {self.model} role {self.role} and stream {stream}"
        )
        self.messages.append({"role": "user", "content": prompt})
        if len(self.messages) > 10:
            self.messages = self.messages[-10:]
        payload = {
            "messages": [] if self.system_message is None else [self.system_message],
            "model": self.model,
            "stream": stream,
        }
        for m in self.messages:
            payload["messages"].append(m)

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
