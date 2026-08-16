"""Lesson engine: drives a lesson through its steps, runs walkthrough
programs, grades prediction questions, verifies challenges, and produces
the three synchronized views (source / assembly / debugger state)."""

from __future__ import annotations

from typing import Dict, Optional, Tuple

from academy.emulator import Executor
from academy.sandbox.explain import format_flags, format_registers

from .models import Lesson, LessonStep


def _flatten_expected(expected: Dict[str, object]) -> Dict[Tuple[str, str], object]:
    flat: Dict[Tuple[str, str], object] = {}
    for reg, value in expected.get("registers", {}).items():
        flat[("registers", reg)] = value
    for flag, value in expected.get("flags", {}).items():
        flat[("flags", flag)] = value
    if "output" in expected:
        value = expected["output"]
        if isinstance(value, str):
            value = value.encode()
        flat[("output", "stdout")] = value
    for addr, value in expected.get("memory", {}).items():
        if isinstance(value, str):
            value = value.encode()
        if isinstance(value, int):
            value = bytes([value])
        flat[("memory", int(addr))] = value
    return flat


class LessonSession:
    def __init__(self, lesson: Lesson, executor: Executor | None = None):
        self.lesson = lesson
        self.executor = executor or Executor()
        self.index = 0
        self.responses = []

    @property
    def current(self) -> LessonStep:
        return self.lesson.steps[self.index]

    def reset(self) -> None:
        self.index = 0
        self.responses = []

    def advance(self) -> Optional[LessonStep]:
        if self.index < len(self.lesson.steps) - 1:
            self.index += 1
            return self.current
        return None

    def respond(self, option_index: int) -> str:
        step = self.current
        self.responses.append({"kind": step.kind, "option": option_index})
        if step.answer is None:
            return ""
        if option_index == step.answer:
            return step.feedback.get(option_index, "") or "Correct!"
        chosen = step.options[option_index] if option_index < len(step.options) else ""
        correct = ""
        if step.answer is not None and step.answer < len(step.options):
            correct = step.options[step.answer]
        base = step.feedback.get(option_index, "")
        hint = (
            f"\nIncorrect (you chose: {chosen}). "
            f"The correct answer was option {step.answer + 1}: {correct}."
        )
        return (base + hint).strip()

    def load_program(self) -> None:
        if self.current.program:
            self.executor.load_asm(self.current.program)

    def run_program(self) -> str:
        self.load_program()
        self.executor.run()
        return f"output: {self.executor.output!r}\nstatus: {self.executor.status}"

    def respond_text(self, submitted: str) -> Tuple[bool, str]:
        """Grade a free-form 'response' step against keywords and a model answer."""
        step = self.current
        self.responses.append({"kind": step.kind, "text": submitted})
        if not step.keywords:
            return True, "Recorded — press N to continue."
        text = submitted.lower()
        missing = [k for k in step.keywords if k.lower() not in text]
        if not missing:
            return True, "Good answer. Press N to continue to the next step."
        joined = ", ".join(missing)
        base = step.model_answer or ""
        return (
            False,
            f"Your answer is missing: {joined}. \nA model answer:\n{base}",
        )

    def verify_challenge(self, submitted_program: Optional[str] = None) -> Tuple[bool, str]:
        step = self.current
        if step.kind != "challenge":
            raise ValueError("current step is not a challenge")
        program = submitted_program if submitted_program is not None else step.program
        expected = _flatten_expected(step.expected)
        ex = Executor()
        try:
            ex.load_asm(program)
        except Exception:
            # A plain number answer (e.g. "5") is synthesized into mov <reg>, <value>
            # when the expected end-state is a single register.
            synthesized = self._synthesize_value_answer(program, expected)
            if synthesized is None:
                raise
            ex = Executor()
            ex.load_asm(synthesized)
        if "input" in step.expected:
            raw = step.expected["input"]
            ex.set_input(raw.encode() if isinstance(raw, str) else raw)
        ex.run()
        diffs = []
        for (group, name), want in expected.items():
            if group == "registers":
                got = ex.get_register(name)
            elif group == "flags":
                got = ex.get_flag(name)
            elif group == "memory":
                try:
                    got = ex.memory_read(name, len(want))
                except Exception:
                    got = None
            else:
                got = ex.output
            if got != want:
                diffs.append(f"{group}.{name}: expected {want!r}, got {got!r}")
        if not diffs:
            return True, "Challenge passed"
        return False, "; ".join(diffs)

    @staticmethod
    def _synthesize_value_answer(program: str, expected: dict) -> Optional[str]:
        """Turn a plain numeric answer into assembly when the expected state is
        a single register. Returns None if the answer isn't a number or other
        groups (output/memory) are asserted."""
        regs = {name: value for (group, name), value in expected.items() if group == "registers"}
        if len(regs) != 1 or len(expected) != 1:
            return None
        (reg, want), = regs.items()
        text = program.strip().lower().replace("_", "").replace(",", "").replace(" ", "")
        if not text:
            return None
        try:
            value = int(text, 0)
        except ValueError:
            try:
                value = int(text, 16)
            except ValueError:
                return None
        return f"mov {reg}, {value:#x}"

    def three_views(self) -> Dict[str, str]:
        step = self.current
        state = "\n".join(
            (
                format_registers(self.executor.registers()),
                format_flags(self.executor.flags()),
            )
        )
        return {
            "source": step.high_level or "",
            "assembly": step.program or "",
            "state": state,
        }
