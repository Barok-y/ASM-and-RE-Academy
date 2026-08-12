"""x86-64 flags (RFLAGS) model."""

from __future__ import annotations

from typing import Dict

from unicorn import Uc
from unicorn.x86_const import UC_X86_REG_RFLAGS

FLAG_BITS: Dict[str, int] = {
    "cf": 0,
    "pf": 2,
    "af": 4,
    "zf": 6,
    "sf": 7,
    "tf": 8,
    "if": 9,
    "df": 10,
    "of": 11,
}

FLAG_NAMES = tuple(FLAG_BITS)


def read_rflags(uc: Uc) -> int:
    return uc.reg_read(UC_X86_REG_RFLAGS)


def write_rflags(uc: Uc, value: int) -> None:
    uc.reg_write(UC_X86_REG_RFLAGS, value & 0xFFFFFFFFFFFFFFFF)


def read_flags(uc: Uc) -> Dict[str, bool]:
    rflags = read_rflags(uc)
    return {name: bool(rflags & (1 << bit)) for name, bit in FLAG_BITS.items()}
