# ShellGPT

[![](https://img.shields.io/pypi/v/shgpt)](https://pypi.org/project/shgpt/)
[![](https://github.com/jiacai2050/shellgpt/actions/workflows/ci.yml/badge.svg)](https://github.com/jiacai2050/shellgpt/actions/workflows/ci.yml)
[![](https://github.com/jiacai2050/shellgpt/actions/workflows/release.yml/badge.svg)](https://github.com/jiacai2050/shellgpt/actions/workflows/release.yml)

Chat with LLM in your terminal, be it shell generator, story teller, linux-terminal, etc.

# Install
```bash
pip install -U shgpt
```

Or install latest version
```bash
pip install --force-reinstall -U git+https://github.com/jiacai2050/shellgpt.git
```

This will install two commands: `sg` and `shellgpt`, which are identical.

After install, use `sg --init` to create required directories(mainly `~/.shellgpt`).

# Usage

ShellGPT has three modes to use:
- Direct mode, `sg [question]` or pipeline like `echo question | sg`.
- REPL mode, `sg -r`, chat with LLM.
- TUI mode, `sg -t`, tailored for infer shell command.

## Model

By default, `shellgpt` uses [Ollama](https://ollama.com/) as its language model backend, requiring installation prior to usage.

Alternatively, one can set up `shellgpt` to utilize [OpenAI compatible](https://developers.cloudflare.com/workers-ai/configuration/open-ai-compatibility/) API endpoints:

```bash
export SHELLGPT_API_URL=https://api.openai.com
export SHELLGPT_API_KEY=<token>
export SHELLGPT_MODEL='gpt-3.5-turbo'

# or Cloudflare Worker AI
export SHELLGPT_API_URL=https://api.cloudflare.com/client/v4/accounts/<account-id>/ai
export SHELLGPT_API_KEY=<token>
export SHELLGPT_MODEL='@cf/meta/llama-3-8b-instruct'
```

See [conf.py](https://github.com/jiacai2050/shellgpt/blob/main/shellgpt/utils/conf.py) for more configs.

## TUI

There are 3 key bindings to use in TUI:
- `ctrl+j`, Infer answer
- `ctrl+r`, Run command
- `ctrl+y`, Yank command

![TUI screenshot](https://github.com/jiacai2050/shellgpt/raw/main/assets/shellgpt-tui.jpg)

## System contents

There are some built-in [system contents](https://platform.openai.com/docs/guides/text-generation/chat-completions-api) in shellgpt:
- `default`, used for ask general questions
- `typo`, used for correct article typos.
- `slug`, used for generate URL slug.
- `code`, used for ask programming questions
- `shell`, used for infer shell command
- `commit`, used for generate git commit message, like `git diff | sg -c commit`

Users can define their own content in `~/.shellgpt/contents.json`, it a JSON map with
- key being content name and
- value being content body

Or you can just copy [contents.json](https://github.com/jiacai2050/shellgpt/blob/main/contents.json) to play with, it's generated from [Awesome ChatGPT Prompts](https://github.com/f/awesome-chatgpt-prompts/blob/main/prompts.csv).

```bash
$ sg -c linux-terminal pwd
/home/user

$ sg -c javascript-console 0.1 + 0.2
0.3

```

Users can share their customized contents in [discuss section](https://github.com/jiacai2050/shellgpt/discussions).

# License

[GPL-3.0](https://opensource.org/license/GPL-3.0)
