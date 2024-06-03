import json
from ..utils.http import TimeoutSession
from ..utils.common import base64_image, debug_print, prepare_prompt
from ..utils.conf import MAX_CHAT_MESSAGES, OLLAMA_IMAGE_MODEL, ROLE_CONTENT


# https://github.com/ollama/ollama/blob/main/docs/api.md#generate-a-completion
class Ollama(object):
    def __init__(self, base_url, model, role, temperature, timeout):
        self.base_url = base_url
        self.http_session = TimeoutSession(timeout=timeout)
        self.model = model
        self.role = role
        self.temperature = temperature
        self.max_messages = MAX_CHAT_MESSAGES
        self.system_message = (
            None
            if role == 'default'
            else {'role': 'system', 'content': ROLE_CONTENT.get(self.role)}
        )
        self.messages = []

    def chat(self, prompt, stream=True):
        url = self.base_url + '/api/chat'
        debug_print(
            f'chat: {prompt} to {url} with model {self.model} role {self.role} and stream {stream}'
        )

        after, imgs = prepare_prompt(prompt)
        model = self.model
        if len(imgs) > 0:
            imgs = [base64_image(img) for img in imgs]
            self.messages.append({'role': 'user', 'content': after, 'images': imgs})
            model = OLLAMA_IMAGE_MODEL
        else:
            self.messages.append({'role': 'user', 'content': prompt})

        if len(self.messages) > self.max_messages:
            self.messages = self.messages[-self.max_messages :]

        payload = {
            'messages': [] if self.system_message is None else [self.system_message],
            'model': model,
            'stream': stream,
            'options': {'temperature': self.temperature},
        }
        for m in self.messages:
            payload['messages'].append(m)

        debug_print(f'Infer message: {payload}')
        r = self.http_session.post(url, json=payload, stream=stream)
        if r.status_code != 200:
            raise Exception('Error: ' + r.text)

        answer = ''
        for item in r.iter_content(chunk_size=None):
            resp = json.loads(item)
            if resp['done']:
                self.messages.append({'role': 'assistant', 'content': answer})
            else:
                content = resp['message']['content']
                answer += content
                yield content

    def generate(self, prompt, stream=True):
        url = self.base_url + '/api/generate'
        debug_print(
            f'generate: {prompt} to {url} with model {self.model} role {self.role} and stream {stream}'
        )

        payload = {
            'model': self.model,
            'prompt': prompt,
            'stream': stream,
            'options': {'temperature': self.temperature},
        }
        r = self.http_session.post(url, json=payload, stream=stream)
        if r.status_code != 200:
            raise Exception('Error: ' + r.text)

        for item in r.iter_content(chunk_size=None):
            resp = json.loads(item)
            if resp['done'] is False:
                content = resp['response']
                yield content
