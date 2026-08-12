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
                "After 'call f', what does RET do?",
                options=[
                    "pops the return address into RIP",
                    "jumps to a fixed address",
                    "pushes the return address",
                    "clears the stack",
                ],
                answer=0,
                feedback={
                    1: "RET follows the address left by the matching CALL.",
                    2: "Pushing the return address is CALL's job.",
                    3: "RET removes only the top item, which is the return address.",
                },
            ),
            _step(
                "response",
                "Which instruction pushes the return address onto the stack?",
                answer=0,
                options=["CALL", "RET"],
            ),
            _step(
                "feedback",
                "CALL pushes the return address; RET pops it back.",
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
                "In System V, where does the 1st integer argument travel?",
                options=["RDI", "RAX", "RSP", "RDX"],
                answer=0,
                feedback={
                    1: "RAX carries the RETURN value, not the first argument.",
                    2: "The stack only carries the 7th argument onward.",
                    3: "RDX is the 3rd argument slot.",
                },
            ),
            _step(
                "response",
                "Where does the callee leave its return value?",
                answer=1,
                options=["RDI", "RAX"],
            ),
            _step(
                "feedback",
                "RAX is the System V return-value register.",
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
                "A callee wants to use RBX temporarily. What must it do?",
                options=[
                    "save RBX (push) and restore it (pop) before returning",
                    "nothing, RBX is caller-saved",
                    "zero RBX before returning",
                    "move its value into RAX and hope",
                ],
                answer=0,
                feedback={
                    1: "RBX is callee-saved; it must be preserved.",
                    2: "Zeroing would violate the preservation contract.",
                    3: "That does not restore the caller's original value.",
                },
            ),
            _step(
                "response",
                "Which of these registers is CALLEE-saved in System V?",
                answer=1,
                options=["RDI", "RBX"],
            ),
            _step(
                "feedback",
                "RBX is callee-saved; RDI is a caller-saved argument register.",
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
                "Right after a CALL pushes the return address, RSP % 16 is...",
                options=["0", "8", "16", "undefined"],
                answer=1,
                feedback={
                    0: "Before the call RSP was 0 mod 16; the 8-byte push makes it 8.",
                    2: "RSP is never congruent to 16 mod 16; it is 0 or 8.",
                    3: "The ABI pins it down precisely.",
                },
            ),
            _step(
                "response",
                "What does 'sub rsp, N' do at the start of a prologue?",
                answer=0,
                options=["reserves N bytes for locals", "pushes the return address"],
            ),
            _step(
                "feedback",
                "SUB RSP carves out the local area; CALL handles the return address.",
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
