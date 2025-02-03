from textual.app import App, ComposeResult, Binding
from textual.widgets import Header, Footer, Static, TextArea, Button
from typing import Optional
from ..utils.common import copy_text, execute_cmd, debug_print, extract_code


class PromptInput(Static):
    def __init__(self, prompt):
        self.initial_prompt = prompt
        super().__init__()

    def compose(self) -> ComposeResult:
        yield TextArea(self.initial_prompt, id='prompt_input')


class AnswerOutput(Static):
    def compose(self) -> ComposeResult:
        yield TextArea(id='answer_output')


class CommandOutput(Static):
    def compose(self) -> ComposeResult:
        yield TextArea(id='command_output', read_only=True)


class ButtonDispatch(Static):
    def __init__(self, yank_handler, run_handler):
        super().__init__()
        self.yank_handler = yank_handler
        self.run_handler = run_handler

    def compose(self) -> ComposeResult:
        yield Button(label='Copy', variant='primary', id='copy')
        yield Button(label='Run', variant='error', id='run')

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Event handler called when a button is pressed."""
        if event.button.id == 'copy':
            self.yank_handler()
        elif event.button.id == 'run':
            self.run_handler()


class ShellGPTApp(App):
    CSS_PATH = 'app.tcss'
    BINDINGS = [
        Binding('ctrl+j', 'infer', 'Infer answer'),
        Binding('ctrl+d', 'toggle_dark', 'Toggle dark mode'),
        Binding('ctrl+y', 'yank', 'Yank code block', priority=True),
        Binding('ctrl+r', 'run', 'Run code block'),
    ]

    def __init__(self, llm, history, initial_prompt):
        self.llm = llm
        self.history = history
        self.has_inflight_req = False
        self.initial_prompt = initial_prompt
        super().__init__()

    def on_mount(self) -> None:
        self.title = f'ShellGPT({self.llm.model})'

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        yield PromptInput(self.initial_prompt)
        yield AnswerOutput()
        yield ButtonDispatch(
            lambda: self.action_yank(),
            lambda: self.action_run(),
        )
        yield CommandOutput()
        yield Footer()

    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        self.theme = (
            'textual-dark' if self.theme == 'textual-light' else 'textual-light'
        )

    def action_infer(self) -> None:
        """An action to infer answer."""
        if self.has_inflight_req:
            return

        self.has_inflight_req = True
        try:
            self.infer_inner()
        except Exception as e:
            answer_output = self.query_one('#answer_output')
            answer_output.load_text(f'Error when infer: {e}')
        finally:
            self.has_inflight_req = False

    def get_prompt_input(self) -> Optional[str]:
        prompt_input = self.query_one('#prompt_input')
        prompt = prompt_input.text.strip()
        return None if prompt == '' else prompt

    def get_answer_output(self) -> Optional[str]:
        out = self.query_one('#answer_output')
        text = out.text.strip()
        return None if text == '' else text

    def infer_inner(self) -> None:
        prompt = self.get_prompt_input()
        if prompt is None:
            return

        debug_print(f'infer {prompt}')
        self.history.add(prompt)
        resp = self.llm.chat(prompt)
        buf = ''
        for item in resp:
            buf += item

        script = extract_code(buf)
        if script is not None:
            buf = script

        debug_print(f'infer ret {buf}')
        answer_output = self.query_one('#answer_output')
        answer_output.load_text(buf)

    def action_yank(self) -> None:
        text = self.get_answer_output()
        if text is None:
            return

        copy_text(text)

    def action_run(self) -> None:
        text = self.get_answer_output()
        if text is None:
            return

        cmd = text
        output = execute_cmd(cmd)
        command_output = self.query_one('#command_output')
        command_output.load_text(output)
