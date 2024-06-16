import requests


# https://blog.apify.com/python-requests-timeout/
class TimeoutSession(requests.Session):
    def __init__(self, timeout=10):
        self.default_timeout = timeout
        super().__init__()

    def request(self, method, url, **kwargs):
        kwargs.setdefault('timeout', self.default_timeout)
        return super().request(method, url, **kwargs)
