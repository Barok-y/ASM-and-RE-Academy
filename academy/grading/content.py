"""Sample challenges covering Module 1 topics."""

from __future__ import annotations

from typing import List

from .grading import Challenge


def sample_challenges() -> List[Challenge]:
    return [
        Challenge(
            id="ch1",
            challenge_type="registers",
            difficulty="easy",
            title="Copy with MOV",
            spec="Write two instructions so that RBX ends up holding 42.",
            program="mov rax, 42\nmov rbx, rax",
            expected={"registers": {"rbx": 42}},
            hints=[
                "MOV copies from a source into a destination.",
                "Load 42 into a register first, then copy it.",
                "mov rax, 42",
                "then mov rbx, rax",
                "RAX can be any scratch register.",
            ],
        ),
        Challenge(
            id="ch2",
            challenge_type="registers",
            difficulty="medium",
            title="Sub-register reconstruction",
            spec="Write instructions so RAX ends up 0x0000000012347F05. "
            "Start with mov eax, 0x12345678, then use AX/AH/AL writes only.",
            program="mov eax, 0x12345678\nmov ax, 0xABCD\nmov al, 0x05\nmov ah, 0x7F",
            expected={"registers": {"rax": 0x0000000012347F05}},
            hints=[
                "Write AX to change the low 16 bits.",
                "AH and AL change one byte of AX each.",
                "mov ax, 0xABCD fixes the low 16 bits.",
                "mov al, 0x05 then mov ah, 0x7F.",
                "Order of AH/AL writes does not matter.",
            ],
        ),
        Challenge(
            id="ch3",
            challenge_type="flags",
            difficulty="easy",
            title="Zero the flag",
            spec="End with ZF = 1 and RAX = 0 using arithmetic.",
            program="mov rax, 5\nsub rax, 5",
            expected={"registers": {"rax": 0}, "flags": {"zf": True}},
            hints=[
                "SUB sets ZF when the result is zero.",
                "Subtract a register from itself to force zero.",
                "mov rax, 5",
                "sub rax, 5",
                "xor rax, rax also works.",
            ],
        ),
        Challenge(
            id="ch4",
            challenge_type="prediction",
            difficulty="easy",
            title="Predict ADD",
            spec="Write a program that starts with mov rax, 3 and ends with "
            "RAX = 8 using a single ADD instruction.",
            program="mov rax, 3\nadd rax, 5",
            expected={"registers": {"rax": 8}},
            hints=[
                "ADD writes the sum into its destination.",
                "3 + 5 = 8, so add the immediate 5.",
                "mov rax, 3",
                "add rax, 5",
                "The first operand is the destination.",
            ],
        ),
Challenge(
            id="ch5",
            challenge_type="optimization",
            difficulty="hard",
            title="Address arithmetic",
            spec="Put 0x2004 into RAX. Bonus: use a single LEA.",
            program="mov rbx, 0x2004\nmov rax, rbx",
            expected={"registers": {"rax": 0x2004}},
            hints=[
                "LEA computes addresses without dereferencing.",
                "You need a base value near 0x2004.",
                "mov rbx, 0x2000 then lea rax, [rbx + 4].",
                "That is two instructions.",
                "Try to reach the same value in one LEA.",
            ],
        ),
        Challenge(
            id="ch6",
            challenge_type="flags",
            difficulty="medium",
            title="Carry or borrow",
            spec="End with CF = 1: use a SUB that needs to borrow.",
            program="mov rax, 1\nsub rax, 2",
            expected={"registers": {"rax": 0xFFFFFFFFFFFFFFFF}, "flags": {"cf": True}},
            hints=[
                "CF is set when unsigned subtraction underflows.",
                "Subtract a number larger than the minuend.",
                "1 - 2 borrows, so CF is set.",
                "mov rax, 1 then sub rax, 2.",
            ],
        ),
        Challenge(
            id="ch7",
            challenge_type="flags",
            difficulty="medium",
            title="Sign test",
            spec="End with SF = 1 (negative result) using arithmetic.",
            program="mov rax, 0\nsub rax, 1",
            expected={"registers": {"rax": 0xFFFFFFFFFFFFFFFF}, "flags": {"sf": True}},
            hints=[
                "SF is the sign bit of the result.",
                "Subtract 1 from 0.",
                "0 - 1 is -1, the sign bit is set.",
            ],
        ),
        Challenge(
            id="ch8",
            challenge_type="registers",
            difficulty="medium",
            title="Exchange without XCHG",
            spec="Swap the values in RAX and RBX without using an XCHG instruction.",
            program="mov rax, 1\nmov rbx, 2\nmov rcx, rax\nmov rax, rbx\nmov rbx, rcx",
            expected={"registers": {"rax": 2, "rbx": 1}},
            hints=[
                "You need a temporary register.",
                "Copy RAX to a temp, then RAX = RBX, then RBX = temp.",
                "mov rcx, rax; mov rax, rbx; mov rbx, rcx.",
            ],
        ),
        Challenge(
            id="ch9",
            challenge_type="optimization",
            difficulty="hard",
            title="Multiply the cheap way",
            spec="Compute RAX = RAX * 8 with a single instruction (no imul).",
            program="mov rax, 3\nshl rax, 3",
            expected={"registers": {"rax": 24}},
            hints=[
                "A negative power-of-two shift multiplies by 2^n.",
                "8 = 2^3, so shift left three times.",
                "shl rax, 3 multiplies by 8.",
            ],
        ),
        Challenge(
            id="ch10",
            challenge_type="prediction",
            difficulty="easy",
            title="Read the register",
            spec="Start with 'mov rax, 7'. Then MOV the answer from the low byte "
            "register AL. What is RAX after 'mov rbx, rax'?",
            program="mov eax, 0x7F\nmov al, 0x42\nmov rbx, rax",
            expected={"registers": {"rax": 0x42, "rbx": 0x42}},
            hints=[
                "Writing AL touches only the low byte of RAX.",
                "0x7F stays, but AL overwrites the low byte.",
                "RAX becomes 0x42; MOV copies the whole register.",
            ],
        ),
        Challenge(
            id="ch11",
            challenge_type="stack",
            difficulty="hard",
            title="Pop to RAX",
            spec="Push 77 onto the stack, then pop it back into RAX.",
            program="mov rax, 77\npush rax\nxor rax, rax\npop rax",
            expected={"registers": {"rax": 77}},
            hints=[
                "PUSH places a value on the stack (RSP decreases).",
                "POP fetches it back (RSP increases).",
                "mov rax, 77; push rax; xor rax, rax; pop rax.",
            ],
        ),
    ]
