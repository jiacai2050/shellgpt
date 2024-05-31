# ShellGPT

Generate shell command you want with power of LLM, without leaving your terminal!

# Install
```
pip install shgpt
```
# Usage

ShellGPT has three modes to use:
- `sg {your question}`
- `sg`, Enter TUI mode
- `sg -l`, Enter an interactive REPL

See [conf.py](shellgpt/utils/conf.py) for configs.

## TUI
There are some key bindings to use in TUI:
- `ctrl+j`, Infer answer
- `ctrl+r`, Run command
- `ctrl+y`, Yank command

# Requirements
- [Ollama](https://ollama.com/), you need to download models before try shellgpt.

# License

[GPL-3.0](https://opensource.org/license/GPL-3.0)
