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
                "Press R to run the example: a breakpoint on 'mov rbx, rax' would pause "
                "after the second ADD, when RAX = 5+3 = 8. Read the final panel — what "
                "value ends up in RBX?",
                program=read_asm("module7/lesson1_breakpoints/example.asm"),
                options=["8", "5", "3", "14"],
                answer=0,
                feedback={
                    1: "5 is RAX's starting value, before the two ADDs.",
                    2: "3 is one of the increments, not the result.",
                    3: "14 would double; the adds total 8, not 14.",
                },
                hint="Press R — RBX copies the observed RAX = 8.",
            ),
            _step(
                "response",
                "Run the challenge (press R): the breakpoint sits on 'mov rbx, rax', and "
                "RAX is 8 when execution pauses there. Type the value RBX ends up "
                "holding.",
                program=read_asm("module7/lesson1_breakpoints/challenge.asm"),
                keywords=["8"],
                model_answer="8 — the pause happens after the ADDs, so RAX = 8 is the "
                    "inspection point; 'mov rbx, rax' then copies exactly the value the "
                    "breakpoint exposed.",
                hint="After R, RBX shows the value seen at the breakpoint.",
            ),
            _step(
                "feedback",
                "RBX = 8. The breakpoint froze execution when RAX reached 5+3, exposing "
                "the state to inspect; the program then continued and copied that state "
                "into RBX. Choosing the right pause point is the whole skill.",
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
                "Press R to run the challenge: bytes 0x10, 0x20, 0x30 are written to "
                "consecutive addresses, then the SECOND byte is loaded into RBX. Read the "
                "final panel — what value ends up in RBX?",
                program=read_asm("module7/lesson2_memory_inspection/challenge.asm"),
                options=["0x20", "0x10", "0x30", "0x00"],
                answer=0,
                feedback={
                    1: "0x10 is at offset +0, the first written byte.",
                    2: "0x30 is at offset +2, the third written byte.",
                    3: "Each byte was explicitly written; nothing reads as 0.",
                },
                hint="Press R — loading [rbx+1] yields the byte at the second slot.",
            ),
            _step(
                "response",
                "Run the example (press R): it writes 0xAA, 0xBB, 0xCC to memory at "
                "0x600000, 0x600001, 0x600002. Type the hex value (with 0x) stored at "
                "offset +1 — the second byte of the structure.",
                program=read_asm("module7/lesson2_memory_inspection/example.asm"),
                keywords=["0xbb", "bb", "187"],
                model_answer="0xBB — offset +1 received the 0xBB write; a hexdump of the "
                    "three bytes reads aa bb cc.",
                hint="After R, visualize the hexdump: aa bb cc in order.",
            ),
            _step(
                "feedback",
                "0xBB sits at [rbx+1]. Reading memory byte-by-byte (aa bb cc) is exactly "
                "the hexdump view a debugger gives you — addresses drive the inspection, "
                "and each offset within the structure names one field.",
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
                "Press R to run this trace: a straight-line calculation, 2*3+1, followed "
                "by a save into R8. Read the final panel — what value ends up in R8?",
                program="mov rax, 2\nmov rbx, 3\nimul rax, rbx\nadd rax, 1\nmov r8, rax\n"
                        "mov rax, 60\nmov rdi, 0\nsyscall",
                options=["7", "6", "5", "1"],
                answer=0,
                feedback={
                    1: "6 is the product before the final +1.",
                    2: "5 would be 2+3; the multiply runs first.",
                    3: "1 is the added constant, not the total.",
                },
                hint="Press R — stepping the trace shows 2*3+1 = 7.",
            ),
            _step(
                "response",
                "Run the challenge (press R): the loop body executes once per decrement. "
                "Type the iteration count the trace would report — the value that ends "
                "up in RBX.",
                program=read_asm("module7/lesson3_runtime_analysis/challenge.asm"),
                keywords=["4"],
                model_answer="4 — the counter runs 4, 3, 2, 1; each pass increments RBX "
                    "and the 'jne' falls through once RCX hits 0, so the body ran 4 "
                    "times.",
                hint="After R, RBX shows the number of body executions.",
            ),
            _step(
                "feedback",
                "RBX = 4 — the trace counted four executions of the loop body. That "
                "count, not static reading of the file, is what tells an optimizer which "
                "path is hot — the core of dynamic analysis.",
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
