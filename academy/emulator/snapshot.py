"""State snapshots and diffs for the emulator."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple


def _changed_ranges(old: bytes, new: bytes) -> List[Tuple[int, bytes, bytes]]:
    ranges: List[Tuple[int, bytes, bytes]] = []
    i = 0
    n = min(len(old), len(new))
    while i < n:
        if old[i] != new[i]:
            j = i
            while j < n and old[j] != new[j]:
                j += 1
            ranges.append((i, old[i:j], new[i:j]))
            i = j
        else:
            i += 1
    return ranges


@dataclass
class StateDiff:
    registers: Dict[str, Tuple[int, int]] = field(default_factory=dict)
    flags: Dict[str, Tuple[bool, bool]] = field(default_factory=dict)
    memory: Dict[str, List[Tuple[int, bytes, bytes]]] = field(default_factory=dict)
    output_changed: bool = False

    @property
    def changed(self) -> bool:
        return bool(self.registers or self.flags or self.memory or self.output_changed)


@dataclass
class StateSnapshot:
    registers: Dict[str, int]
    flags: Dict[str, bool]
    rflags_raw: int
    segments: Dict[str, bytes]
    output: bytes
    status: str
    exit_code: int | None = None
    step_index: int = 0

    def diff(self, previous: "StateSnapshot") -> StateDiff:
        registers: Dict[str, Tuple[int, int]] = {}
        for name in sorted(set(self.registers) | set(previous.registers)):
            old = previous.registers.get(name, 0)
            new = self.registers.get(name, 0)
            if old != new:
                registers[name] = (old, new)
        flags: Dict[str, Tuple[bool, bool]] = {}
        for name in self.flags:
            if self.flags[name] != previous.flags.get(name, False):
                flags[name] = (previous.flags.get(name, False), self.flags[name])
        memory: Dict[str, List[Tuple[int, bytes, bytes]]] = {}
        for seg, new_bytes in self.segments.items():
            old_bytes = previous.segments.get(seg)
            if old_bytes is None:
                continue
            changed = _changed_ranges(old_bytes, new_bytes)
            if changed:
                memory[seg] = changed
        return StateDiff(
            registers=registers,
            flags=flags,
            memory=memory,
            output_changed=self.output != previous.output,
        )
