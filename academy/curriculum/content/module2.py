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
                "Press R to run the example and read the final STATE panel: the program "
                "addresses the data segment through RBX. Which register still holds the "
                "data-segment base 0x600000 at exit?",
                program=read_asm("module2/lesson1_memory_layout/example.asm"),
                options=["RBX", "RAX", "RDX", "RSP"],
                answer=0,
                feedback={
                    1: "RAX is reused by the exit syscall, not by the address setup.",
                    2: "RDX is left at 0; the data address was loaded into RBX.",
                    3: "RSP tracks the stack, a different segment entirely.",
                },
                hint="Press R — RBX shows 0x600000, the base the byte was stored at.",
            ),
            _step(
                "response",
                "Run this program (press R): it stores the byte 17 into the data segment "
                "at 0x600009, then loads it straight back with MOVZX. Type the value that "
                "ends up in RDX.",
                program="mov rbx, 0x600000\nmov byte ptr [rbx+8], 17\n"
                        "movzx rdx, byte ptr [rbx+8]\nmov rax, 60\nmov rdi, 0\nsyscall",
                keywords=["17"],
                model_answer="17 — the store wrote 17 into the data segment and the MOVZX "
                    "read the exact byte back into RDX, so memory round-tripped the value.",
                hint="After R, RDX shows the byte that was stored.",
            ),
            _step(
                "feedback",
                "RDX = 17: the data segment accepted the byte at 0x600009 and returned the "
                "same byte on the load. Segments are ordinary addressable memory with "
                "roles — data is the read/write home for globals.",
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
                "Press R to run the example: RAX = 7 is pushed, RAX is disturbed, then the "
                "stack's top is popped into RBX. Read the final STATE panel — which value "
                "ends up in RBX?",
                program=read_asm("module2/lesson2_stack_rsp/example.asm"),
                options=["7", "99", "0", "the exit code"],
                answer=0,
                feedback={
                    1: "99 was written to RAX AFTER the save; the saved 7 came back via POP.",
                    2: "POP writes the popped value into its destination; it is never left at 0.",
                    3: "POP pulls the data value off the stack, not the process exit code.",
                },
                hint="Press R — RBX reads 7, the value that was pushed before RAX changed.",
            ),
            _step(
                "response",
                "Run this short program (press R): push 5, overwrite RAX, then pop into "
                "RDX. Type the value that ends up in RDX.",
                program=(
                    "mov rax, 5\npush rax\nmov rax, 1\npop rdx\n"
                    "mov rax, 60\nmov rdi, 0\nsyscall"
                ),
                keywords=["5"],
                model_answer="5 — PUSH saved 5 on the stack at RSP, MOV clobbered RAX, and "
                    "POP read the saved 5 back into RDX; the stack preserved the value "
                    "across the write.",
                hint="After R, RDX shows the value that was saved before the clobber.",
            ),
            _step(
                "feedback",
                "RDX = 5. PUSH wrote 5 onto the top of the stack and RSP dropped by 8; "
                "after MOV destroyed RAX, POP lifted the value back off and restored 5 "
                "into RDX. The stack grows down, and PUSH/POP keep that LIFO order.",
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
                "Press R to run the challenge: the frame reserves 24 bytes and stores "
                "1/2/3 at offsets 0/8/16, then sums the three locals. Read the final panel "
                "— what total ends up in RBX?",
                program=read_asm("module2/lesson3_stack_frames/challenge.asm"),
                options=["6", "3", "24", "1"],
                answer=0,
                feedback={
                    1: "3 is one local, not the sum of all three.",
                    2: "24 is the frame size in bytes, not the accumulated value.",
                    3: "1 is the first local's value, not the total.",
                },
                hint="Press R — RBX shows the sum of the three stored locals.",
            ),
            _step(
                "response",
                "Run this small frame (press R): 8 bytes are reserved at [rsp], the value "
                "42 is stored there, then loaded back into RDX before the frame is "
                "reclaimed. Type the value RDX ends up holding.",
                program="sub rsp, 8\nmov qword ptr [rsp], 42\nmov rdx, [rsp]\n"
                        "add rsp, 8\nmov rax, 60\nmov rdi, 0\nsyscall",
                keywords=["42"],
                model_answer="42 — the reserved stack slot held the value until the load "
                    "copied it into RDX; that slot was a local addressed relative to the "
                    "frame.",
                hint="After R, RDX shows the value stored into the frame slot.",
            ),
            _step(
                "feedback",
                "RDX = 42. A reserved block of stack (SUB RSP, N) is the locals area; the "
                "value was stored and loaded back from one of its slots. RBP is the fixed "
                "reference a prologue sets so every local has a stable address.",
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
                "Press R to run the example: RAX loads 0x1111111122222222, writes it into "
                "the heap block at 0x700000, and reads it back into RCX. Which register "
                "still shows the heap base 0x700000 at exit?",
                program=read_asm("module2/lesson4_heap/example.asm"),
                options=["RBX", "RAX", "RCX", "RSP"],
                answer=0,
                feedback={
                    1: "RAX is consumed by the exit syscall at the end.",
                    2: "RCX holds the VALUE loaded back, not the base address.",
                    3: "RSP points at the stack, the segment that grows downward.",
                },
                hint="Press R — RBX keeps the heap base it was loaded with.",
            ),
            _step(
                "response",
                "Run this program (press R): it treats 0x700000 as a heap block, writes "
                "100 into it, and reads it back into RDX. Type the value RDX ends up "
                "holding.",
                program="mov rbx, 0x700000\nmov qword ptr [rbx], 100\nmov rdx, [rbx]\n"
                        "mov rax, 60\nmov rdi, 0\nsyscall",
                keywords=["100"],
                model_answer="100 — the heap slot stored 100 and the load returned it; the "
                    "heap is just addressable memory whose lifetime the program controls.",
                hint="After R, RDX shows the value stored into the heap block.",
            ),
            _step(
                "feedback",
                "RDX = 100 — the heap block round-tripped the value. Nothing auto-frees a "
                "heap allocation; the program requested the block and must release it, "
                "otherwise the block leaks.",
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
