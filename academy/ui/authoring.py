from __future__ import annotations

from pathlib import Path

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical
from textual.screen import Screen
from textual.widgets import Footer, Header, Input, Label, ListItem, ListView, Static

MODE_NAMES = ("practice", "challenge", "lesson")
KIND_NAMES = ("registers", "flags", "output", "mini_ctf")
STEP_KIND_NAMES = (
    "concept",
    "intuition",
    "analogy",
    "visualization",
    "example",
    "walkthrough",
    "prediction",
    "response",
    "feedback",
    "challenge",
    "reflection",
)

FIELD_PROMPTS = {
    "title": "title: what should it be called?",
    "spec": "spec: what should the learner accomplish?",
    "reg": "reg: a register to check as name:value (repeatable, empty to stop)",
    "asm": "asm: the reference assembly (use \\n for newlines)",
    "solution": "solution: step-by-step walkthrough text (use \\n for newlines)",
    "path": "path: absolute path to a .asm file to import (e.g. /home/you/thing.asm)",
    "flag": "flag: the exact flag string a solve is rewarded with (empty to skip)",
    "out": "out: expected program output as raw text (e.g. Hello!) — empty to skip",
    "kind": "kind: registers | flags | output | mini_ctf",
    "difficulty": "difficulty: easy | medium | hard | expert",
    "step": "step: KIND|body — add a lesson step (repeatable, empty to stop)",
    "prog": "prog: KIND|assembly — optional program for a step (empty to skip)",
}

MODE_GUIDE = {
    "practice": (
        "Adding a PRACTICE exercise. First you may import a .asm file by "
        "absolute path (or press Enter empty to type it by hand). Then: title, "
        "spec, registers, reference assembly, and an optional step-by-step "
        "solution. Example:\n"
        "  path  = /home/you/sum.asm   (or empty to type asm yourself)\n"
        "  title = Sum to 8\n  spec  = Leave the sum of 3 and 5 in RAX.\n"
        "  reg   = rax:8\n  asm   = mov rax, 3\\nadd rax, 5\n"
        "  solution = Load 3 into RAX\\nAdd 5 to RAX"
    ),
    "challenge": (
        "Adding a CHALLENGE (CTF / crackme). You may import a .asm file first, "
        "then: title, spec, registers, expected output, final flag, assembly, "
        "solution, kind, difficulty.\n"
        "  path  = /home/you/key.asm   (or empty to type asm yourself)\n"
        "  title = Serial key\n  spec  = Compute the accepted serial into RAX.\n"
        "  reg   = rax:16657\n  out   = Accepted (or empty)\n"
        "  flag  = ASM{my_flag_1234}   (or empty)\n"
        "  asm   = mov rax, 0x4242\\nxor rax, 0x1337\n"
        "  kind  = registers\n  difficulty = medium"
    ),
    "lesson": (
        "Adding a LESSON. Fields: title, then any number of steps, each with "
        "optional assembly. Steps follow the 11-step kinds:\n"
        "  concept intuition analogy visualization example walkthrough\n"
        "  prediction response feedback challenge reflection\n"
        "Example:\n"
        "  title = My lesson\n"
        "  step  = concept|A register is a tiny cell inside the CPU.\n"
        "  step  = challenge|Write assembly so RAX holds 7.\n"
        "  prog  = challenge|mov rax, 7\n"
        "Lesson steps can carry registers and assembly — use prog=KIND|asm to "
        "add a program, and add step=concept|... etc. to build the loop."
    ),
}


class AuthorModeScreen(Screen):
    BINDINGS = [
        Binding("b", "app.pop_screen", "Back"),
        Binding("escape", "app.pop_screen", "Back"),
    ]

    _GUIDE = {
        "practice": "A practice exercise: import a .asm file, then set the "
                    "spec, target registers, reference assembly and a "
                    "step-by-step solution.",
        "challenge": "A CTF/crackme: import a .asm file, set spec, the exact "
        "registers/flags/output to check, difficulty, a final flag, and a "
        "solution walkthrough.",
        "lesson": "A full lesson: give a title, then add any number of steps — "
        "each with content, an example program, and how every line affects "
        "the registers, ready to blend with the other topics in Learn.",
    }

    def __init__(self, state) -> None:
        super().__init__()
        self._state = state

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Static(
            "[bold]Author & Content — pick what to create[/bold]",
            id="author-pick-title",
        )
        yield ListView(
            *[ListItem(Label(label)) for label in self._labels()],
            id="author-mode-list",
        )
        yield Static("", id="author-mode-detail")
        yield Static(
            "Enter to pick   B/Esc: back",
            classes="hint",
        )
        yield Footer()

    def _labels(self) -> list:
        return ["[b]Add a practice[/b] — solve a target end-state",
                "[b]Add a challenge[/b] — CTF/crackme with flag",
                "[b]Add a lesson[/b] — multiple concept steps, then Learn"]

    def on_mount(self) -> None:
        self.query_one("#author-mode-detail").update(self.MODES["practice"])

    MODES = MODE_GUIDE

    def on_list_view_selected(self, event) -> None:
        index = event.list_view.index
        mode = MODE_NAMES[index]
        self.app.push_screen(AddContentScreen(self, self._state, mode=mode))


class AddContentScreen(Screen):
    BINDINGS = [
        Binding("m", "cycle_mode", "Mode"),
        Binding("?", "howto", "How-to"),
        Binding("ctrl+enter", "save", "Save"),
    ] + [
        Binding("b", "app.pop_screen", "Back"),
        Binding("escape", "app.pop_screen", "Back"),
    ]

    def __init__(self, parent, state, mode: str = "practice") -> None:
        super().__init__()
        self._parent = parent
        self._state = state
        if mode not in MODE_NAMES:
            mode = "practice"
        self._mode = mode
        self._fields: dict = {}

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Static("", id="author-title")
        with Vertical():
            yield Label("mode (M to change)", classes="field-label")
            yield Static("practice", id="mode-display", classes="field")
            yield Label("current fields", classes="field-label")
            yield Static("(none yet)", id="field-display", classes="field")
            yield Label("answer for the field above", classes="field-label")
            yield Input(placeholder="type your answer, then press Enter", id="author-input")
            yield Static("", id="author-status", classes="author-status")
        yield Static(
            "Enter: next field   M: change mode   ?: how-to   Ctrl+Enter: save   B: back",
            classes="hint",
        )
        yield Footer()

    def on_mount(self) -> None:
        self._reset_wizard()
        self.query_one("#author-input").focus()

    def _reset_wizard(self) -> None:
        self._fields = {}
        self._stage = self._field_order()[0]
        self._last_field = ""
        self._prog_queue: list = []
        self._current_prog_kind = ""
        self._render_mode()

    def _render_mode(self) -> None:
        self.query_one("#author-title").update(
            f"[bold]Add a {MODE_NAMES[MODE_NAMES.index(self._mode)]}[/bold] "
            f"(M to change to another kind)"
        )
        self.query_one("#mode-display").update(MODE_NAMES[MODE_NAMES.index(self._mode)].upper())
        self._render_field()

    def _field_order(self) -> list:
        if self._mode == "lesson":
            return ["title", "step"]
        if self._mode == "challenge":
            return [
                "path",
                "title",
                "spec",
                "reg",
                "out",
                "flag",
                "asm",
                "solution",
                "kind",
                "difficulty",
            ]
        return ["path", "title", "spec", "reg", "asm", "solution"]

    def _prompt(self) -> str:
        if self._mode == "lesson" and self._stage == "prog":
            return (
                f"prog: assembly for the '{self._current_prog_kind}' step "
                f"(empty to skip):"
            )
        return FIELD_PROMPTS[self._stage]

    def _render_field(self) -> None:
        self.query_one("#author-status").update(MODE_GUIDE[self._mode])
        display = self._format_fields()
        self.query_one("#field-display").update(display)
        input_widget = self.query_one("#author-input")
        input_widget.placeholder = self._prompt()
        input_widget.value = ""
        input_widget.focus()

    def _format_fields(self) -> str:
        if not self._fields:
            return "(none yet)"
        parts = []
        for key, value in self._fields.items():
            if key == "steps":
                parts.append(f"steps: {len(value)}")
            else:
                parts.append(f"{key}={value}")
        return "   ".join(parts)

    def _import_from_path(self, answer: str) -> None:
        if not answer:
            self._fields.setdefault("asm", "")
            self._stage = "title"
            self._render_field()
            return
        path = Path(answer.strip()).expanduser()
        if not path.is_absolute():
            self.query_one("#author-status").update(
                "import: that path isn't absolute. Type the full path, e.g. "
                "/home/you/thing.asm (or press Enter empty to skip importing)."
            )
            return
        if not path.exists():
            self.query_one("#author-status").update(
                f"import: no file at '{path}'. Check the path and retry, or "
                "press Enter empty to skip importing."
            )
            return
        if path.suffix.lower() not in (".asm", ".s", ".txt"):
            self.query_one("#author-status").update(
                f"import: '{path.name}' doesn't look like assembly (.asm/.s). "
                "Press Enter empty to skip, or point at a real assembly file."
            )
            return
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError as exc:
            self.query_one("#author-status").update(
                f"import: could not read '{path}': {exc}. Retry or skip."
            )
            return
        self._fields["asm"] = text
        self._fields["imported_from"] = str(path)
        self.query_one("#author-status").update(
            f"import: loaded {len(text.splitlines())} lines from '{path}'. "
            "Now answer the next fields — title/spec/registers/solution."
        )
        self._stage = "title"
        self._render_field()

    def on_key(self, event) -> None:
        if event.key == "enter":
            self._advance_field(self.query_one("#author-input").value)
            event.stop()

    def _advance_field(self, answer: str) -> None:
        answer = answer.strip()
        stage = self._stage
        if stage == "title":
            if not answer:
                self.query_one("#author-status").update("A title is required.")
                return
            self._fields["title"] = answer
            self._last_field = "title"
        elif stage == "spec":
            self._fields["spec"] = answer
        elif stage == "reg":
            if answer:
                name, _, value = answer.partition(":")
                try:
                    int(value.strip(), 0)
                except ValueError:
                    self.query_one("#author-status").update(
                        f"Bad register value: {value!r} — use name:value"
                    )
                    return
                self._fields.setdefault("registers", []).append(f"{name}:{value}")
        elif stage == "asm":
            if not answer:
                self.query_one("#author-status").update("A reference program is required.")
                return
            self._fields["asm"] = answer.replace("\\n", "\n")
        elif stage == "solution":
            self._fields["solution"] = answer.replace("\\n", "\n")
        elif stage == "path":
            self._import_from_path(answer)
            return
        elif stage == "kind":
            if answer not in KIND_NAMES:
                self.query_one("#author-status").update(
                    f"kind must be one of {', '.join(KIND_NAMES)}"
                )
                return
            self._fields["kind"] = answer
        elif stage == "difficulty":
            self._fields["difficulty"] = answer
        elif stage == "flag":
            self._fields["flag"] = answer if answer else ""
        elif stage == "out":
            self._fields["output"] = answer.replace("\\n", "\n") if answer else ""
        elif stage == "step":
            if answer:
                kind, _, body = answer.partition("|")
                if kind not in STEP_KIND_NAMES:
                    self.query_one("#author-status").update(
                        f"unknown step kind {kind!r}; use {', '.join(STEP_KIND_NAMES)}"
                    )
                    return
                self._fields.setdefault("steps", []).append({"kind": kind, "content": body})
            else:
                self._fields.setdefault("steps", [])
                self._prog_queue = [s["kind"] for s in self._fields["steps"]]
                if self._prog_queue:
                    self._stage = "prog"
                    self._current_prog_kind = self._prog_queue.pop(0)
                    self._render_field()
                else:
                    self.action_save()
                return
        elif stage == "prog":
            if answer:
                kind, _, asm = answer.partition("|")
                for step in self._fields.get("steps", []):
                    if step["kind"] == kind:
                        step["program"] = asm.replace("\\n", "\n")
                        break
            if self._prog_queue:
                self._current_prog_kind = self._prog_queue.pop(0)
                self._render_field()
            else:
                self.action_save()
            return

        self._last_field = stage
        if self._mode == "lesson" and stage == "step":
            self._stage = "step"
            self._render_field()
            return
        order = self._field_order()
        if stage in order:
            next_index = order.index(stage) + 1
        else:
            next_index = len(order)
        if next_index >= len(order):
            self.action_save()
            return
        self._stage = order[next_index]
        self._render_field()

    def action_cycle_mode(self) -> None:
        self._mode = MODE_NAMES[(MODE_NAMES.index(self._mode) + 1) % len(MODE_NAMES)]
        self._reset_wizard()

    def action_howto(self) -> None:
        self.query_one("#author-status").update(
            "ADD CONTENT — press M to pick practice/challenge/lesson.\n"
            "The wizard asks one field at a time; press Enter after each answer.\n"
            "  - practice: title, spec, registers, reference assembly.\n"
            "  - challenge: + kind (registers/flags/output/mini_ctf), difficulty.\n"
            "  - lesson: title, then step=KIND|body lines and prog=KIND|asm lines.\n"
            "Registers: type 'rax:5' — the exercise will require RAX to end at 5.\n"
            "Assembly in lessons: 'prog=concept|mov rax, 1' runs on that step.\n"
            "Finish with Ctrl+Enter; it saves and appears in the list instantly."
        )

    def action_save(self) -> None:
        try:
            if self._mode == "lesson":
                saved = self._save_lesson()
            elif self._mode == "challenge":
                saved = self._save_challenge(challenge=True)
            else:
                saved = self._save_challenge(challenge=False)
        except ValueError as exc:
            self.query_one("#author-status").update(f"error: {exc}")
            self.app.notify(str(exc), severity="error")
            return
        if getattr(self._parent, "load_list", None) is not None:
            self._parent.load_list()
        self.query_one("#author-status").update(saved)
        self.app.notify(saved, severity="success")
        self._reset_wizard()

    def _save_challenge(self, challenge: bool) -> str:
        f = self._fields
        title = f.get("title", "")
        spec = f.get("spec", "")
        asm = f.get("asm", "")
        if not title or not spec or not asm.strip():
            raise ValueError("need title=, spec= and asm= before saving")
        expected = {"registers": {}}
        for reg in f.get("registers", []):
            name, _, value = reg.partition(":")
            expected["registers"][name] = int(value.strip(), 0)
        if f.get("output"):
            expected["output"] = f["output"]
        if challenge:
            self._state.user_content.add_challenge(
                title=title,
                spec=spec,
                reference=asm,
                expected=expected,
                challenge_type=f.get("kind", "registers"),
                difficulty=f.get("difficulty", "easy"),
                solution=f.get("solution", ""),
                flag=f.get("flag", ""),
            )
            return f"Challenge '{title}' saved."
        self._state.user_content.add_practice(
            title=title,
            spec=spec,
            reference=asm,
            expected=expected,
            solution=f.get("solution", ""),
        )
        return f"Practice '{title}' saved."

    def _save_lesson(self) -> str:
        f = self._fields
        title = f.get("title", "")
        if not title:
            raise ValueError("need a title before saving a lesson")
        steps = f.get("steps", [])
        if not steps:
            raise ValueError("a lesson needs at least one step (type step=concept|... first)")
        for step in steps:
            if step.get("program"):
                step["trace"] = self._trace_program(step["program"])
        self._state.user_content.add_lesson(
            module=f"user{self._next_module_ordinal()}",
            order=1,
            title=title,
            steps=steps,
        )
        return f"Lesson '{title}' saved ({len(steps)} steps)."

    @staticmethod
    def _trace_program(program: str) -> str:
        from academy.emulator import Executor

        ex = Executor()
        try:
            ex.load_asm(program)
        except Exception:
            return ""
        lines = []
        prev = {}
        for _ in range(500):
            try:
                snap = ex.step()
            except Exception:
                break
            insn = getattr(ex, "last_instruction", None) or f"step {snap.step_index}"
            changed = []
            regs = snap.registers or {}
            for name in sorted(set(regs) | set(prev)):
                old = prev.get(name, 0)
                new = regs.get(name, 0)
                if old != new:
                    changed.append(f"{name}={new:#x}")
            out = f"  {insn}"
            if changed:
                out += "   ->  " + ", ".join(changed)
            lines.append(out)
            prev = regs
            if snap.status in ("exited", "halted", "error", "breakpoint"):
                break
        if not lines:
            return ""
        header = "register effects per line (generated by running the example in the "
        "emulator):"
        return "\n".join([header, *lines])

    def _next_module_ordinal(self) -> int:
        existing = self._state.user_content.lesson_dicts()
        modules = {lesson["module"] for lesson in existing}
        n = 1
        while f"user{n}" in modules:
            n += 1
        return n
