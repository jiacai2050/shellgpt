class FileHistory(object):
    def __init__(self, path):
        self.path = path
        self.file = open(path, "a+")

    def write(self, content):
        self.file.write(content)
        self.file.flush()

    def close(self):
        self.file.close()


class DummyHistory(object):
    def write(self, content):
        pass

    def close(self):
        pass
