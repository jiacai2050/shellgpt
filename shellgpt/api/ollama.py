import json

from ..utils.http import TimeoutSession
from ..utils.common import base64_image, debug_print, prepare_prompt
from ..utils.conf import IMAGE_MODEL, SYSTEM_CONTENT


def get_system_content(sc):
    return None if sc == 'default' else SYSTEM_CONTENT.get(sc)


# https://github.com/ollama/ollama/blob/main/docs/api.md#generate-a-completion
class Ollama(object):
    def __init__(
        self, base_url, key, model, system_content, temperature, timeout, max_messages
    ):
        session = TimeoutSession(timeout=timeout)
        if key is not None and key != '':
            session.headers = {'Authorization': f'Bearer {key}'}
            self.use_openai = True
        else:
            self.use_openai = False
        self.base_url = base_url
        self.model = model
        self.http_session = session
        self.system_content = system_content
        self.temperature = temperature
        self.max_messages = max_messages
        self.messages = []

    def chat(self, prompt, stream=True, add_system_message=True):
        return (
            self.chat_openai(prompt, stream, add_system_message)
            if self.use_openai
            else self.chat_ollama(prompt, stream, add_system_message)
        )

    def chat_openai(self, prompt, stream, add_system_message):
        url = f'{self.base_url}/v1/chat/completions'
        debug_print(
            f'chat: {prompt} to {url} with model {self.model} system_content {self.system_content} and stream {stream}'
        )
        messages, model = self.make_messages(
            prompt,
            False,
            add_system_message,
        )
        payload = {
            'messages': messages,
            'model': model,
            'stream': stream,
            'temperature': self.temperature,
        }
        r = self.http_session.post(url, json=payload, stream=stream)
        if r.status_code != 200:
            raise Exception('Error: ' + r.text)

        answer = ''
        current = b''
        for item in r.iter_content(chunk_size=None):
            debug_print(f'item: {item}')
            for msg in item.split(b'\n\n'):
                msg = msg.strip(b'data: ')
                if len(msg) == 0:
                    continue

                current += msg

                # when current end with '}', it's the end of the message
                if current[-1] == 125:
                    msg = current
                    current = b''
                else:
                    continue

                s = msg.decode('utf-8')
                if s == '[DONE]':
                    self.messages.append({'role': 'assistant', 'content': answer})
                    return
                else:
                    resp = json.loads(s)
                    for item in resp['choices']:
                        msg = item['delta']['content']
                        answer += msg
                        yield msg

    def make_messages(self, prompt, support_image, add_system_message):
        model = self.model
        if add_system_message is False:
            return [{'role': 'user', 'content': prompt}], model

        after, imgs = prepare_prompt(prompt) if support_image else (prompt, [])
        if len(imgs) > 0:
            imgs = [base64_image(img) for img in imgs]
            self.messages.append({'role': 'user', 'content': after, 'images': imgs})
            model = IMAGE_MODEL
        else:
            self.messages.append({'role': 'user', 'content': prompt})

        if len(self.messages) > self.max_messages:
            self.messages = self.messages[-self.max_messages :]

        msgs = (
            []
            if self.system_content == 'default'
            else [
                {'role': 'system', 'content': get_system_content(self.system_content)}
            ]
        )
        for m in self.messages:
            msgs.append(m)

        return msgs, model

    def chat_ollama(self, prompt, stream, add_system_message):
        model = self.model
        url = self.base_url + '/api/chat'
        debug_print(
            f'chat: {prompt} to {url} with model {model} system_content {self.system_content} and stream {stream}'
        )

        messages, model = self.make_messages(prompt, True, add_system_message)
        payload = {
            'messages': messages,
            'model': model,
            'stream': stream,
            'options': {'temperature': self.temperature},
        }

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
