import readline
import atexit
from .utils.conf import CONF_PATH, MAX_HISTORY
from os import path


class History:
    def __init__(self, filename=path.join(CONF_PATH, 'history')):
        self.filename = filename
        try:
            readline.read_history_file(filename)
            readline.set_history_length(MAX_HISTORY)
        except FileNotFoundError:
            pass
        atexit.register(self.save)

    def save(self):
        try:
            readline.write_history_file(self.filename)
        except Exception:
            pass

    def add(self, line):
        readline.add_history(line)

    def len(self):
        return readline.get_current_history_length()

    def remove_last(self):
        return readline.remove_history_item(self.len() - 1)

    def __del__(self):
        self.save()
