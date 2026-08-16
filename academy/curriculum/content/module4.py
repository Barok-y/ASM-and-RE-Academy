from __future__ import annotations

from ..models import Lesson, LessonStep, Module
from ._asm import read_asm


def _step(kind: str, content: str = "", **kwargs) -> LessonStep:
    return LessonStep(kind=kind, content=content, **kwargs)


def lesson_call_ret() -> Lesson:
    return Lesson(
        id="module4.lesson1",
        module="module4",
        title="CALL and RET",
        order=1,
        steps=[
            _step(
                "concept",
                "CALL does two things: it pushes the address of the next "
                "instruction onto the stack, then jumps to the callee. RET pops "
                "that address back into RIP, returning control right after the "
                "CALL. This makes calls nestable - each callee's return address "
                "sits on its own stack frame.",
            ),
            _step(
                "intuition",
                "CALL leaves a breadcrumb (the return address) on the stack so "
                "the CPU can always find its way home; RET follows the most "
                "recent breadcrumb.",
            ),
            _step(
                "analogy",
                "Marking your spot in a book before following a footnote, then "
                "returning to the bookmark when you finish - except the bookmarks "
                "pile up on a stack, so you always return to the most recent one.",
            ),
            _step(
                "visualization",
                "call f  ->  push <address after call>; rip = f\n"
                "stack:  [ret addr] <- RSP\n"
                "ret     ->  rip = pop();\n"
                "stack:  [ ... ]    <- RSP (frame of the caller)",
            ),
            _step(
                "example",
                "Call a function that adds 10 to RAX and returns it.",
                high_level="long f(long x) { return x + 10; } r = f(5);",
                program=read_asm("module4/lesson1_call_ret/example.asm"),
            ),
            _step(
                "walkthrough",
                "Step: RAX = 5, CALL pushes the return address and jumps to "
                "myfunc, ADD makes RAX 15, RET pops back to the instruction after "
                "the CALL, then the exit syscall runs.",
                program=read_asm("module4/lesson1_call_ret/example.asm"),
            ),
            _step(
                "prediction",
                "Press R to run the example: RAX = 5, CALL enters myfunc (which adds 10), "
                "RET comes back, and R8 copies RAX. Read the final panel — what value ends "
                "up in R8?",
                program=read_asm("module4/lesson1_call_ret/example.asm"),
                options=["15", "5", "10", "50"],
                answer=0,
                feedback={
                    1: "5 is the value BEFORE the call; the callee then changed it.",
                    2: "10 is the size of the add, not the final value.",
                    3: "The callee adds, it does not multiply.",
                },
                hint="Press R — the callee adds 10 to RAX, then RET hands control back.",
            ),
            _step(
                "response",
                "Run the challenge (press R): RAX = 5, CALL addten (add 10), then CALL "
                "double_it (double). Type the value that ends up in R8.",
                program=read_asm("module4/lesson1_call_ret/challenge.asm"),
                keywords=["30"],
                model_answer="30 — addten returned 15 to the instruction after its CALL, "
                    "then double_it doubled it to 30; each RET returned to the right spot "
                    "by popping its own return address.",
                hint="After R, R8 shows (5+10)*2 = 30.",
            ),
            _step(
                "feedback",
                "R8 = 30. Two CALLs pushed two return addresses onto the stack, and each "
                "RET popped the correct one back into RIP. That stack discipline is what "
                "lets calls nest and returns land exactly where they should.",
            ),
            _step(
                "challenge",
                "Call two functions in sequence: one adds 10, the other doubles. "
                "Start RAX at 5.",
                program=read_asm("module4/lesson1_call_ret/challenge.asm"),
                expected={"registers": {"r8": 30}},
            ),
            _step(
                "reflection",
                "If a callee's RET pops the wrong value, control jumps to garbage. "
                "What kinds of bugs can corrupt a saved return address?",
            ),
        ],
    )


def lesson_sysv_abi() -> Lesson:
    return Lesson(
        id="module4.lesson2",
        module="module4",
        title="System V Calling Convention",
        order=2,
        steps=[
            _step(
                "concept",
                "On Linux x86-64, the System V ABI says the first six integer "
                "arguments go in RDI, RSI, RDX, RCX, R8, R9 (left to right), and "
                "the return value comes back in RAX. The stack passes extra "
                "arguments. This fixed contract lets separately compiled "
                "functions call each other.",
            ),
            _step(
                "intuition",
                "Both caller and callee agree on where the handoff happens: "
                "registers for the first six arguments, RAX for the result. "
                "Without the agreement, neither side knows where to look.",
            ),
            _step(
                "analogy",
                "A standardized relay race handoff zone: the incoming runner "
                "(caller) places the baton in RDI, RSI, ... and the outgoing "
                "runner (callee) expects it exactly there and drops the finish "
                "time in RAX.",
            ),
            _step(
                "visualization",
                "caller:  mov rdi, a; mov rsi, b; call f\n"
                "callee:  f: ...  uses rdi and rsi ...  ret  (result in rax)\n"
                "arg slots: 1st=rdi 2nd=rsi 3rd=rdx 4th=rcx 5th=r8 6th=r9\n"
                "return:   rax",
            ),
            _step(
                "example",
                "Pass two arguments in RDI/RSI and read the return value in RAX.",
                high_level="long add(long a, long b) { return a + b; } r = add(4, 3);",
                program=read_asm("module4/lesson2_sysv_abi/example.asm"),
            ),
            _step(
                "walkthrough",
                "Step: RDI=4, RSI=3, CALL enters add_args, which moves RDI into "
                "RAX and adds RSI, then RET hands 7 back in RAX.",
                program=read_asm("module4/lesson2_sysv_abi/example.asm"),
            ),
            _step(
                "prediction",
                "Press R to run the challenge: RDI = 6, RSI = 4, and the callee computes "
                "rdi*rsi+1. Read the final panel — what value ends up in RBX?",
                program=read_asm("module4/lesson2_sysv_abi/challenge.asm"),
                options=["25", "10", "24", "30"],
                answer=0,
                feedback={
                    1: "6+4 = 10 is a sum; the callee multiplies then adds one.",
                    2: "6*4 = 24 misses the final +1.",
                    3: "30 would double the result; the callee does not.",
                },
                hint="Press R — 6*4+1 = 25 lands in RBX.",
            ),
            _step(
                "response",
                "Run the example (press R): the callee receives 4 in RDI and 3 in RSI, and "
                "returns rdi + rsi. Type the value that ends up in R8.",
                program=read_asm("module4/lesson2_sysv_abi/example.asm"),
                keywords=["7"],
                model_answer="7 — the callee moved RDI into RAX, added RSI, and returned "
                    "4+3 = 7 in RAX; the caller copied that into R8 per the ABI.",
                hint="After R, R8 shows 4+3 = 7.",
            ),
            _step(
                "feedback",
                "R8 = 7. The handoff ran on contract: arguments in RDI/RSI, result in RAX, "
                "caller reads it after the call. That shared convention is what lets any "
                "two functions call each other.",
            ),
            _step(
                "challenge",
                "Pass 6 and 4 in RDI/RSI and call a function returning "
                "rdi*rsi+1. Leave the result in RBX.",
                program=read_asm("module4/lesson2_sysv_abi/challenge.asm"),
                expected={"registers": {"rbx": 25}},
            ),
            _step(
                "reflection",
                "Why must the caller and callee agree on an exact ABI, and what "
                "goes wrong when a binary mixes two different conventions?",
            ),
        ],
    )


def lesson_callee_saved() -> Lesson:
    return Lesson(
        id="module4.lesson3",
        module="module4",
        title="Callee-Saved vs Caller-Saved",
        order=3,
        steps=[
            _step(
                "concept",
                "The ABI splits registers into two classes. Caller-saved (RAX, "
                "RCX, RDX, RSI, RDI, R8-R11) may be freely destroyed by a callee, "
                "so the caller must save anything it still needs. Callee-saved "
                "(RBX, RBP, R12-R15) must be restored to their incoming values "
                "before a callee returns, so the caller can rely on them "
                "surviving a call untouched.",
            ),
            _step(
                "intuition",
                "Think of registers as whiteboards in a shared room. Caller-saved "
                "means 'I might erase your notes - back them up first'. "
                "Callee-saved means 'I promise to restore your notes before I "
                "leave'.",
            ),
            _step(
                "analogy",
                "Caller-saved: you lend a pencil and accept it may come back "
                "chewed (save a spare). Callee-saved: you lend a pencil and the "
                "borrower must hand back the same pencil.",
            ),
            _step(
                "visualization",
                "caller:  mov rbx, 42      ; rbx is callee-saved\n"
                "         call f\n"
                "         ; rbx is STILL 42 here\n"
                "callee f:\n"
                "         push rbx          ; save it\n"
                "         mov rbx, 999\n"
                "         pop rbx           ; restore it\n"
                "         ret",
            ),
            _step(
                "example",
                "A callee that preserves RBX across its own use of the register.",
                high_level="// f must not clobber rbx: push/pop around its use",
                program=read_asm("module4/lesson3_callee_saved/example.asm"),
            ),
            _step(
                "walkthrough",
                "Step: RBX=42, CALL clobber, which pushes RBX, uses it, pops it "
                "back, and returns - leaving RBX at 42.",
                program=read_asm("module4/lesson3_callee_saved/example.asm"),
            ),
            _step(
                "prediction",
                "Press R to run the example: RBX = 42 enters 'clobber', which uses RBX "
                "internally (999) but pushes/pops it before returning. Read the final "
                "panel — what value ends up in R8 (the copy of RBX)?",
                program=read_asm("module4/lesson3_callee_saved/example.asm"),
                options=["42", "999", "0", "60"],
                answer=0,
                feedback={
                    1: "999 is the internal garbage value; the pop restored 42 first.",
                    2: "POP restores the saved value; it never leaves RBX zeroed.",
                    3: "60 is the exit syscall number, consumed at the very end.",
                },
                hint="Press R — RBX (and its copy R8) show the preserved 42.",
            ),
            _step(
                "response",
                "Run the challenge (press R): the CALLER saves RBX = 77 before the call "
                "and restores it after. Type the value that ends up in RBX.",
                program=read_asm("module4/lesson3_callee_saved/challenge.asm"),
                keywords=["77"],
                model_answer="77 — the caller pushed 77, the callee set RBX = 999, and the "
                    "caller popped 77 back, so its value survived the call untouched.",
                hint="After R, RBX shows 77 — saved and restored by the caller.",
            ),
            _step(
                "feedback",
                "RBX = 77 — the caller bore the cost by pushing and popping its own value. "
                "That is the caller-saved pattern: whoever needs a value across a call "
                "preserves it, because callees are free to destroy RDI, RAX, RCX and "
                "friends.",
            ),
            _step(
                "challenge",
                "Preserve RBX across a call that tramples it, using the "
                "caller-saved pattern (save before the call, restore after).",
                program=read_asm("module4/lesson3_callee_saved/challenge.asm"),
                expected={"registers": {"rbx": 77}},
            ),
            _step(
                "reflection",
                "Both caller-saved and callee-saved registers survive a call if "
                "both sides follow the rules. What is the actual difference in "
                "who pays the save/restore cost?",
            ),
        ],
    )


def lesson_stack_alignment() -> Lesson:
    return Lesson(
        id="module4.lesson4",
        module="module4",
        title="Stack Alignment and Prologues",
        order=4,
        steps=[
            _step(
                "concept",
                "System V requires RSP to be 16-byte aligned immediately before "
                "a CALL. CALL itself pushes 8 bytes, so at callee entry "
                "RSP % 16 == 8. Many functions start with 'push rbp; mov rbp, "
                "rsp; sub rsp, N' - the prologue that sets a frame pointer and "
                "reserves locals while keeping the alignment contract.",
            ),
            _step(
                "intuition",
                "The compiler counts bytes like a mason counting bricks: every "
                "CALL shifts RSP by 8, so the stack is padded in 8-byte units "
                "until the 16-byte boundary lines up again. Misalignment crashes "
                "code that uses aligned SSE loads.",
            ),
            _step(
                "analogy",
                "Avalanche safety: everyone takes one step down the mountain "
                "(8 bytes) for the call, and padding is the extra sideways "
                "shuffle that keeps everyone on the marked 16-foot grid.",
            ),
            _step(
                "visualization",
                "RSP = 0x...f00 (aligned, %16 == 0)\n"
                "call f:          push 8 bytes -> RSP % 16 == 8 at f's entry\n"
                "f prologue:      push rbp; mov rbp, rsp; sub rsp, N\n"
                "locals:          [rbp-8], [rbp-16], ...\n"
                "epilogue:        leave; ret  (RSP realigns on the way out)",
            ),
            _step(
                "example",
                "Pad the stack by 8 so the CALL is issued from an aligned RSP.",
                high_level="// rsp must be 0 mod 16 before the call",
                program=read_asm("module4/lesson4_stack_alignment/example.asm"),
            ),
            _step(
                "walkthrough",
                "Step: SUB RSP, 8 shifts the pointer, RDI carries the argument, "
                "CALL enters align_me, which reads RDI and returns RDI+1; ADD "
                "RSP, 8 restores the caller's stack.",
                program=read_asm("module4/lesson4_stack_alignment/example.asm"),
            ),
            _step(
                "prediction",
                "Press R to run the challenge: the code pads RSP by 8, passes 3 in RDI, "
                "and calls times_seven (rdi*7). Read the final panel — what value ends up "
                "in RBX?",
                program=read_asm("module4/lesson4_stack_alignment/challenge.asm"),
                options=["21", "17", "7", "24"],
                answer=0,
                feedback={
                    1: "17 would be rdi*5+2; the callee multiplies by 7 exactly.",
                    2: "7 is one argument, not the returned product.",
                    3: "24 is stack padding math, not the function's result.",
                },
                hint="Press R — 3*7 = 21 lands in RBX.",
            ),
            _step(
                "response",
                "Run the example (press R): RDI carries 5 into align_me, which returns "
                "rdi + 1. Type the value that ends up in R8.",
                program=read_asm("module4/lesson4_stack_alignment/example.asm"),
                keywords=["6"],
                model_answer="6 — align_me read RDI = 5, returned 5+1 = 6 in RAX, and the "
                    "caller copied it to R8 after restoring the stack.",
                hint="After R, R8 shows 5+1 = 6.",
            ),
            _step(
                "feedback",
                "R8 = 6 — the argument travelled in RDI, the callee left rdi+1 in RAX, and "
                "the caller saved it before the exit syscall. The 8-byte SUB kept RSP "
                "16-byte aligned at the CALL, so the ABI contract held.",
            ),
            _step(
                "challenge",
                "Align the stack, pass 3 in RDI, call a function returning "
                "rdi*7, and leave the result in RBX.",
                program=read_asm("module4/lesson4_stack_alignment/challenge.asm"),
                expected={"registers": {"rbx": 21}},
            ),
            _step(
                "reflection",
                "Why do compilers go to the trouble of padding to 16 bytes when "
                "plain integer code would run either way?",
            ),
        ],
    )


def module4() -> Module:
    return Module(
        id="module4",
        title="Functions and ABI",
        order=4,
        lessons=[
            lesson_call_ret(),
            lesson_sysv_abi(),
            lesson_callee_saved(),
            lesson_stack_alignment(),
        ],
    )
