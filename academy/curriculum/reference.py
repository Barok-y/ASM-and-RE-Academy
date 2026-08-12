"""Reference cheat sheet: quick lookups for common Intel x86-64
instructions, registers, and flags shown inside lessons."""

from __future__ import annotations

from typing import Dict

INSTRUCTIONS: Dict[str, str] = {
    "mov": "copy source into destination: mov rax, 5 ; sub-registers write low bits",
    "lea": "load effective address without dereferencing: lea rax, [rbx+4]",
    "add": "dest = dest + src; sets ZF/SF/CF/OF",
    "sub": "dest = dest - src; sets ZF/SF/CF/OF",
    "inc": "increment by 1",
    "dec": "decrement by 1",
    "imul": "signed multiply",
    "div": "unsigned divide; quotient in RAX, remainder in RDX",
    "and": "bitwise AND",
    "or": "bitwise OR",
    "xor": "bitwise XOR (xor reg,reg zeroes a register)",
    "not": "bitwise NOT",
    "shl": "shift left; bits shift out into CF",
    "shr": "logical shift right",
    "sar": "arithmetic (sign-preserving) shift right",
    "movzx": "move with zero extension: movzx rax, byte ptr [rbx]",
    "movsx": "move with sign extension",
    "push": "push onto stack; decrements RSP",
    "pop": "pop off stack; increments RSP",
    "call": "push RIP then jump to operand",
    "ret": "pop return address into RIP",
    "jmp": "unconditional jump",
    "je": "jump if equal (ZF=1)",
    "jne": "jump if not equal (ZF=0)",
    "jg": "jump if greater (signed)",
    "jl": "jump if less (signed)",
    "jge": "jump if >= (signed)",
    "jle": "jump if <= (signed)",
    "jz": "jump if zero (ZF=1)",
    "jnz": "jump if not zero (ZF=0)",
    "js": "jump if sign (SF=1)",
    "jns": "jump if not sign",
    "jo": "jump if overflow (OF=1)",
    "jno": "jump if not overflow",
    "jc": "jump if carry (CF=1)",
    "jnc": "jump if not carry",
    "test": "AND that only sets flags (no result write)",
    "syscall": "invoke the kernel; number in RAX, args RDI/RSI/RDX",
}

REGISTERS: Dict[str, str] = {
    "rax/eax/ax/al": "accumulator: results and syscall number return",
    "rbx/ebx/bx/bl": "caller-saved general register",
    "rcx/ecx": "loop counter / syscall arg",
    "rdx/edx": "syscall arg 3 / division remainder",
    "rsi/esi": "syscall arg 2 / data register",
    "rdi/edi": "syscall arg 1 / data register",
    "rsp": "stack pointer — points to top of stack (grows DOWN)",
    "rbp": "frame pointer: base of current stack frame",
    "rip": "instruction pointer — address of next instruction",
    "r8-r15": "extended general-purpose registers",
    "rflags": "condition flags register",
}

FLAGS: Dict[str, str] = {
    "ZF": "Zero Flag — set when the last result was zero",
    "SF": "Sign Flag — set when the last result was negative",
    "CF": "Carry Flag — set on unsigned overflow",
    "OF": "Overflow Flag — set on signed overflow",
    "PF": "Parity Flag — set when low byte has even parity",
    "AF": "Auxiliary Flag — BCD carry between low nibble bits",
    "DF": "Direction Flag — controls string instruction direction",
}

SYSCALLS: Dict[str, str] = {
    "60": "exit: RAX=60, RDI=exit code",
    "1": "write: RAX=1, RDI=fd, RSI=buffer, RDX=length",
    "0": "read: RAX=0, RDI=fd, RSI=buffer, RDX=length",
    "2": "open: RAX=2, RDI=path, RSI=flags",
    "3": "close: RAX=3, RDI=fd",
    "9": "mmap: RAX=9, RDI=addr, RSI=length, RDX=prot",
    "59": "execve: RAX=59, RDI=path, RSI=argv, RDX=envp",
}


def lookup(keyword: str) -> str:
    """Return the best matching cheat-sheet entry for a keyword, or ''."""
    k = keyword.strip().lower()
    if k in INSTRUCTIONS:
        return f"{k}: {INSTRUCTIONS[k]}"
    if k.upper() in FLAGS:
        return f"{k.upper()}: {FLAGS[k.upper()]}"
    for regs, desc in REGISTERS.items():
        if k in regs.split("/"):
            return f"{regs}: {desc}"
    if k.isdigit() and k in SYSCALLS:
        return f"syscall {k}: {SYSCALLS[k]}"
    return ""


def cheat_sheet_text() -> str:
    lines = ["INSTRUCTIONS", "------------"]
    for name, desc in INSTRUCTIONS.items():
        lines.append(f"  {name:8s} {desc}")
    lines.append("\nREGISTERS")
    for name, desc in REGISTERS.items():
        lines.append(f"  {name:24s} {desc}")
    lines.append("\nFLAGS")
    for name, desc in FLAGS.items():
        lines.append(f"  {name:6s} {desc}")
    lines.append("\nSYSCALLS")
    for num, desc in SYSCALLS.items():
        lines.append(f"  {num:4s} {desc}")
    return "\n".join(lines)
