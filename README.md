# ShellGPT

[![](https://img.shields.io/pypi/v/shgpt)](https://pypi.org/project/shgpt/)

Generate shell command you want with power of LLM, without leaving your terminal!

# Install
```
pip install shgpt
```

This will install two commands: `sg` and `shgpt`.

# Usage

ShellGPT has three modes to use:
- Direct mode, `sg [question]` or `echo question | sg`.
- `sg`, Enter TUI mode, tailored for infer shell command
- `sg -l`, Enter an interactive REPL.

See [conf.py](shgpt/utils/conf.py) for configs.

## Role

There are some built-in roles in shellgpt:
- `default`, used for ask general questions
- `code`, used for ask programming questions
- `shell`, used for infer shell command
- `cm`, used for generate git commit message

```bash
git diff | sg -r cm
```

Users can provide their own role with `-r` option.

## TUI generate git commit message

Users can provide their own role with `-r`There are some key bindings to use in TUI: option
- `ctrl+j`, Infer answer
- `ctrl+r`, Run command
- `ctrl+y`, Yank command

![TUI screenshot](./assets/shellgpt-tui.jpg)

# Requirements
- [Ollama](https://ollama.com/), you need to download models before try shellgpt.

# License

[GPL-3.0](https://opensource.org/license/GPL-3.0)
