from __future__ import annotations

from ..models import Lesson, LessonStep, Module
from ._asm import read_asm


def _step(kind: str, content: str = "", **kwargs) -> LessonStep:
    return LessonStep(kind=kind, content=content, **kwargs)


def lesson_breakpoints() -> Lesson:
    return Lesson(
        id="module7.lesson1",
        module="module7",
        title="Breakpoints",
        order=1,
        steps=[
            _step(
                "concept",
                "A breakpoint pauses execution at a chosen address. Debuggers "
                "implement it by replacing the instruction byte with int3, "
                "letting the CPU raise an interrupt the debugger catches, then "
                "restoring the byte so stepping continues. Breakpoints let you "
                "stop at a moment of interest and inspect state.",
            ),
            _step(
                "intuition",
                "You do not want to watch every instruction; you want to pause "
                "exactly where things get interesting. A breakpoint is that "
                "chosen pause point.",
            ),
            _step(
                "analogy",
                "Putting a sticky note on a page of a recipe so you stop there "
                "to check the oven, instead of reading the whole book first.",
            ),
            _step(
                "visualization",
                "original bytes:  48 c7 c0 05 00 00 00   (mov rax, 5)\n"
                "with breakpoint: cc                    (int3)\n"
                "debugger catches, restores, and lets you inspect registers\n"
                "before re-inserting the breakpoint and continuing.",
            ),
            _step(
                "example",
                "Set a mental breakpoint on 'mov rbx, rax': what is RAX when "
                "execution pauses there?",
                high_level="long x = 5; x += 3; long y = x;",
                program=read_asm("module7/lesson1_breakpoints/example.asm"),
            ),
            _step(
                "walkthrough",
                "Step through the two ADD instructions and notice RAX reaches 8 "
                "before the copy; that is exactly the state a breakpoint would "
                "expose.",
                program=read_asm("module7/lesson1_breakpoints/example.asm"),
            ),
            _step(
                "prediction",
                "A breakpoint pauses execution...",
                options=[
                    "at a chosen address",
                    "only at the start of the program",
                    "at random points",
                    "only after 1000 instructions",
                ],
                answer=0,
                feedback={
                    1: "You can break anywhere, not just at the start.",
                    2: "Breakpoints are deterministic addresses, not random.",
                    3: "Count-based stopping is a different feature (a step count).",
                },
            ),
            _step(
                "response",
                "What single-byte instruction do debuggers typically insert for "
                "a breakpoint?",
                answer=1,
                options=["nop", "int3"],
            ),
            _step(
                "feedback",
                "int3 (0xCC) triggers the breakpoint trap the debugger handles.",
            ),
            _step(
                "challenge",
                "Break on 'mov rbx, rax' after the second ADD: RAX is 8 there. "
                "Run it so RBX ends up holding 8.",
                program=read_asm("module7/lesson1_breakpoints/challenge.asm"),
                expected={"registers": {"rbx": 8}},
            ),
            _step(
                "reflection",
                "Why does patching an instruction in place to int3 break "
                "self-modifying code or code that verifies its own checksums?",
            ),
        ],
    )


def lesson_memory_inspection() -> Lesson:
    return Lesson(
        id="module7.lesson2",
        module="module7",
        title="Memory Inspection",
        order=2,
        steps=[
            _step(
                "concept",
                "Memory inspection means reading raw bytes at an address: a "
                "hexdump of a region, the value of a local on the stack, or the "
                "contents of a struct. Debuggers let you view memory as bytes, "
                "words, or the types of the original source.",
            ),
            _step(
                "intuition",
                "Registers are where the CPU does work; memory is where the "
                "data lives. To understand a crash or a data race you often "
                "have to look at the bytes themselves, not the registers.",
            ),
            _step(
                "analogy",
                "Registers are the hands holding the tools; memory is the "
                "warehouse. A warehouse inventory (hexdump) tells you exactly "
                "what is sitting where on the shelves.",
            ),
            _step(
                "visualization",
                "hexdump 0x600000, 4 bytes:   aa bb cc 00\n"
                "byte at +0: 0xaa   byte at +1: 0xbb\n"
                "byte at +2: 0xcc   byte at +3: 0x00\n"
                "reading [rbx+1] widens byte 0xbb -> rax (0xbb).",
            ),
            _step(
                "example",
                "Write a three-byte structure into memory and inspect the bytes.",
                high_level="struct { unsigned char a, b, c; } s; s.a=0xAA; s.b=0xBB; "
                "s.c=0xCC;",
                program=read_asm("module7/lesson2_memory_inspection/example.asm"),
            ),
            _step(
                "walkthrough",
                "Step and watch each byte land at [rbx], [rbx+1], [rbx+2]; a "
                "hexdump of 0x600000 shows exactly aa bb cc.",
                program=read_asm("module7/lesson2_memory_inspection/example.asm"),
            ),
            _step(
                "prediction",
                "After writing 0x10 at [rbx], 0x20 at [rbx+1], 0x30 at "
                "[rbx+2], what is byte [rbx+1]?",
                options=["0x10", "0x20", "0x30", "0x00"],
                answer=1,
                feedback={
                    0: "0x10 is at offset +0.",
                    2: "0x30 is at offset +2.",
                    3: "Each byte was explicitly written, not zeroed.",
                },
            ),
            _step(
                "response",
                "Memory inspection reads bytes at a given...",
                answer=1,
                options=["register value only", "address"],
            ),
            _step(
                "feedback",
                "Inspection is address-driven: you read the bytes at an address.",
            ),
            _step(
                "challenge",
                "Write 0x10, 0x20, 0x30 to three consecutive bytes, then load "
                "the second byte (0x20) into RBX.",
                program=read_asm("module7/lesson2_memory_inspection/challenge.asm"),
                expected={"registers": {"rbx": 0x20}},
            ),
            _step(
                "reflection",
                "When debugging a crash, why is looking at the bytes on the "
                "stack often more informative than the registers?",
            ),
        ],
    )


def lesson_runtime_analysis() -> Lesson:
    return Lesson(
        id="module7.lesson3",
        module="module7",
        title="Runtime Analysis",
        order=3,
        steps=[
            _step(
                "concept",
                "Runtime analysis observes a program as it executes: tracing "
                "each instruction, counting how often a block runs, sampling "
                "where time is spent, and watching memory/register changes "
                "unfold. Where static analysis reads bytes, dynamic analysis "
                "records behavior.",
            ),
            _step(
                "intuition",
                "A profiler answers 'which loop runs a million times?' by "
                "counting, not by guessing. Tracing answers 'what exactly "
                "happened?' with a step-by-step record of state changes.",
            ),
            _step(
                "analogy",
                "Watching a replay of a sports game with a coach's pointer: you "
                "see each play (instruction), how often a formation repeats "
                "(loop count), and where the game is won or lost (hot path).",
            ),
            _step(
                "visualization",
                "instruction trace:\n"
                "  1  mov rax, 2      rax=2\n"
                "  2  mov rbx, 3      rbx=3\n"
                "  3  imul rax, rbx   rax=6\n"
                "  4  add rax, 1      rax=7\n"
                "hot loop: body executed 4 times.",
            ),
            _step(
                "example",
                "Trace a short calculation: 2 * 3 + 1.",
                high_level="long x = 2 * 3 + 1;",
                program=read_asm("module7/lesson3_runtime_analysis/example.asm"),
            ),
            _step(
                "walkthrough",
                "Step and read the trace: RAX = 2, RBX = 3, IMUL makes RAX 6, "
                "and the final ADD leaves 7.",
                program=read_asm("module7/lesson3_runtime_analysis/example.asm"),
            ),
            _step(
                "prediction",
                "A profile shows one loop body executed 100,000 times while "
                "everything else ran a handful of times. Where should an "
                "optimizer look first?",
                options=[
                    "inside that loop",
                    "in the entry code",
                    "in error handling",
                    "everywhere equally",
                ],
                answer=0,
                feedback={
                    1: "The entry code runs once; optimize the hot path.",
                    2: "Error paths rarely run.",
                    3: "Optimization effort should follow measured frequency.",
                },
            ),
            _step(
                "response",
                "Runtime analysis records a program's...",
                answer=1,
                options=["bytes on disk", "actual behavior as it executes"],
            ),
            _step(
                "feedback",
                "Dynamic analysis captures behavior over time, unlike static "
                "analysis of the file alone.",
            ),
            _step(
                "challenge",
                "This loop body executes 4 times; leave the iteration count in "
                "RBX.",
                program=read_asm("module7/lesson3_runtime_analysis/challenge.asm"),
                expected={"registers": {"rbx": 4}},
            ),
            _step(
                "reflection",
                "Dynamic analysis only sees the paths a given input executes. "
                "Why is that both its power and its blind spot?",
            ),
        ],
    )


def module7() -> Module:
    return Module(
        id="module7",
        title="Dynamic Analysis",
        order=7,
        lessons=[
            lesson_breakpoints(),
            lesson_memory_inspection(),
            lesson_runtime_analysis(),
        ],
    )
