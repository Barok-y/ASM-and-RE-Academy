"""Human-readable rendering of emulator state and state changes."""

from __future__ import annotations

from typing import Dict, List, Sequence

from academy.emulator import StateSnapshot

REGISTER_ORDER = (
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

FLAG_ORDER = ("cf", "pf", "af", "zf", "sf", "of", "df", "if", "tf")


def fmt_hex(value: int) -> str:
    return f"0x{value & 0xFFFFFFFFFFFFFFFF:x}"


def format_registers(registers: Dict[str, int]) -> str:
    lines = []
    for name in REGISTER_ORDER:
        lines.append(f"{name:4s} = {fmt_hex(registers.get(name, 0))}")
    return "\n".join(lines)


def format_flags(flags: Dict[str, bool]) -> str:
    return " ".join(f"{name.upper()}={1 if flags.get(name) else 0}" for name in FLAG_ORDER)


def hexdump(data: bytes, base: int = 0, width: int = 16) -> str:
    lines: List[str] = []
    for offset in range(0, len(data), width):
        chunk = data[offset : offset + width]
        hex_part = " ".join(f"{b:02x}" for b in chunk)
        hex_part = hex_part.ljust(width * 3 - 1)
        ascii_part = "".join(chr(b) if 32 <= b < 127 else "." for b in chunk)
        lines.append(f"{base + offset:016x}  {hex_part}  {ascii_part}")
    return "\n".join(lines)


def explain_diff(previous: StateSnapshot, new: StateSnapshot) -> str:
    diff = new.diff(previous)
    parts: List[str] = []
    if diff.registers:
        rendered = ", ".join(
            f"{name} {fmt_hex(old)} -> {fmt_hex(value)}"
            for name, (old, value) in sorted(diff.registers.items())
        )
        parts.append(rendered)
    if diff.flags:
        rendered = ", ".join(
            f"{name.upper()} {'set' if value else 'cleared'}"
            for name, (_, value) in sorted(diff.flags.items())
        )
        parts.append(rendered)
    for seg in sorted(diff.memory):
        count = len(diff.memory[seg])
        parts.append(f"{seg}: {count} byte-range(s) written")
    if diff.output_changed:
        parts.append(f"output: {new.output!r}")
    return "; ".join(parts) if parts else "no state change"


def explain_steps(snapshots: Sequence[StateSnapshot]) -> List[str]:
    lines = []
    for i in range(1, len(snapshots)):
        lines.append(explain_diff(snapshots[i - 1], snapshots[i]))
    return lines
