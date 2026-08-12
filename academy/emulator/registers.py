"""x86-64 general purpose register model with sub-register access."""

from __future__ import annotations

from typing import Dict, Tuple

from unicorn import Uc
from unicorn.x86_const import (
    UC_X86_REG_R8,
    UC_X86_REG_R9,
    UC_X86_REG_R10,
    UC_X86_REG_R11,
    UC_X86_REG_R12,
    UC_X86_REG_R13,
    UC_X86_REG_R14,
    UC_X86_REG_R15,
    UC_X86_REG_RAX,
    UC_X86_REG_RBP,
    UC_X86_REG_RBX,
    UC_X86_REG_RCX,
    UC_X86_REG_RDI,
    UC_X86_REG_RDX,
    UC_X86_REG_RIP,
    UC_X86_REG_RSI,
    UC_X86_REG_RSP,
)

_UC_REGS: Dict[str, int] = {
    "rax": UC_X86_REG_RAX,
    "rbx": UC_X86_REG_RBX,
    "rcx": UC_X86_REG_RCX,
    "rdx": UC_X86_REG_RDX,
    "rsi": UC_X86_REG_RSI,
    "rdi": UC_X86_REG_RDI,
    "rbp": UC_X86_REG_RBP,
    "rsp": UC_X86_REG_RSP,
    "rip": UC_X86_REG_RIP,
    "r8": UC_X86_REG_R8,
    "r9": UC_X86_REG_R9,
    "r10": UC_X86_REG_R10,
    "r11": UC_X86_REG_R11,
    "r12": UC_X86_REG_R12,
    "r13": UC_X86_REG_R13,
    "r14": UC_X86_REG_R14,
    "r15": UC_X86_REG_R15,
}

BASE_REGISTERS: Tuple[str, ...] = (
    "rax",
    "rbx",
    "rcx",
    "rdx",
    "rsi",
    "rdi",
    "rbp",
    "rsp",
    "rip",
    "r8",
    "r9",
    "r10",
    "r11",
    "r12",
    "r13",
    "r14",
    "r15",
)


def _build_table() -> Dict[str, Tuple[str, int, int]]:
    table: Dict[str, Tuple[str, int, int]] = {}
    legacy = [
        ("rax", True),
        ("rbx", True),
        ("rcx", True),
        ("rdx", True),
        ("rsi", False),
        ("rdi", False),
        ("rbp", False),
        ("rsp", False),
    ]
    for base, has_high in legacy:
        table[base] = (base, 0xFFFFFFFFFFFFFFFF, 0)
        table["e" + base[1:]] = (base, 0xFFFFFFFF, 0)
        word = base[1:]
        table[word] = (base, 0xFFFF, 0)
        low_name = word[0] + "l" if has_high else word + "l"
        table[low_name] = (base, 0xFF, 0)
        if has_high:
            table[word[0] + "h"] = (base, 0xFF00, 8)
    for i in range(8, 16):
        name = f"r{i}"
        table[name] = (name, 0xFFFFFFFFFFFFFFFF, 0)
        table[f"r{i}d"] = (name, 0xFFFFFFFF, 0)
        table[f"r{i}w"] = (name, 0xFFFF, 0)
        table[f"r{i}b"] = (name, 0xFF, 0)
    table["rip"] = ("rip", 0xFFFFFFFFFFFFFFFF, 0)
    return table


REGISTER_TABLE = _build_table()


def read_register(uc: Uc, name: str) -> int:
    base, mask, shift = REGISTER_TABLE[name.lower()]
    full = uc.reg_read(_UC_REGS[base])
    return (full >> shift) & (mask >> shift)


def write_register(uc: Uc, name: str, value: int) -> None:
    base, mask, shift = REGISTER_TABLE[name.lower()]
    if mask == 0xFFFFFFFF:
        uc.reg_write(_UC_REGS[base], value & 0xFFFFFFFF)
    else:
        full = uc.reg_read(_UC_REGS[base])
        uc.reg_write(_UC_REGS[base], (full & ~mask) | ((value << shift) & mask))


def read_all_registers(uc: Uc) -> Dict[str, int]:
    return {name: uc.reg_read(_UC_REGS[name]) for name in BASE_REGISTERS}
