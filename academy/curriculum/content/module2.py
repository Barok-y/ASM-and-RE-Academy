from __future__ import annotations

from ..models import Lesson, LessonStep, Module
from ._asm import read_asm


def _step(kind: str, content: str = "", **kwargs) -> LessonStep:
    return LessonStep(kind=kind, content=content, **kwargs)


def lesson_layout() -> Lesson:
    return Lesson(
        id="module2.lesson1",
        module="module2",
        title="Process Memory Layout",
        order=1,
        steps=[
            _step(
                "concept",
                "A process's memory is split into segments. The text segment holds "
                "executable code, data holds initialized globals, bss holds "
                "zero-initialized globals, heap grows upward for dynamic allocation, "
                "and stack grows downward for function frames. Each has its own "
                "permissions and purpose.",
            ),
            _step(
                "intuition",
                "A single flat chunk of bytes would be chaos. Segments are "
                "neighborhoods with different rules: one is read-only (text), one "
                "holds your files (data/bss), and two grow toward each other "
                "(heap and stack).",
            ),
            _step(
                "analogy",
                "Imagine a warehouse. Text is the sealed instruction manual on the "
                "shelf, data is the box of labeled tools, bss is a pile of empty "
                "boxes pre-labeled, heap is the loading dock that expands outward, "
                "and stack is a stack of plates you push plates onto and take off "
                "the top.",
            ),
            _step(
                "visualization",
                "address space (x86-64, simplified)\n"
                " 0x400000  text   (code, read+execute)\n"
                " 0x600000  data   (initialized globals)\n"
                " 0x610000  bss    (zero-initialized globals)\n"
                " 0x700000  heap   (grows up   ^)\n"
                " 0x7ffff00000  stack (grows down v)",
            ),
            _step(
                "example",
                "Write a byte into the data segment and read it straight back.",
                high_level="unsigned char x; x = 42; return x;",
                program=read_asm("module2/lesson1_memory_layout/example.asm"),
            ),
            _step(
                "walkthrough",
                "Step and watch RBX load the absolute data address, then the byte "
                "store, then MOVZX widen it into RAX.",
                program=read_asm("module2/lesson1_memory_layout/example.asm"),
            ),
            _step(
                "prediction",
                "The data segment starts at 0x600000. Where is the heap segment?",
                options=["0x400000", "0x610000", "0x700000", "0x7ffff00000"],
                answer=2,
                feedback={
                    0: "0x400000 is the text segment.",
                    1: "0x610000 is the bss segment.",
                    3: "That is the top of the stack segment.",
                },
            ),
            _step(
                "response",
                "Which segment holds code and is typically read-only?",
                answer=1,
                options=["data", "text"],
            ),
            _step(
                "feedback",
                "Text is the code segment; it is mapped without write permission.",
            ),
            _step(
                "challenge",
                "Store the bytes 7 and 9 in the data segment and leave their sum in RBX.",
                program=read_asm("module2/lesson1_memory_layout/challenge.asm"),
                expected={"registers": {"rbx": 16}},
            ),
            _step(
                "reflection",
                "What would happen if a program wrote to the text segment? Why does "
                "the OS forbid it?",
            ),
        ],
    )


def lesson_stack_rsp() -> Lesson:
    return Lesson(
        id="module2.lesson2",
        module="module2",
        title="The Stack and RSP",
        order=2,
        steps=[
            _step(
                "concept",
                "The stack is a LIFO region of memory addressed by RSP. PUSH "
                "decrements RSP and writes a value; POP reads the value and "
                "increments RSP. The stack grows downward: lower addresses are "
                "newer entries.",
            ),
            _step(
                "intuition",
                "PUSH and POP are the only two movements the stack understands: "
                "put a plate on top, take the top plate off. You cannot grab the "
                "bottom plate without removing everything above it.",
            ),
            _step(
                "analogy",
                "The stack is a stack of plates. PUSH adds a plate on top, POP "
                "removes the top plate. RSP always points at the current top plate.",
            ),
            _step(
                "visualization",
                "RSP starts at 0x7ffffef00, RAX = 7.\n"
                "after 'push rax':   RSP 0x7ffffef00 -> 0x7ffffeef8\n"
                "    [0x7ffffeef8] holds 7   <- RSP\n"
                "    [0x7ffffef00] (old top)\n"
                "after 'pop rbx':    RBX = 7, RSP back to 0x7ffffef00.",
            ),
            _step(
                "example",
                "Save RAX on the stack, overwrite it, then restore it into RBX.",
                high_level="long tmp = x; x = 99; y = tmp;",
                program=read_asm("module2/lesson2_stack_rsp/example.asm"),
            ),
            _step(
                "walkthrough",
                "Step: PUSH drops RSP by 8 and stores 7; MOV breaks RAX; POP lifts "
                "RSP back up and loads 7 into RBX.",
                program=read_asm("module2/lesson2_stack_rsp/example.asm"),
            ),
            _step(
                "prediction",
                "RSP = 0x7ffffef00 and RAX = 3. After 'push rax', what is RSP?",
                options=[
                    "0x7ffffef00",
                    "0x7ffffef08",
                    "0x7ffffeef8",
                    "0x7fffffef0",
                ],
                answer=2,
                feedback={
                    0: "PUSH always changes RSP.",
                    1: "The stack grows DOWN: RSP decreases.",
                    3: "PUSH moves RSP by exactly 8 bytes, not 0x1f0.",
                },
            ),
            _step(
                "response",
                "Does the stack grow toward lower or higher addresses?",
                answer=0,
                options=["lower", "higher"],
            ),
            _step(
                "feedback",
                "It grows downward, so PUSH subtracts from RSP.",
            ),
            _step(
                "challenge",
                "Preserve RAX across a modification: push RAX (5), zero RAX, then "
                "pop the original value into RBX.",
                program=read_asm("module2/lesson2_stack_rsp/challenge.asm"),
                expected={"registers": {"rbx": 5}},
            ),
            _step(
                "reflection",
                "Why is preserving values on the stack better than copying them to "
                "another register when you have many nested calls?",
            ),
        ],
    )


def lesson_stack_frames() -> Lesson:
    return Lesson(
        id="module2.lesson3",
        module="module2",
        title="Stack Frames and RBP",
        order=3,
        steps=[
            _step(
                "concept",
                "A function reserves a block of the stack for its local variables, "
                "called a stack frame. The classic prologue is 'push rbp; mov rbp, "
                "rsp; sub rsp, N', which saves the caller's frame pointer, sets a "
                "new one, and carves out N bytes of locals addressed as "
                "[rbp - offset].",
            ),
            _step(
                "intuition",
                "The frame pointer is a bookmark that stays put while RSP moves "
                "around, so every local has a stable address no matter how the "
                "stack is pushed during the function.",
            ),
            _step(
                "analogy",
                "Think of a clipboard you hold still while you shuffle papers on "
                "your desk: RBP is the clipboard, RSP is the moving stack of "
                "papers, and locals are always measured from the clipboard.",
            ),
            _step(
                "visualization",
                "before call:  [caller frame]  <- RSP\n"
                "prologue:\n"
                "  push rbp      [saved rbp]\n"
                "  mov rbp, rsp  RBP = RSP (frame base)\n"
                "  sub rsp, 16   [local2] [local1]  <- RSP\n"
                "locals live at [rbp-8] and [rbp-16].",
            ),
            _step(
                "example",
                "Carve out 16 bytes of locals and move values through them.",
                high_level="void f(void) { long a = x; long b = y; z = a + b; }",
                program=read_asm("module2/lesson3_stack_frames/example.asm"),
            ),
            _step(
                "walkthrough",
                "Step: SUB RSP reserves space, stores go to [rsp] and [rsp+8], "
                "loads copy them back, and ADD RSP reclaims the space.",
                program=read_asm("module2/lesson3_stack_frames/example.asm"),
            ),
            _step(
                "prediction",
                "After 'sub rsp, 16', where do the two locals live?",
                options=[
                    "[rsp] and [rsp+8]",
                    "[rsp+16] and [rsp+24]",
                    "[rsp-8] and [rsp-16]",
                    "in registers only",
                ],
                answer=0,
                feedback={
                    1: "RSP moved down by 16, so the reserved space is [rsp, rsp+16).",
                    2: "That would be below the stack, outside the frame.",
                    3: "Locals are in memory; the registers just hold addresses.",
                },
            ),
            _step(
                "response",
                "Which register acts as the stable frame base in a classic prologue?",
                answer=1,
                options=["RSP", "RBP"],
            ),
            _step(
                "feedback",
                "RBP is the frame pointer; RSP keeps moving as the function runs.",
            ),
            _step(
                "challenge",
                "Reserve 24 bytes, store 1/2/3 at offsets 0/8/16, then sum the "
                "three locals into RBX before reclaiming the frame.",
                program=read_asm("module2/lesson3_stack_frames/challenge.asm"),
                expected={"registers": {"rbx": 6}},
            ),
            _step(
                "reflection",
                "A compiler sometimes omits RBP entirely and addresses locals from "
                "RSP. When is the frame pointer actually necessary?",
            ),
        ],
    )


def lesson_heap() -> Lesson:
    return Lesson(
        id="module2.lesson4",
        module="module2",
        title="Heap and Dynamic Memory",
        order=4,
        steps=[
            _step(
                "concept",
                "The heap is a large region for data whose size is unknown at "
                "compile time. The program requests memory from it (malloc, brk, "
                "mmap) and is responsible for releasing it. The heap grows upward "
                "from a low base, the stack downward from a high base.",
            ),
            _step(
                "intuition",
                "The stack is automatic: push/pop handles lifetime. The heap is "
                "manual: you ask for a block, use it, and must give it back, or "
                "the block leaks.",
            ),
            _step(
                "analogy",
                "The stack is a scratch pad you rent by the page and return "
                "automatically. The heap is a self-service storage lot: rent a "
                "unit, use it, return the key when done - forget to return it and "
                "the lot slowly fills forever (a leak).",
            ),
            _step(
                "visualization",
                "heap base 0x700000\n"
                "  block1 @ 0x700000 (8 bytes)\n"
                "  block2 @ 0x700008 (16 bytes)\n"
                "heap grows UP  ->  next block at the top of the used area\n"
                "stack grows DOWN  <-  the two regions meet nowhere (until overflow).",
            ),
            _step(
                "example",
                "Write a value into the heap segment and read it back.",
                high_level="unsigned long *p = malloc(8); *p = 0x1111111122222222;",
                program=read_asm("module2/lesson4_heap/example.asm"),
            ),
            _step(
                "walkthrough",
                "Step: RBX loads the heap base, the store writes 8 bytes, and the "
                "load reads them back into RCX.",
                program=read_asm("module2/lesson4_heap/example.asm"),
            ),
            _step(
                "prediction",
                "If heap grows up and stack grows down, what happens to a buffer "
                "that overruns its heap block toward higher addresses?",
                options=[
                    "It collides with the stack",
                    "It collides with the text segment",
                    "It stays inside the same heap block",
                    "It is caught by the CPU automatically",
                ],
                answer=0,
                feedback={
                    1: "The heap is far above the text segment.",
                    2: "An overrun by definition leaves the block.",
                    3: "The CPU does not track heap block boundaries.",
                },
            ),
            _step(
                "response",
                "Who is responsible for freeing memory allocated on the heap?",
                answer=1,
                options=["the stack", "the program (via free/delete)"],
            ),
            _step(
                "feedback",
                "Correct: heap memory is manual - the program must release it.",
            ),
            _step(
                "challenge",
                "Treat 0x700000 as a 16-byte heap block: store 0xABCD in the first "
                "slot and 0x1234 in the second, then leave the second slot in RBX.",
                program=read_asm("module2/lesson4_heap/challenge.asm"),
                expected={"registers": {"rbx": 0x1234}},
            ),
            _step(
                "reflection",
                "A memory leak is a program that forgets to free heap blocks. How "
                "could a leak eventually make a long-running server crash?",
            ),
        ],
    )


def module2() -> Module:
    return Module(
        id="module2",
        title="Memory and Stack",
        order=2,
        lessons=[
            lesson_layout(),
            lesson_stack_rsp(),
            lesson_stack_frames(),
            lesson_heap(),
        ],
    )
