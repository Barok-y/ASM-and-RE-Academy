from __future__ import annotations

from pathlib import Path
from typing import ClassVar, List, Optional

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.screen import Screen
from textual.widgets import (
    Button,
    Footer,
    Header,
    Input,
    Label,
    ListItem,
    ListView,
    Static,
    TextArea,
)

from academy.core import default_mission_pack
from academy.curriculum import Lesson, LessonSession, Module, all_modules, get_module
from academy.debugger import Debugger
from academy.grading import Challenge, Grader, HintEngine, sample_challenges
from academy.grading.ctf import ctf_challenges
from academy.sandbox import Sandbox
from academy.sandbox.explain import (
    explain_diff,
    format_flags,
    format_registers,
    hexdump,
)
from academy.sandbox.sandbox import CommandResult
from academy.ui.logo import ACADEMY_LOGO

DEFAULT_PROGRAM = """\
mov rax, 60
mov rdi, 42
syscall
"""

DEFAULT_DEBUG_PROGRAM = """\
mov rax, 10
add rax, 5
sub rax, 3
mov rdi, rax
mov rax, 60
syscall
"""

_SANDBOX_TUTORIAL = """\
WHAT THE SANDBOX IS FOR
-----------------------
Think of it as your own CPU you can hold still and inspect. Assembly runs inside
a machine, and beginners are told "trust me, RAX becomes 5". The sandbox lets
you PROVE it: you type one command, the CPU moves one step, and the panels show
you the exact byte-by-byte change. It is your microscope for everything the
lessons teach.

The six panels are live: CODE (next instructions), REGISTERS, FLAGS, MEMORY,
STACK, and OUTPUT. Every command updates them instantly.

TYPE `demo` TO WATCH IT EXPLAINED, or follow this walkthrough:
  1. help            -> list every command
  2. run             -> execute the whole program right now
  3. reset           -> rewind back to the start
  4. step 1          -> execute ONE instruction and watch what changes
  5. registers       -> read all registers
  6. flags           -> read the CPU condition flags
  7. explain         -> plain-language note on the last change
8. trace 5         -> step 5 times, listing each register change
   9. disassemble 10  -> show the next 10 instructions
   10. rewind          -> undo the last step (or press Z)

Inspecting memory and the stack:
  memory 0x600000 16   -> 16 bytes of data memory (hexdump)
  stack 8              -> the current stack (grows DOWN)

Debugging controls:
  break 0x400000       -> stop when the CPU reaches an address
  watch 0x600000 8     -> fire when 8 bytes at that address change
  next / continue      -> step over a call, or run to the end

The status line shows where the CPU is: running / halted / exited.
If a program has no final exit syscall it simply runs out of instructions.
"""

_DEBUGGER_TUTORIAL = """\
WHAT THE DEBUGGER IS FOR
------------------------
A debugger runs ONE instruction at a time so you can watch every write to
registers, flags, memory, and the stack — the fastest way to build real
intuition about fetch/decode/execute. The lessons teach you the steps; the
debugger is where you SEE them happen.

Keys:  F step-into   O step-over   T step-out   C continue   R reset

Try this: press F a few times and watch the #registers panel change as 10 is
loaded into RAX, then ADD 5, then SUB 3, then the exit syscall fires.

Habit to build: before each F, predict what the next instruction will change.
That prediction muscle is the entire point of the debugger — and of being a
reverse engineer.
"""

MENU_ORDER = (
    "learn",
    "practice",
    "daily",
    "challenges",
    "projects",
    "author",
    "sandbox",
    "debugger",
    "notebook",
    "profile",
    "progress",
    "settings",
    "quit",
)

MENU_LABELS = {
    "learn": "Learn",
    "practice": "Practice",
    "daily": "Daily Challenge",
    "challenges": "Challenges",
    "projects": "Projects",
    "author": "Author & Create",
    "sandbox": "Sandbox",
    "debugger": "Debugger",
    "notebook": "Notebook",
    "profile": "Profile",
    "progress": "Progress",
    "settings": "Settings",
    "quit": "Quit",
}

BACK_BINDINGS = [
    Binding("b", "app.pop_screen", "Back"),
    Binding("escape", "app.pop_screen", "Back"),
]

_STATUS_GLYPH = {
    "concept": "\u25C8",
    "intuition": "\u2736",
    "analogy": "\u2387",
    "visualization": "\u25B2",
    "example": "\u25C6",
    "walkthrough": "\u25B6",
    "prediction": "\u2753",
    "response": "\u270D",
    "feedback": "\u21BA",
    "challenge": "\u2694",
    "reflection": "\u2766",
}


class CodeArea(TextArea):
    def __init__(self, name: str | None = None, id: str | None = None,
                 placeholder: str = "", **kwargs) -> None:
        super().__init__(placeholder=placeholder, id=id, name=name, **kwargs)

    @property
    def value(self) -> str:
        return self.text

    @value.setter
    def value(self, text: str) -> None:
        self.text = text if text else ""

    async def _on_key(self, event) -> None:
        key = event.key
        if key in ("enter", "ctrl+enter"):
            event.stop()
            event.prevent_default()
            self.post_message(Input.Submitted(self, self.value))
            return
        if key == "shift+enter":
            event.stop()
            event.prevent_default()
            self.insert("\n")
            return
        await super()._on_key(event)


class MainMenuScreen(Screen):
    BINDINGS = [Binding("q", "app.quit", "Quit")]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Horizontal(id="menu-body"):
            with VerticalScroll(id="menu-side"):
                yield Static("Assembly & Reverse Engineering Academy", id="title")
                with Vertical(classes="menu-col"):
                    for option in MENU_ORDER:
                        yield Button(MENU_LABELS[option], id=f"menu-{option}")
            yield Static(ACADEMY_LOGO, id="logo", classes="panel")
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        option = event.button.id.removeprefix("menu-")
        if option == "quit":
            self.app.exit()
        elif option == "author":
            self.action_open_author()
        elif option == "daily":
            from academy.grading import daily_challenge

            self.app.push_screen(ChallengeScreen(daily_challenge(), self.app.state))
        else:
            self.app.push_screen(option)

    def action_open_author(self) -> None:
        from academy.ui.authoring import AuthorModeScreen

        self.app.push_screen(AuthorModeScreen(self.app.state))


class LearnScreen(Screen):
    """Module list -> lesson list -> lesson runner."""

    BINDINGS = BACK_BINDINGS

    def __init__(self) -> None:
        super().__init__()

    @staticmethod
    def _user_modules(state) -> List[Module]:
        try:
            lesson_dicts = state.user_content.lesson_dicts()
        except Exception:
            return []
        from academy.curriculum import Lesson, Module
        from academy.curriculum.models import LessonStep

        if not lesson_dicts:
            return []
        by_module: dict = {}
        for ld in lesson_dicts:
            steps = [
                LessonStep(
                    kind=s.get("kind", "concept"),
                    content=s.get("content", ""),
                    high_level=s.get("high_level", ""),
                    program=s.get("program", ""),
                    expected=s.get("expected", {}),
                    model_answer=s.get("model_answer", ""),
                    keywords=s.get("keywords", []) or [],
                    hint=s.get("hint", ""),
                    trace=s.get("trace", ""),
                )
                for s in ld.get("steps", [])
            ]
            lesson = Lesson(
                id=ld.get("id", "user_lesson"),
                module=ld.get("module", "user"),
                title=ld.get("title", "Untitled lesson"),
                order=ld.get("order", 1),
                steps=steps,
            )
            by_module.setdefault(lesson.module, []).append(lesson)
        return [
            Module(
                id=mid,
                title=f"My Lessons ({mid})",
                order=99,
                lessons=lessons,
            )
            for mid, lessons in by_module.items()
        ]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Static("Modules", id="learn-title")
        yield ListView(id="learn-list")
        yield Static("Enter to open a module; B to go back.", classes="hint")
        yield Footer()

    def on_mount(self) -> None:
        self.load_list()

    def load_list(self) -> None:
        modules = all_modules() + self._user_modules(self.app.state)
        list_view = self.query_one("#learn-list")
        list_view.clear()
        for module in modules:
            list_view.append(
                ListItem(Label(self._module_label(module)))
            )

    @staticmethod
    def _module_label(module: Module) -> str:
        return f"[{module.order:02d}] {module.title}  ({len(module.lessons)} lessons)"

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        modules = all_modules() + self._user_modules(self.app.state)
        module = modules[event.list_view.index]
        self.app.push_screen(LessonListScreen(module))


class LessonListScreen(Screen):
    BINDINGS = BACK_BINDINGS

    def __init__(self, module: Module) -> None:
        super().__init__()
        self._module = module

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Static(self._module.title, id="module-title")
        yield ListView(
            *[
                ListItem(Label(f"{lesson.order}. {lesson.title}"))
                for lesson in self._module.lessons
            ],
            id="lesson-list",
        )
        yield Static("Enter to start a lesson; B to go back.", classes="hint")
        yield Footer()

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        lesson = self._module.lessons[event.list_view.index]
        self.app.push_screen(LessonScreen(lesson, self.app.state))


class LessonScreen(Screen):
    BINDINGS = [
        Binding("n", "advance", "Next"),
        Binding("enter", "advance", "Next"),
        Binding("ctrl+n", "advance", "Next"),
        Binding("r", "run_program", "Run"),
        Binding("c", "run_challenge", "Verify"),
        Binding("ctrl+enter", "run_challenge", "Verify"),
        Binding("h", "show_hint", "Hint"),
        Binding("v", "toggle_views", "Views"),
        Binding("x", "toggle_cheatsheet", "Cheat sheet"),
    ] + BACK_BINDINGS

    def __init__(self, lesson: Lesson, state) -> None:
        super().__init__()
        self.session = LessonSession(lesson)
        self._state = state
        self._feedback = ""
        self._show_views = True
        self._complete = False
        self._challenge_passed = False
        self._response_passed = False
        self._ran = False
        self._step_diff = ""
        self._rendered_index = -1
        self._show_cheatsheet = False

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Static("", id="lesson-header")
        yield Static("", id="lesson-step")
        yield Static("", id="lesson-feedback")
        with Horizontal(id="views"):
            yield Static("", id="view-source", classes="panel")
            yield Static("", id="view-asm", classes="panel")
            yield Static("", id="view-state", classes="panel")
        yield CodeArea(
            placeholder="write your assembly for the challenge, then press Enter or Ctrl+Enter",
            id="lesson-input",
        )
        yield Static("", classes="hint")
        yield Footer()

    def on_mount(self) -> None:
        self.query_one("#views").display = self._show_views
        resume = self._state.lesson_position(self.session.lesson.id)
        if resume is not None:
            resume = max(0, min(resume, len(self.session.lesson.steps) - 1))
            self.session.index = resume
        self._render_view()

    def _current(self):
        return self.session.current

    def _render_view(self) -> None:
        step = self._current()
        if self.session.index != self._rendered_index:
            self._rendered_index = self.session.index
            self._ran = False
            self._step_diff = ""
        header = (
            f"[b]{self.session.lesson.title}[/b]  "
            f"[b][{self.session.index + 1}/{len(self.session.lesson.steps)}][/b]  "
            f"[{step.kind.upper()}]  {_STATUS_GLYPH[step.kind]}"
        )
        self.query_one("#lesson-header").update(header)
        if self._show_cheatsheet:
            from academy.curriculum.reference import cheat_sheet_text

            self.query_one("#lesson-step").update(cheat_sheet_text())
            self.query_one("#lesson-feedback").update(
                "[cyan]Cheat sheet (X: close) — opcodes, registers, flags, syscalls.[/cyan]"
            )
            self._update_hint()
            return
        body = step.content
        if step.high_level:
            body += f"\n\n[bold cyan]high level:[/bold cyan] {step.high_level}"
        if step.options:
            body += "\n\n[b]choose:[/b]\n"
            for i, option in enumerate(step.options, start=1):
                body += f"  [cyan]{i}.[/cyan] {option}\n"
        if step.program:
            body += f"\n[bold magenta]assembly:[/bold magenta]\n{step.program}"
        if step.trace:
            body += f"\n\n[bold green]{step.trace}[/bold green]"
        if step.kind == "challenge" and step.expected:
            body += f"\n[b]target end-state:[/b] {step.expected}"
        self.query_one("#lesson-step").update(body)
        self.query_one("#lesson-feedback").update(self._feedback)
        input_widget = self.query_one("#lesson-input")
        interactive = step.kind in ("challenge", "response")
        input_widget.visible = interactive
        if step.kind == "response":
            input_widget.placeholder = "type your own words, then press Enter to check"
        elif step.kind == "challenge":
            input_widget.placeholder = (
                "write your assembly, then press Enter to check (Shift+Enter = new line)"
            )
        if interactive:
            input_widget.focus()
        else:
            input_widget.blur()
        self._update_hint()
        if self._show_views:
            self._update_views()

    def _update_hint(self) -> None:
        step = self._current()
        progress = self._progress_bar()
        if self._show_cheatsheet:
            text = ""
        elif self._complete:
            text = "Lesson complete! Enter/N: next lesson   B/Esc: back to list"
        elif step.kind == "response":
            text = (
                "Type your answer in your own words; Enter: check   Ctrl+N: skip   "
                "Esc: back   H: hint   Tab: reach V/H"
            )
        elif step.kind == "challenge":
            if self._challenge_passed:
                text = "Passed! N: continue to the next step   B/Esc: back"
            else:
                text = (
                    "Type assembly; Enter/Ctrl+Enter: verify   Ctrl+N: skip   "
                    "Esc: back   Tab: reach V/H"
                )
        elif step.options:
            text = "Pick 1-9 to answer   H: hint   R: run   V: views   B/Esc: back"
        else:
            text = "N/Enter: next step   R: run   H: hint   V: views   B/Esc: back"
        self.query_one(".hint").update(progress + "   " + text)

    def _progress_bar(self) -> str:
        total = len(self.session.lesson.steps)
        filled = self.session.index
        width = 24
        done = int((filled / total) * width) if total else 0
        bar = "\u25A0" * done + "\u25A1" * (width - done)
        return f"[bold]{filled}/{total}[/bold] {bar}"

    def _ensure_program_state(self) -> None:
        step = self._current()
        if not step.program or self._ran:
            return
        if step.kind in ("prediction", "response", "challenge"):
            self.session.load_program()
            return
        self._run_program()

    def _run_program(self) -> None:
        self.session.load_program()
        before = self.session.executor.snapshot()
        self.session.executor.run()
        self._ran = True
        self._step_diff = explain_diff(before, self.session.executor.snapshot())

    def _update_views(self) -> None:
        step = self._current()
        if not step.program:
            state_text = "(no program on this step)"
        else:
            self._ensure_program_state()
            state_text = self.session.three_views()["state"]
            if self._step_diff:
                state_text += f"\n\nchanged: {self._step_diff}"
            state_text += f"\nstatus: {self._friendly_status()}"
        views = self.session.three_views()
        source = views["source"] or step.content
        asm = views["assembly"] or "(no program)"
        self.query_one("#view-source").update(f"[b]SOURCE[/b]\n{source}")
        self.query_one("#view-asm").update(f"[b]ASSEMBLY[/b]\n{asm}")
        self.query_one("#view-state").update(f"[b]STATE[/b]\n{state_text}")

    def _friendly_status(self) -> str:
        ex = self.session.executor
        if ex.exit_code is not None:
            return f"exited (code {ex.exit_code})"
        if ex.status in ("halted", "error"):
            return "executed to the end (no exit syscall)"
        return ex.status

    def _step_hint(self) -> str:
        step = self._current()
        if step.hint:
            return step.hint
        if step.kind == "challenge":
            return f"A passing solution looks like:\n{step.program}"
        if step.expected:
            parts = []
            for reg, value in step.expected.get("registers", {}).items():
                parts.append(f"{reg} = {value:#x}")
            for flag, value in step.expected.get("flags", {}).items():
                parts.append(f"{flag.upper()} = {int(bool(value))}")
            return "Target end state: " + ", ".join(parts)
        if step.options:
            if step.program:
                return (
                    "One of the listed options is correct — re-read the example above, "
                    "then press R to watch the machine state."
                )
            return "One of the listed options is correct — re-read the definition above."
        if step.program:
            return "Press R to run the program and watch the STATE panel update."
        return (
            f"This is a {step.kind} step — restate the key idea in your own words; "
            "the answer follows directly from the definition above."
        )

    def action_show_hint(self) -> None:
        self._feedback = f"hint: {self._step_hint()}"
        self._render_view()

    def on_key(self, event) -> None:
        if self.focused is not None and self.focused.id == "lesson-input":
            return
        if self._current().options and event.key in "123456789":
            self._choose(int(event.key) - 1)
            event.stop()

    def _choose(self, option_index: int) -> None:
        step = self._current()
        if option_index >= len(step.options):
            return
        self._challenge_passed = False
        feedback = self.session.respond(option_index)
        correct = step.answer is not None and option_index == step.answer
        if step.answer is not None:
            self._state.record_attempt(
                f"{self.session.lesson.id}.step{self.session.index}",
                step.kind,
                correct,
            )
        self._feedback = feedback
        self._render_view()
        if step.answer is not None:
            if correct:
                self.app.notify("Correct!", severity="success")
            else:
                self.app.notify("Not quite — press H for a hint.", severity="warning")

    def action_run_program(self) -> None:
        step = self._current()
        if not step.program:
            self._feedback = "This step has no program to run."
            self._render_view()
            return
        self._run_program()
        output = (
            f"   output: {self.session.executor.output!r}"
            if self.session.executor.output
            else ""
        )
        self._feedback = f"status: {self._friendly_status()}{output}"
        self._state.achievements.check_event("program_run")
        self._render_view()

    def action_run_response(self, answer_text: str = "") -> None:
        step = self._current()
        passed, message = self.session.respond_text(answer_text)
        self._state.record_attempt(
            f"{self.session.lesson.id}.step{self.session.index}",
            step.kind,
            passed,
        )
        self._feedback = f"{'CHECKED' if passed else 'NEEDS WORK'} — {message}"
        self._response_passed = passed
        self._render_view()
        if passed:
            self.app.notify("Good answer!", severity="success")
            self.query_one("#lesson-input").blur()
        else:
            self.app.notify("Almost — add the missing ideas, then retry.", severity="warning")

    def action_run_challenge(self) -> None:
        step = self._current()
        if step.kind != "challenge":
            self._feedback = (
                "Verify only works on challenge steps — press N to reach the challenge."
            )
            self.app.notify("Verify only works on challenge steps", severity="warning")
            self._render_view()
            return
        submission = self.query_one("#lesson-input").value
        if not submission.strip():
            self._feedback = (
                "Type a solution first. Write assembly instructions (e.g. 'mov rax, 5') "
                "or, if the exercise asks for a value, just type that value — both work."
            )
            self.app.notify(
                "Type an answer: assembly (mov rax, 5) or just the value (5)",
                severity="error",
            )
            self._render_view()
            return
        try:
            passed, message = self.session.verify_challenge(submission)
        except Exception as exc:  # assembly/emulation errors must never crash the TUI
            self._feedback = f"error: {exc}"
            self.app.notify(f"Could not assemble or run your code: {exc}", severity="error")
            self._render_view()
            return
        self._feedback = f"{'PASSED' if passed else 'FAILED'} — {message}"
        self._challenge_passed = passed
        self._state.record_attempt(
            f"{self.session.lesson.id}.challenge",
            self.session.lesson.module,
            passed,
        )
        self._render_view()
        if passed:
            self.app.notify("Challenge passed!", severity="success")
            self._state.achievements.check_event("challenge_complete", {"count": 1})
            self.query_one("#lesson-input").blur()
        else:
            self._feedback += (
                "\nNot quite — fix your code and press Enter to retry. "
                "Press H for a hint."
            )
            self.app.notify(
                "Not quite — fix your code and retry (H for a hint).",
                severity="warning",
            )
            self.query_one("#lesson-input").focus()
        self._update_hint()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        step = self._current()
        if step.kind == "response":
            self.action_run_response(event.value)
        else:
            self.action_run_challenge()
        event.input.value = ""

    def action_toggle_views(self) -> None:
        self._show_views = not self._show_views
        self.query_one("#views").display = self._show_views
        if self._show_views:
            self._update_views()
        self._render_view()

    def action_toggle_cheatsheet(self) -> None:
        self._show_cheatsheet = not self._show_cheatsheet
        self._render_view()

    def action_advance(self) -> None:
        self._feedback = ""
        self._challenge_passed = False
        self._response_passed = False
        if self.session.advance() is None:
            if self._complete:
                self._goto_next_lesson()
                return
            self._complete = True
            self._state.mark_lesson_complete(
                self.session.lesson.id, self.session.lesson.module
            )
            self._state.clear_lesson_position(self.session.lesson.id)
            self._feedback = (
                f"Lesson '{self.session.lesson.title}' complete. "
                f"Press Enter to continue to the next lesson, B to go back."
            )
            self.app.notify(
                f"Lesson complete: {self.session.lesson.title}",
                title="Completed",
                severity="success",
            )
        else:
            self._state.save_lesson_position(
                self.session.lesson.id, self.session.index
            )
        self._render_view()

    def _goto_next_lesson(self) -> None:
        module = get_module(self.session.lesson.module)
        next_lesson = None
        if module is not None:
            lessons = module.lessons
            for i, lesson in enumerate(lessons):
                if lesson.id == self.session.lesson.id and i + 1 < len(lessons):
                    next_lesson = lessons[i + 1]
                    break
        if next_lesson is not None:
            self.app.switch_screen(LessonScreen(next_lesson, self._state))
        else:
            self.app.pop_screen()


def _normalize(text: str) -> str:
    return "".join(ch for ch in text.lower() if ch.isalnum())


def _find_lesson(state, keyword: str):
    """Find a lesson by id-or-title keyword across builtin + user modules."""
    try:
        user_modules = LearnScreen._user_modules(state)
    except Exception:
        user_modules = []
    haystack = list(all_modules()) + list(user_modules)
    kw = _normalize(keyword)
    for module in haystack:
        for lesson in module.lessons:
            if kw in _normalize(lesson.id) or kw in _normalize(lesson.title):
                return lesson
    return None


def _challenge_from_dict(data) -> Optional[Challenge]:
    """Convert a persisted user-authored challenge dict back to a Challenge."""
    if not isinstance(data, dict):
        return None
    return Challenge(
        id=str(data.get("id", f"user_{id(data)}")),
        challenge_type=data.get("challenge_type", "registers"),
        difficulty=data.get("difficulty", "easy"),
        title=data.get("title", "Untitled"),
        spec=data.get("spec", ""),
        program=data.get("program", ""),
        expected=data.get("expected", {}) or {},
        hints=data.get("hints", []) or [],
        solution=data.get("solution", ""),
        flag=data.get("flag", ""),
    )


class ChallengeListScreen(Screen):
    """Challenges and Practice share this list; each entry opens a runner."""

    BINDINGS = [Binding("a", "create_challenge", "Add content")] + BACK_BINDINGS

    def __init__(
        self,
        title: str,
        challenges: Optional[List[Challenge]] = None,
        mode: str = "training",
    ) -> None:
        super().__init__()
        self._title = title
        self._mode = mode
        self._challenges = (
            challenges if challenges is not None else self._builtin_challenges()
        )

    def _builtin_challenges(self) -> List[Challenge]:
        if self._mode == "ctf":
            return ctf_challenges()
        return sample_challenges()

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Static(self._title, id="challenge-title")
        yield ListView(id="challenge-list")
        yield Static(
            "Enter: attempt   A: add your own content   B/Esc: back", classes="hint"
        )
        yield Footer()

    def on_mount(self) -> None:
        self.load_list()

    def _all_challenges(self) -> List[Challenge]:
        challenges = list(self._challenges)
        try:
            user_dicts = self.app.state.user_content.challenge_dicts()
        except Exception:
            user_dicts = []
        for data in user_dicts:
            converted = _challenge_from_dict(data)
            if converted is None:
                continue
            if self._mode == "ctf":
                if converted.challenge_type not in (
                    "mini_ctf",
                    "reverse_engineering",
                    "patching",
                    "debugging",
                ):
                    continue
            else:
                if converted.challenge_type in (
                    "mini_ctf",
                    "reverse_engineering",
                    "patching",
                ):
                    continue
            challenges.append(converted)
        return challenges

    def load_list(self) -> None:
        list_view = self.query_one("#challenge-list")
        list_view.clear()
        for c in self._all_challenges():
            list_view.append(
                ListItem(
                    Label(f"{c.difficulty:6s} {c.title:34s} [{c.challenge_type}]")
                )
            )

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        challenge = self._all_challenges()[event.list_view.index]
        self.app.push_screen(ChallengeScreen(challenge, self.app.state))

    def action_create_challenge(self) -> None:
        from academy.ui.authoring import AddContentScreen

        mode = "challenge" if self._mode == "ctf" else "practice"
        self.app.push_screen(AddContentScreen(self, self.app.state, mode=mode))


class ChallengeScreen(Screen):
    BINDINGS = [
        Binding("h", "hint", "Hint"),
        Binding("v", "solution", "Solution"),
        Binding("d", "launch_debugger", "Debug"),
        Binding("?", "help", "Help"),
        Binding("g", "grade", "Grade"),
        Binding("l", "open_lesson", "Relearn"),
    ] + BACK_BINDINGS

    def __init__(self, challenge: Challenge, state) -> None:
        super().__init__()
        self.challenge = challenge
        self._state = state
        self._hints_used = 0
        self._result = None
        self._hint_engine = HintEngine()
        self._solved = False

    def action_launch_debugger(self) -> None:
        program = self.challenge.program or ""
        self.app.push_screen(DebuggerScreen(program=program))

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Static("", id="challenge-spec")
        yield Static("", id="challenge-hints")
        yield CodeArea(
            placeholder="write your assembly submission, then press Ctrl+Enter",
            id="challenge-input",
        )
        yield Static("", id="challenge-result")
        yield Static(
            "H: hint  V: solution  D: debug  ?: help  G/Ctrl+Enter: grade",
            classes="hint",
        )
        yield Footer()

    def on_mount(self) -> None:
        self._render_spec()

    def _render_spec(self) -> None:
        flag_note = (
            "\n\n[b]flag:[/b] reveals when you pass"
            if self.challenge.flag
            else ""
        )
        text = (
            f"[b]{self.challenge.difficulty} / {self.challenge.challenge_type}[/b]\n\n"
            f"{self.challenge.spec}\n{flag_note}\n\n"
            f"reference:\n{self.challenge.program}"
        )
        self.query_one("#challenge-spec").update(text)
        self.query_one("#challenge-hints").update("")
        self.query_one("#challenge-result").update("")

    def _help_text(self) -> str:
        lines = [
            "HOW TO SOLVE THIS EXERCISE",
            "1. Understand the goal in the spec above (target registers/flags/output).",
            "2. Write assembly that reaches that end-state; end with a clean "
            "exit syscall (mov rax, 60; mov rdi, 0; syscall) if you like.",
            "3. Press Ctrl+Enter (or G) to grade — you get instant feedback.",
            "4. Wrong? Fix your code and re-grade as many times as you like. "
            "Each hint (H) costs points.",
            "5. When you pass, a green toast confirms it and the solve is "
            "registered (and may unlock an achievement).",
            "",
            "You can also press D to load this into the debugger and step "
            "through it, or press R on a hint to see the reference, then adapt it.",
        ]
        return "\n".join(lines)

    def action_help(self) -> None:
        self.query_one("#challenge-hints").update(self._help_text())

    def action_solution(self) -> None:
        solution = (self.challenge.solution or "").strip()
        if not solution:
            self.query_one("#challenge-hints").update(
                "No step-by-step solution is written for this one yet.\n"
                "Hint: use the 'Author & Create' wizard and fill its solution field."
            )
            return
        lines = ["[bold]STEP-BY-STEP SOLUTION[/bold]", ""]
        for i, step in enumerate(solution.split("\\n"), 1):
            if step.strip():
                lines.append(f"  {i}. {step.strip()}")
        self.query_one("#challenge-hints").update("\n".join(lines))

    def on_key(self, event) -> None:
        if event.key == "?":
            self.action_help()
            event.stop()

    def action_hint(self) -> None:
        self._hints_used += 1
        hints = self._hint_engine.hints_for(self.challenge, self._hints_used)
        if not hints:
            self._hints_used -= 1
            return
        failures = sum(
            1 for a in self._state.tracker.attempts
            if a.item_id == self.challenge.id and not a.correct
        )
        penalty = self._hint_engine.penalty(self._hints_used, failures)
        text = "\n".join(f"  {i + 1}. {hint}" for i, hint in enumerate(hints))
        self.query_one("#challenge-hints").update(
            f"hint level {self._hints_used} (penalty {penalty} points, "
            f"{failures} prior failures):\n{text}"
        )

    def _grade(self, submission: str) -> None:
        grade = Grader().grade(self.challenge, submission, hints_used=self._hints_used)
        self._result = grade
        self._state.record_attempt(
            self.challenge.id,
            self.challenge.challenge_type,
            grade.passed,
            hints_used=self._hints_used,
        )
        if grade.passed:
            self._state.achievements.check_event(
                "challenge_complete", {"count": 1}
            )
            if not self._solved:
                self._solved = True
                msg = f"Solved: {self.challenge.title}  ({grade.total}/100)"
                if self.challenge.flag:
                    msg += f"  flag: {self.challenge.flag}"
                self.app.notify(
                    msg,
                    title="Practice complete",
                    severity="success",
                )
        self.query_one("#challenge-result").update(self._format_review(grade))
        self.query_one("#challenge-hints").update("")

    def _open_lesson(self) -> None:
        if not self._result:
            self.query_one("#challenge-hints").update(
                "Grade your answer first (G) — the review then links to the "
                "exact lesson to re-learn."
            )
            return
        keyword = (self._result.related_lessons or [None])[0]
        target = None
        if keyword:
            target = _find_lesson(self._state, keyword)
        if target is None:
            self.query_one("#challenge-hints").update(
                "Could not find a matching lesson for this topic. "
                "Re-read the spec and the reference program above."
            )
            return
        self.app.push_screen(LessonScreen(target, self._state))

    def action_open_lesson(self) -> None:
        self._open_lesson()

    def _format_review(self, grade) -> str:
        verdict = (
            "[green]PASSED[/green]" if grade.passed else "[red]NOT YET[/red]"
        )
        lines = [
            f"total: [b]{grade.total:.0f}/100[/b]   status: {verdict}",
            f"correctness {grade.correctness:.0%}  efficiency {grade.efficiency:.0%}",
            "",
            "what to fix:",
        ]
        lines += [f"  - {f}" for f in grade.feedback] or ["  - (none)"]
        lines.append("")
        lines.append("structured review + what to re-learn:")
        lines += [f"  · {r}" for r in grade.review]
        lines.append("")
        lines.append("tip: press ? for how-to, H for a hint, L to open the linked "
                     "lesson, and re-grade freely until green.")
        return "\n".join(lines)

    def action_grade(self) -> None:
        self._grade(self.query_one("#challenge-input").value)

    def on_input_submitted(self, event: Input.Submitted) -> None:
        self._grade(event.value)
        event.input.value = ""


class ChallengesScreen(ChallengeListScreen):
    def __init__(self) -> None:
        super().__init__("CTF & Crackmes", mode="ctf")


class PracticeScreen(ChallengeListScreen):
    def __init__(self) -> None:
        super().__init__("Practice", mode="training")


class SandboxScreen(Screen):
    BINDINGS = [
        Binding("?", "help", "Help"),
        Binding("z", "rewind", "Rewind"),
    ] + BACK_BINDINGS

    def __init__(self) -> None:
        super().__init__()
        self.sandbox = Sandbox()
        self.sandbox.executor.load_asm(DEFAULT_PROGRAM)

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Vertical(id="sandbox-root"):
            with Horizontal(id="panels"):
                yield Static("(code)", id="code-panel", classes="panel")
                yield Static("(registers)", id="registers-panel", classes="panel")
                yield Static("(flags)", id="flags-panel", classes="panel")
                yield Static("(memory)", id="memory-panel", classes="panel")
                yield Static("(stack)", id="stack-panel", classes="panel")
                yield Static("(output)", id="output-panel", classes="panel")
            yield Input(
                placeholder=(
                    "type a command (help lists them), e.g. run, step, registers, "
                    "memory 0x600000 16"
                ),
                id="cmd",
            )
        yield Static("? : how-to   type help in the box for commands   B/Esc: back", classes="hint")
        yield Footer()

    def on_mount(self) -> None:
        self.refresh_views()
        self.query_one("#output-panel").update(_SANDBOX_TUTORIAL)
        self.query_one("#cmd").focus()

    def action_help(self) -> None:
        self.query_one("#output-panel").update(_SANDBOX_TUTORIAL)

    def action_rewind(self) -> None:
        self.handle_command("rewind")
        self.query_one("#cmd").focus()

    def on_key(self, event) -> None:
        if event.key == "?":
            self.action_help()
            event.stop()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        try:
            self.handle_command(event.value)
        except (ValueError, IndexError) as exc:
            self.query_one("#output-panel").update(f"error: {exc}")
        event.input.value = ""
        self.query_one("#cmd").focus()

    def handle_command(self, cmdline: str) -> CommandResult:
        result = self.sandbox.execute(cmdline)
        text = result.text
        if result.explanation:
            text += "\n\n" + result.explanation
        self.query_one("#output-panel").update(text)
        self.refresh_views()
        return result

    def refresh_views(self) -> None:
        executor = self.sandbox.executor
        self.query_one("#code-panel").update(self._code_view())
        self.query_one("#registers-panel").update(format_registers(executor.registers()))
        self.query_one("#flags-panel").update(format_flags(executor.flags()))
        self.query_one("#memory-panel").update(self._memory_view())
        self.query_one("#stack-panel").update(self._stack_view())

    def _code_view(self) -> str:
        lines = self.sandbox.executor.disassemble(count=12)
        return "\n".join(lines) if lines else "(no code loaded)"

    def _memory_view(self) -> str:
        try:
            data = self.sandbox.executor.read_memory("data", 48)
        except Exception:
            return "(data segment unreadable)"
        return hexdump(data, base=self.sandbox.executor.segment_base("data"), width=8)

    def _stack_view(self) -> str:
        rows = self.sandbox.executor.stack_view(8)
        return "\n".join(f"{addr:016x}  {data.hex()}" for addr, data in rows)


class DebuggerScreen(Screen):
    BINDINGS = [
        Binding("f", "step_into", "Step into"),
        Binding("o", "step_over", "Step over"),
        Binding("t", "step_out", "Step out"),
        Binding("c", "continue", "Continue"),
        Binding("r", "reset", "Reset"),
        Binding("?", "help", "Help"),
    ] + BACK_BINDINGS

    def __init__(self, program: Optional[str] = None) -> None:
        super().__init__()
        self.debugger = Debugger()
        self.debugger.load_asm(program if program is not None else DEFAULT_DEBUG_PROGRAM)

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Static("", id="debug-status")
        with Horizontal(id="debug-panels"):
            yield Static("(code)", id="debug-code", classes="panel")
            yield Static("(registers)", id="debug-registers", classes="panel")
            yield Static("(flags)", id="debug-flags", classes="panel")
            yield Static("(stack)", id="debug-stack", classes="panel")
        yield Static("F: into  O: over  T: out  C: continue  R: reset  ?: how-to", classes="hint")
        yield Footer()

    def on_mount(self) -> None:
        self.query_one("#debug-status").update(_DEBUGGER_TUTORIAL)
        self._refresh()

    def action_help(self) -> None:
        self.query_one("#debug-status").update(_DEBUGGER_TUTORIAL)
        self._refresh()

    def _refresh(self) -> None:
        ex = self.debugger.executor
        self.query_one("#debug-code").update(self._code_view())
        self.query_one("#debug-registers").update(format_registers(ex.registers()))
        self.query_one("#debug-flags").update(format_flags(ex.flags()))
        self.query_one("#debug-stack").update(self._stack_view())

    def _code_view(self) -> str:
        lines = self.debugger.executor.disassemble(count=14)
        return "\n".join(lines) if lines else "(no code)"

    def _stack_view(self) -> str:
        rows = self.debugger.executor.stack_view(8)
        return "\n".join(f"{addr:016x}  {data.hex()}" for addr, data in rows)

    def _run_action(self, message: str) -> None:
        self.query_one("#debug-status").update(message)
        self._refresh()

    def action_step_into(self) -> None:
        self._run_action(self.debugger.step_into())

    def action_step_over(self) -> None:
        self._run_action(self.debugger.step_over())

    def action_step_out(self) -> None:
        self._run_action(self.debugger.step_out())

    def action_continue(self) -> None:
        self._run_action(self.debugger.continue_run())

    def action_reset(self) -> None:
        self.debugger.executor.reset()
        self._run_action("reset complete")


class ProjectsScreen(Screen):
    BINDINGS = BACK_BINDINGS

    def __init__(self) -> None:
        super().__init__()
        self._pack = default_mission_pack()
        self._missions = self._pack.campaign()

    def _completed(self) -> set:
        try:
            progress = self.app.state.session.load_progress()
        except Exception:
            return set()
        return set((progress.get("missions") or {}).keys())

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Static("The Dungeon of the Machine — story campaign", id="missions-title")
        yield ListView(*self._render_items(), id="missions-list")
        yield Static(
            "Enter to open a chapter. Each must be cleared to unlock the next.",
            classes="hint",
        )
        yield Footer()

    def _render_items(self):
        completed = self._completed()
        items = []
        for m in self._missions:
            done = m.mission_id in completed
            locked = m.requires is not None and m.requires not in completed
            if locked:
                glyph = "[red]LOCK[/red]"
            elif done:
                glyph = "[green]done[/green]"
            else:
                glyph = "[yellow]->[/yellow]"
            items.append(ListItem(Label(f"{glyph}  {m.title}  ({m.difficulty})")))
        return items

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        mission = self._missions[event.list_view.index]
        self.app.push_screen(MissionScreen(mission, self.app.state))


class MissionScreen(Screen):
    BINDINGS = [
        Binding("v", "verify", "Verify"),
        Binding("a", "auto", "Auto-run"),
        Binding("g", "grade", "Grade"),
        Binding("h", "hint", "Hint"),
    ] + BACK_BINDINGS

    def __init__(self, mission, state) -> None:
        super().__init__()
        self.mission = mission
        self._state = state
        self._hint_engine = HintEngine()
        self._hints_used = 0

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Static("", id="mission-body")
        yield CodeArea(
            placeholder="enter your answer (or press A to auto-run for this mission)",
            id="mission-input",
        )
        yield Static("", id="mission-result")
        yield Static(
            "V: verify   A: auto-run   G: grade   H: hint   ?: help",
            classes="hint",
        )
        yield Footer()

    def _has_challenge(self) -> bool:
        return self.mission.challenge is not None and bool(
            (self.mission.challenge.program or "").strip()
        )

    def _is_locked(self) -> bool:
        req = self.mission.requires
        if not req:
            return False
        try:
            progress = self._state.session.load_progress()
        except Exception:
            return True
        return req not in (progress.get("missions") or {})

    def on_mount(self) -> None:
        body = (
            f"{self.mission.title}  (difficulty {self.mission.difficulty})\n\n"
            f"{self.mission.story}\n\nobjective:\n{self.mission.objective}"
        )
        if self._has_challenge():
            body += (
                "\n\nchallenge:\n"
                f"{self.mission.challenge.spec}"
            )
            self.query_one("#mission-input").placeholder = (
                "write your assembly, then press G (or Ctrl+Enter) to grade"
            )
        self.query_one("#mission-body").update(body)
        if self._is_locked():
            self.query_one("#mission-result").update(
                "[red]LOCKED — clear the previous chapter first.[/red]"
            )
        else:
            self.query_one("#mission-result").update("")

    def action_hint(self) -> None:
        if self._is_locked():
            self.query_one("#mission-result").update(
                "[red]LOCKED — clear the previous chapter first.[/red]"
            )
            return
        if not self._has_challenge():
            self.query_one("#mission-result").update(
                "No separate hint for this chapter — re-read the objective or use "
                "A to auto-run the lab."
            )
            return
        challenge = self.mission.challenge
        self._hints_used += 1
        failures = sum(
            1 for a in self._state.tracker.attempts
            if a.item_id == self.mission.mission_id and not a.correct
        )
        penalty = HintEngine().penalty(self._hints_used, failures)
        lines = [
            f"hint level {self._hints_used} (grade penalty {penalty} points, "
            f"{failures} prior failures)",
            "",
        ]
        hints = HintEngine().hints_for(challenge, self._hints_used)
        lines += [f"  · {h}" for h in hints]
        lines.append("")
        if self._hints_used >= 3:
            lines.append("")
            lines.append(f"one working reference:\n{challenge.program}")
            if challenge.solution:
                lines.append(f"\naim to end with:\n{challenge.solution}")
        self.query_one("#mission-result").update("\n".join(lines))

    def action_grade(self) -> None:
        if self._is_locked():
            self.query_one("#mission-result").update(
                "[red]LOCKED — clear the previous chapter first.[/red]"
            )
            return
        if not self._has_challenge():
            self.query_one("#mission-result").update(
                "No graded assembly challenge on this chapter — use V to verify "
                "your text answer or A to auto-run the lab."
            )
            return
        submission = self.query_one("#mission-input").value
        grade = Grader().grade(
            self.mission.challenge, submission, hints_used=self._hints_used
        )
        verdict = (
            "[green]PASSED[/green]" if grade.passed else "[red]NOT YET[/red]"
        )
        lines = [
            f"challenge grade: {grade.total:.0f}/100   status: {verdict}",
            f"correctness {grade.correctness:.0%}  efficiency {grade.efficiency:.0%}",
            "",
            "what to fix:",
        ]
        lines += [f"  - {f}" for f in grade.feedback] or ["  - (none)"]
        lines.append("")
        lines += [f"  · {r}" for r in grade.review]
        if grade.passed:
            self._mark_progress()
            self._state.achievements.check_event("challenge_complete", {"count": 1})
            self.app.notify(
                f"{self.mission.title} — challenge solved!",
                severity="success",
            )
        self.query_one("#mission-result").update("\n".join(lines))

    def on_input_submitted(self, event) -> None:
        if self._has_challenge():
            self.action_grade()
        else:
            self._verify(event.value)
        event.input.value = ""

    def action_verify(self) -> None:
        self._verify(self.query_one("#mission-input").value)

    def _mark_progress(self) -> None:
        try:
            progress = self._state.session.load_progress()
        except Exception:
            progress = {}
        progress.setdefault("missions", {})[self.mission.mission_id] = "complete"
        self._state.session.save_progress(progress)

    def _verify(self, answer_text: str) -> None:
        if self._is_locked():
            self.query_one("#mission-result").update(
                "[red]LOCKED — clear the previous chapter first.[/red]"
            )
            return
        answer, autofail = self._parse_answer(answer_text)
        passed = self.mission.complete(answer)
        if passed:
            self._mark_progress()
            self._state.achievements.check_event("binary_analyzed")
            suffix = ""
            if self.mission.mission_id == "extract_flag":
                from academy.sandbox.toy import CAMPAIGN_FLAG

                suffix = f"\n\n[green]FLAG CAPTURED: {CAMPAIGN_FLAG}[/green]"
            result = f"PASSED — {self.mission.title} complete!" + suffix
        else:
            result = "FAILED — answer did not verify."
        if autofail:
            result = "That mission must be auto-run (press A) — no text answer is used."
        self.query_one("#mission-result").update(result)

    def _parse_answer(self, answer_text: str):
        mission_id = self.mission.mission_id
        text = answer_text.strip()
        if mission_id == "recover_password":
            return text.encode(), False
        if mission_id == "extract_flag":
            return text.encode(), False
        return text, False

    def action_auto(self) -> None:
        from academy.sandbox.patching import PatchingLab
        from academy.sandbox.re import ReverseEngineeringLab
        from academy.sandbox.toy import (
            CAMPAIGN_FLAG,
            build_flag_vault,
            build_function_sample,
            build_license_check,
        )

        if self._is_locked():
            self.query_one("#mission-result").update(
                "[red]LOCKED — clear the previous chapter first.[/red]"
            )
            return
        mission_id = self.mission.mission_id
        if mission_id == "patch_license":
            binary = build_license_check()
            patched = PatchingLab().flip_jump(binary.code, "je")
            ok, message = PatchingLab().verify(binary, patched)
            result = f"patched & verified: {message}"
            self._mark_progress()
        elif mission_id == "map_functions":
            result_obj = ReverseEngineeringLab().analyze(build_function_sample())
            result_text = (
                f"{len(result_obj.functions)} function(s): "
                + ", ".join(f"{f.start:08x}" for f in result_obj.functions)
            )
            self.mission.complete(
                {
                    "count": len(result_obj.functions),
                    "starts": [f.start for f in result_obj.functions],
                }
            )
            result = f"analysis: {result_text}"
            self._mark_progress()
        elif mission_id == "extract_flag":
            result_obj = ReverseEngineeringLab().analyze(build_flag_vault())
            strings = ", ".join(result_obj.strings)
            self.mission.complete(CAMPAIGN_FLAG.encode("ascii"))
            result = (
                f"vault ran — strings found: {strings}\n"
                f"[green]FLAG CAPTURED: {CAMPAIGN_FLAG}[/green]"
            )
            self._mark_progress()
        else:
            result = (
                "Auto analysis of the password check narrows it to one constant. "
                "Type Zx9!kq as your answer and press V."
            )
        if mission_id not in ("recover_password",):
            self._state.achievements.check_event("binary_analyzed")
        self.query_one("#mission-result").update(result)


class NotebookScreen(Screen):
    BINDINGS = [
        Binding("v", "view_entry", "View"),
        Binding("d", "delete_entry", "Delete"),
        Binding("n", "new_entry", "New"),
    ] + BACK_BINDINGS

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Vertical(id="notebook-root"):
            yield ListView(id="notebook-list")
            yield Static("(details)", id="notebook-detail")
            yield Input(
                placeholder='add: kind|title|content   e.g. note|MOV semantics|mov rax,5',
                id="notebook-input",
            )
        yield Static("V: view  D: delete  N: new  Enter: add", classes="hint")
        yield Footer()

    def on_mount(self) -> None:
        self._render_list()

    @property
    def _state(self):
        return self.app.state

    def _render_list(self) -> None:
        entries = self._state.notebook.entries()
        self.query_one("#notebook-list").clear()
        for entry in entries:
            self.query_one("#notebook-list").append(
                ListItem(Label(f"{entry.kind:9s} {entry.title}  ({entry.entry_id})"))
            )
        if not entries:
            self.query_one("#notebook-list").append(ListItem(Label("(empty)")))
        self.query_one("#notebook-detail").update(
            f"{len(entries)} entries. Use N to add a note/code/bookmark."
        )

    def _selected(self):
        entries = self._state.notebook.entries()
        list_view = self.query_one("#notebook-list")
        if not entries or list_view.index is None or list_view.index >= len(entries):
            return None
        return entries[list_view.index]

    def action_new_entry(self) -> None:
        self.query_one("#notebook-input").focus()

    def action_view_entry(self) -> None:
        entry = self._selected()
        if entry is None:
            return
        self.query_one("#notebook-detail").update(
            f"{entry.kind}: {entry.title}\n{entry.content}"
        )

    def action_delete_entry(self) -> None:
        entry = self._selected()
        if entry is not None:
            self._state.notebook.delete(entry.entry_id)
        self._render_list()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        parts = [p.strip() for p in event.value.split("|", 2)]
        try:
            if len(parts) == 3:
                kind, title, content = parts
            elif len(parts) == 2:
                kind, title = parts
                content = ""
            else:
                raise ValueError("use: kind|title|content")
            entry = self._state.notebook.add(kind, title, content)
            self.query_one("#notebook-detail").update(
                f"added {kind} '{title}' ({entry.entry_id})"
            )
        except ValueError as exc:
            self.query_one("#notebook-detail").update(f"error: {exc}")
        event.input.value = ""
        self._render_list()


class ProfileScreen(Screen):
    """Gamification profile: XP, level, streaks, and badges."""

    BINDINGS = [Binding("r", "refresh", "Refresh")] + BACK_BINDINGS

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Static("", id="profile-body")
        yield Static("R: refresh   B/Esc: back", classes="hint")
        yield Footer()

    @property
    def _state(self):
        return self.app.state

    def on_mount(self) -> None:
        self._render_view()

    def action_refresh(self) -> None:
        self._render_view()

    def _render_view(self) -> None:
        stats = self._state.progress_summary()
        g = stats.get("gamification", {})
        lines = [
            "PROFILE",
            "--------",
            f"level:      [bold cyan]{g.get('level', 1)}[/bold cyan]",
            f"XP:         {g.get('xp', 0)}  (next level in {g.get('xp_to_next', 100)} XP)",
            f"streak:     {g.get('streak', 0)} days (best {g.get('best_streak', 0)})",
            f"accuracy:   {g.get('accuracy', 0)}% "
            f"({g.get('total_correct', 0)}/{g.get('total_attempts', 0)} correct)",
            "",
            "BADGES / ACHIEVEMENTS",
            "---------------------",
        ]
        achievements = self._state.achievements.unlocked()
        if achievements:
            lines.extend(f"  [green]✓[/green] {a.name} — {a.description}" for a in achievements)
        else:
            lines.append("  (none yet — solve exercises, run programs, analyze binaries)")
        lines.append("")
        lines.append("lessons complete: " + str(len(stats.get("lessons_complete", []))))
        lines += [f"  - {lesson}" for lesson in stats.get("lessons_complete", [])[:10]]
        self.query_one("#profile-body").update("\n".join(lines))


class ProgressScreen(Screen):
    BINDINGS = [Binding("r", "refresh", "Refresh")] + BACK_BINDINGS

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Static("", id="progress-body")
        yield Static("R: refresh", classes="hint")
        yield Footer()

    @property
    def _state(self):
        return self.app.state

    def on_mount(self) -> None:
        self._render_view()

    def _render_view(self) -> None:
        summary = self._state.progress_summary()
        lines = ["PROGRESS", "--------"]
        lessons = summary["lessons_complete"]
        lines.append(f"lessons complete: {len(lessons)}")
        lines.extend(f"  - {lesson}" for lesson in lessons[:8])
        lines.append("")
        lines.append("mastery:")
        mastery = summary["mastery"]
        for topic, value in sorted(mastery.items()):
            lines.append(f"  - {topic}: {value}%")
        lines.append("")
        lines.append("achievements:")
        achievements = summary["achievements"]
        lines.append("  " + (", ".join(achievements) if achievements else "(none yet)"))
        lines.append("")
        lines.append("recommendations:")
        lines.extend(f"  - {rec}" for rec in summary["recommendations"])
        lines.append("")
        lines.append("attempts logged: " + str(self._state.sqlite.count()))
        self.query_one("#progress-body").update("\n".join(lines))

    def action_refresh(self) -> None:
        self._render_view()


class SettingsScreen(Screen):
    # Don't auto-focus the profile-path Input on mount: it must not swallow
    # the D/C/E/I/P hotkeys. Press P (or Tab/click) to focus it for editing.
    AUTO_FOCUS: ClassVar[str | None] = ""

    BINDINGS = [
        Binding("d", "toggle_dark", "Dark mode"),
        Binding("c", "clear_state", "Clear state"),
        Binding("e", "export_profile", "Export"),
        Binding("i", "import_profile", "Import"),
        Binding("p", "focus_path", "Path"),
    ] + BACK_BINDINGS

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Static("", id="settings-body")
        yield Input(
            placeholder="profile file path (for E export / I import)",
            id="profile-path",
        )
        yield Static(
            "D: dark mode  C: clear state  E: export profile  I: import profile"
            "  P: edit path",
            classes="hint",
        )
        yield Footer()

    @property
    def _state(self):
        return self.app.state

    def on_mount(self) -> None:
        default = str(Path(self._state.data_dir) / "profile.json")
        self.query_one("#profile-path").value = default
        self._render_view()

    def action_focus_path(self) -> None:
        self.query_one("#profile-path").focus()

    def on_input_submitted(self, event) -> None:
        # Editing done: hand focus back so the settings hotkeys work again.
        self.query_one("#profile-path").blur()
        event.input.blur()

    def _path(self) -> Path:
        value = self.query_one("#profile-path").value.strip()
        return Path(value) if value else Path(self._state.data_dir) / "profile.json"

    def _render_view(self) -> None:
        text = (
            f"data directory: {self._state.data_dir}\n"
            f"dark mode: {self.app.current_theme.dark}\n\n"
            "The box below is the profile path used by E (export) and I (import). "
            "Press P to edit it.\n\n"
            "D toggles the color scheme; C erases saved JSON state "
            "(notebook, achievements, progress).\n"
            "E exports your full profile; I restores it from a JSON file."
        )
        self.query_one("#settings-body").update(text)

    def action_toggle_dark(self) -> None:
        if self.app.current_theme.dark:
            self.app.theme = "textual-light"
        else:
            self.app.theme = "archont-ink"
        self._render_view()

    def action_clear_state(self) -> None:
        self._state.clear_state()
        self._render_view()
        self.app.notify("Saved state cleared", severity="success")

    def action_export_profile(self) -> None:
        try:
            path = self._state.session.export_to(self._path())
            self.app.notify(f"Profile exported to {path}", severity="success")
        except Exception as exc:
            self.app.notify(f"Export failed: {exc}", severity="error")

    def action_import_profile(self) -> None:
        try:
            data = self._state.session.import_from(self._path())
            self.app.notify(
                f"Profile restored ({sum(1 for v in data.values() if v)} sections)",
                severity="success",
            )
        except Exception as exc:
            self.app.notify(f"Import failed: {exc}", severity="error")


def _fuzzy_score(query: str, text: str) -> int:
    """Return a score for how well ``query`` appears (subsequence) in ``text``.
    0 means no match (or empty query)."""
    if not query:
        return 1
    q = query.lower()
    t = text.lower()
    qi = 0
    score = 0
    last = -1
    for ti, ch in enumerate(t):
        if qi < len(q) and ch == q[qi]:
            score += 1 + (10 if ti == last + 1 else 0)
            last = ti
            qi += 1
        if qi == len(q):
            break
    return score if qi == len(q) else 0


class PaletteScreen(Screen):
    """Command palette (Ctrl+K): fuzzy-jump to any screen, lesson, challenge,
    or platform action without navigating the menus."""

    BINDINGS = [Binding("escape", "close", "Close")]

    def __init__(self, state) -> None:
        super().__init__()
        self._state = state
        self._entries: list = []
        self._filtered: list = []

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Static("Command palette — type to filter, Enter to jump", classes="hint")
        yield Input(
            placeholder="fuzzy search screens / lessons / challenges / actions",
            id="palette-input",
        )
        yield ListView(id="palette-list")
        yield Static("Esc/ctrl+k: close   Enter: jump", classes="hint")
        yield Footer()

    def _build_entries(self) -> None:
        entries = []
        for name, label in MENU_LABELS.items():
            if name == "quit":
                entries.append((label, "action", "app.quit"))
            elif name == "author":
                entries.append((label, "author", ""))
            else:
                entries.append((label, "screen", name))
        for module in all_modules():
            for lesson in module.lessons:
                entries.append((f"{module.title} › {lesson.title}", "lesson", lesson))
        try:
            user_modules = LearnScreen._user_modules(self._state)
            for module in user_modules:
                for lesson in module.lessons:
                    entries.append((f"{module.title} › {lesson.title}", "lesson", lesson))
        except Exception:
            pass
        for challenge in sample_challenges():
            entries.append((f"Practice › {challenge.title}", "challenge", challenge))
        for challenge in ctf_challenges():
            entries.append((f"CTF › {challenge.title}", "challenge", challenge))
        try:
            for data in self._state.user_content.challenge_dicts():
                converted = _challenge_from_dict(data)
                if converted is not None:
                    entries.append((f"User › {converted.title}", "challenge", converted))
        except Exception:
            pass
        self._entries = entries

    def on_mount(self) -> None:
        self._build_entries()
        self._filtered = list(self._entries)
        self._render_list()
        self.query_one("#palette-input").focus()

    def _render_list(self) -> None:
        list_view = self.query_one("#palette-list")
        list_view.clear()
        for label, kind, _payload in self._filtered[:50]:
            glyph = {
                "screen": ">",
                "lesson": "L",
                "challenge": "!",
                "author": "+",
                "quit": "x",
            }.get(kind, "?")
            list_view.append(ListItem(Label(f"[cyan]{glyph}[/cyan]  {label}")))
        list_view.index = 0

    def on_input_changed(self, event: Input.Changed) -> None:
        query = event.value
        scored = []
        for label, kind, payload in self._entries:
            score = _fuzzy_score(query, label)
            if score:
                scored.append((score, label, kind, payload))
        scored.sort(key=lambda s: (-s[0], s[1].lower()))
        self._filtered = [
            (label, kind, payload) for _score, label, kind, payload in scored
        ]
        self._render_list()

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        if not self._filtered:
            return
        label, kind, payload = self._filtered[event.list_view.index]
        self._jump(kind, payload)

    def _jump(self, kind: str, payload) -> None:
        if kind == "quit":
            self.app.exit()
            return
        self.app.pop_screen()
        if kind == "screen":
            self.app.push_screen(payload)
        elif kind == "author":
            from academy.ui.authoring import AuthorModeScreen

            self.app.push_screen(AuthorModeScreen(self._state))
        elif kind == "lesson":
            self.app.push_screen(LessonScreen(payload, self._state))
        elif kind == "challenge":
            self.app.push_screen(ChallengeScreen(payload, self._state))

    def action_close(self) -> None:
        self.app.pop_screen()
