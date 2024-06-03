# ShellGPT

[![](https://img.shields.io/pypi/v/shgpt)](https://pypi.org/project/shgpt/)
[![](https://github.com/jiacai2050/shellgpt/actions/workflows/ci.yml/badge.svg)](https://github.com/jiacai2050/shellgpt/actions/workflows/ci.yml)
[![](https://github.com/jiacai2050/shellgpt/actions/workflows/release.yml/badge.svg)](https://github.com/jiacai2050/shellgpt/actions/workflows/release.yml)

Chat with LLM in your terminal, be it shell generator, story teller, linux-terminal, etc.

# Install
```
pip install -U shgpt
```

This will install two commands: `sg` and `shgpt`, which are identical.

After install, use `sg --init` to create required directories(mainly `~/.shellgpt`).

# Usage

ShellGPT has three modes to use:
- Direct mode, `sg [question]` or pipeline like `echo question | sg`.
- TUI mode, `sg`, tailored for infer shell command.
- REPL mode, `sg -l`, chat with LLM.

See [conf.py](https://github.com/jiacai2050/shellgpt/blob/main/shgpt/utils/conf.py) for detailed configs.

## TUI

There are 3 key bindings to use in TUI:
- `ctrl+j`, Infer answer
- `ctrl+r`, Run command
- `ctrl+y`, Yank command

![TUI screenshot](https://github.com/jiacai2050/shellgpt/raw/main/assets/shellgpt-tui.jpg)

## Role

There are 4 built-in [system role contents](https://platform.openai.com/docs/guides/text-generation/chat-completions-api) in shellgpt:
- `default`, used for ask general questions
- `code`, used for ask programming questions
- `shell`, used for infer shell command
- `cm`, used for generate git commit message, like `git diff | sg -r cm`

Users can define their own content in `~/.shellgpt/roles.json`, it a JSON map with
- key being role name and
- value being role content

Or you can just copy [roles.json](https://github.com/jiacai2050/shellgpt/blob/main/roles.json) to play with, it's generated from [Awesome ChatGPT Prompts](https://github.com/f/awesome-chatgpt-prompts/blob/main/prompts.csv).

```bash
$ shgpt -r linux-terminal pwd
/home/user

$ shgpt -r javascript-console 0.1 + 0.2
0.3

```

# Requirements
- [Ollama](https://ollama.com/), you need to download models before try shellgpt.

# License

[GPL-3.0](https://opensource.org/license/GPL-3.0)
