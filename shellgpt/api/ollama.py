from shellgpt.utils.http import TimeoutSession

# https://github.com/ollama/ollama/blob/main/docs/api.md#generate-a-completion
class Ollama(object):
    def __init__(self, base_url, timeout=10):
        self.base_url = base_url
        self.http_session = TimeoutSession(timeout=timeout)

    def generate(self, prompt, model='llama3', stream=False):
        url = self.base_url + '/api/generate'
        payload = {'prompt': prompt, 'model': model, 'stream': stream}
        r = self.http_session.post(url, json=payload)
        if r.status_code != 200:
            raise Exception("Error: " + r.text)

        r = r.json()
        if 'error' in r:
            raise Exception("Error: " + r['error'])

        return r.get('response')

    def supported_models(self):
        return ['ollama3', 'codellama', 'ollama2']
