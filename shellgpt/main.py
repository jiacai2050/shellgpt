from shellgpt.api.ollama import Ollama

if __name__ == '__main__':
    print(r'''
__      __   _                    _         ___ _        _ _  ___ ___ _____
\ \    / /__| |__ ___ _ __  ___  | |_ ___  / __| |_  ___| | |/ __| _ \_   _|
 \ \/\/ / -_) / _/ _ \ '  \/ -_) |  _/ _ \ \__ \ ' \/ -_) | | (_ |  _/ | |
  \_/\_/\___|_\__\___/_|_|_\___|  \__\___/ |___/_||_\___|_|_|\___|_|   |_|
''')
    ollama = Ollama('http://127.0.0.1:11434')
    while True:
        line = input("> ")
        if line != "":
            try:
                resp = ollama.generate(line)
                print(resp)
            except Exception as e:
                print(f"Error get resp: ${e}")
