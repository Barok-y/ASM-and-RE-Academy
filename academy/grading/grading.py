from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Tuple

from capstone import CS_ARCH_X86, CS_MODE_64, Cs
from keystone import KS_ARCH_X86, KS_MODE_64, Ks, KsError

from academy.emulator import Executor

CHALLENGE_TYPES = (
    "prediction",
    "registers",
    "flags",
    "stack",
    "functions",
    "reverse_engineering",
    "patching",
    "optimization",
    "debugging",
    "mini_ctf",
)

DIFFICULTIES = ("easy", "medium", "hard", "expert", "adaptive")

MAX_HINT_LEVEL = 5
PENALTY_PER_HINT = 10
FAILURE_PENALTY = 3


@dataclass
class Challenge:
    id: str
    challenge_type: str
    difficulty: str
    title: str
    spec: str
    program: str
    expected: Dict[str, Any]
    hints: List[str] = field(default_factory=list)
    solution: str = ""
    flag: str = ""
    max_score: int = 100


@dataclass
class Grade:
    challenge_id: str
    correctness: float
    efficiency: float
    understanding: float
    explanation: float
    optimization: float
    total: float
    passed: bool
    feedback: List[str] = field(default_factory=list)
    review: List[str] = field(default_factory=list)
    related_lessons: List[str] = field(default_factory=list)


def _instruction_count(program: str) -> int:
    try:
        encoding, _ = Ks(KS_ARCH_X86, KS_MODE_64).asm(program)
    except KsError:
        return 0
    count = 0
    for _ in Cs(CS_ARCH_X86, CS_MODE_64).disasm(bytes(encoding), 0x400000):
        count += 1
    return count


def _run_and_collect(program: str, expected: Dict[str, Any]) -> Dict[Tuple[str, str], object]:
    ex = Executor()
    try:
        ex.load_asm(program)
        if "input" in expected:
            value = expected["input"]
            ex.set_input(value.encode() if isinstance(value, str) else value)
        ex.run(max_steps=10_000)
    except ValueError:
        return {}
    collected: Dict[Tuple[str, str], object] = {}
    for reg, value in expected.get("registers", {}).items():
        collected[("registers", reg)] = ex.get_register(reg)
    for flag, value in expected.get("flags", {}).items():
        collected[("flags", flag)] = ex.get_flag(flag)
    if "output" in expected:
        value = expected["output"]
        if isinstance(value, str):
            value = value.encode()
        collected[("output", "stdout")] = ex.output
    for addr, value in expected.get("memory", {}).items():
        if isinstance(value, str):
            value = value.encode()
        if isinstance(value, int):
            value = bytes([value])
        try:
            collected[("memory", int(addr))] = ex.memory_read(int(addr), len(value))
        except Exception:
            collected[("memory", int(addr))] = None
    return collected


class HintEngine:
    MAX_LEVEL = MAX_HINT_LEVEL
    PENALTY_PER_HINT = PENALTY_PER_HINT

    def hints_for(self, challenge: Challenge, level: int) -> List[str]:
        level = max(1, min(level, self.MAX_LEVEL))
        return list(challenge.hints[:level])

    def penalty(self, hints_used: int, failures: int = 0) -> int:
        base = self.PENALTY_PER_HINT * max(0, hints_used)
        return base + FAILURE_PENALTY * max(0, failures)


class Grader:
    def _review_for(self, challenge_type: str, wrong: List[str]) -> List[str]:
        """Map a failure to a concrete re-study plan linked to curriculum lessons."""
        topics = {
            "registers": (
                "registers",
                "Module 1 · Lesson 2 'Registers and the RAX family'",
                "MOV copies source->destination; sub-registers EAX/AX/AH/AL write "
                "into the low bits of the same cell.",
                "registers",
            ),
            "flags": (
                "flags",
                "Module 1 · Lesson 6 'Arithmetic and flags'",
                "Arithmetic sets ZF/SF/CF/OF; subtract a value from itself to force zero.",
                "flags",
            ),
            "prediction": (
                "instruction flow",
                "Module 3 · Lesson 2 'Conditional jumps'",
                "Re-read how RIP and the fetch-decode-execute loop move through a program.",
                "jumps",
            ),
            "stack": (
                "the stack",
                "Module 2 · Lesson 2 'The stack and RSP'",
                "The stack grows down; push/pop update RSP; the top is at [RSP].",
                "stack",
            ),
            "functions": (
                "functions & ABI",
                "Module 4 · Lesson 1 'CALL and RET'",
                "CALL pushes the return address, RET pops it; args live in RDI/RSI "
                "per the ABI.",
                "functions",
            ),
            "optimization": (
                "instruction efficiency",
                "Module 1 · Lesson 4 'LEA and addressing'",
                "LEA computes addresses without a dereference — a common one-instruction trick.",
                "lea",
            ),
            "reverse_engineering": (
                "reverse engineering",
                "Module 6 · Lesson 3 'Control-flow graphs'",
                "Rebuild intent by following branches and data flow across basic blocks.",
                "control-flow",
            ),
            "patching": (
                "patching",
                "Module 6 · Lesson 4 'Crackmes and patching'",
                "Flipping a conditional jump changes behavior — verify by re-running the emulator.",
                "patching",
            ),
            "debugging": (
                "debugging",
                "Module 7 · Lesson 1 'Breakpoints'",
                "Step through with breakpoints and inspect registers at each change.",
                "breakpoints",
            ),
        }
        topic, lesson, why, lesson_id = topics.get(
            challenge_type,
            ("the statement", "earlier modules", "review the concept.", ""),
        )
        self._related = [lesson_id] if lesson_id else []
        if not wrong:
            return [
                "Correctness passed — your end-state matches; focus next on efficiency.",
                f"review: {topic} — {lesson} — {why}",
            ]
        if any("register" in w for w in wrong):
            advice = "Check every `mov`/`lea` target and end-state value."
        elif any("flag" in w for w in wrong):
            advice = "Trace which instruction last set the flag you are checking."
        elif any("output" in w for w in wrong):
            advice = "Verify the syscall number and the register holding the buffer/length."
        else:
            advice = "Re-trace the program one instruction at a time in the sandbox."
        return [
            f"[red]state mismatch in {'/'.join(w.split(' ')[1] for w in wrong[:2])}[/] "
            f"— review: {advice}",
            f"review: what to re-learn — {lesson} — {why}",
            "hands-on: open the sandbox, run `step` / `registers`, watch the state change.",
        ]

    def grade(
        self,
        challenge: Challenge,
        submission: str,
        hints_used: int = 0,
        explanation: str = "",
    ) -> Grade:
        self._related: List[str] = []
        expected = challenge.expected
        actual = _run_and_collect(submission, expected)
        correctness = 1.0
        wrong = []
        for (group, name), want in {
            ("registers", k): v for k, v in expected.get("registers", {}).items()
        }.items():
            got = actual.get(("registers", name))
            if got != want:
                correctness = 0.0
                wrong.append(f"register {name}: expected {want}, got {got}")
        for (group, name), want in {
            ("flags", k): v for k, v in expected.get("flags", {}).items()
        }.items():
            got = actual.get(("flags", name))
            if got != want:
                correctness = 0.0
                wrong.append(f"flag {name}: expected {want}, got {got}")
        if "output" in expected:
            want = expected["output"]
            if isinstance(want, str):
                want = want.encode()
            got = actual.get(("output", "stdout"))
            if got != want:
                correctness = 0.0
                wrong.append(f"output: expected {want!r}, got {got!r}")
        for addr, want in expected.get("memory", {}).items():
            if isinstance(want, str):
                want = want.encode()
            if isinstance(want, int):
                want = bytes([want])
            got = actual.get(("memory", int(addr)))
            if got != want:
                correctness = 0.0
                wrong.append(f"memory @{addr:#x}: expected {want!r}, got {got!r}")

        submitted_count = _instruction_count(submission)
        reference_count = _instruction_count(challenge.program)
        if reference_count <= 0:
            efficiency = 1.0
        else:
            efficiency = (
                1.0 if submitted_count <= reference_count else reference_count / submitted_count
            )

        understanding = max(0.0, 1.0 - 0.25 * hints_used)
        word_count = len([w for w in explanation.split() if w])
        explanation_score = min(1.0, word_count / 20.0)
        optimization = efficiency

        total = (
            correctness * 50
            + efficiency * 15
            + understanding * 15
            + explanation_score * 10
            + optimization * 10
        )
        passed = correctness == 1.0 and total >= 60.0

        feedback = []
        if wrong:
            feedback.extend(f"incorrect: {w}" for w in wrong)
        else:
            feedback.append("correctness: passed")
        if efficiency < 1.0:
            feedback.append(
                f"efficiency: submission uses {submitted_count} instructions "
                f"vs {reference_count} reference"
            )
        if hints_used:
            feedback.append(
                f"hints used: {hints_used} "
                f"(penalty {hints_used * PENALTY_PER_HINT} points)"
            )
        review = self._review_for(challenge.challenge_type, wrong)
        if wrong and efficiency < 1.0:
            review.append(
                "optional: you solved the goal but used more instructions than needed."
            )

        return Grade(
            challenge_id=challenge.id,
            correctness=correctness,
            efficiency=efficiency,
            understanding=understanding,
            explanation=explanation_score,
            optimization=optimization,
            total=round(total, 1),
            passed=passed,
            feedback=feedback,
            review=review,
            related_lessons=getattr(self, "_related", []),
        )
