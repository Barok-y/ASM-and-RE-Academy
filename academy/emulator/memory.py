"""Segmented memory model for the x86-64 emulator."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence

from unicorn import UC_PROT_ALL, Uc


@dataclass(frozen=True)
class Segment:
    name: str
    base: int
    size: int
    kind: str
    writable: bool = True
    perms: int = UC_PROT_ALL


class MemoryModel:
    def __init__(self, segments: Sequence[Segment]):
        self._segments = list(segments)
        self._by_name: Dict[str, Segment] = {s.name: s for s in self._segments}

    @property
    def segments(self) -> List[Segment]:
        return list(self._segments)

    def segment(self, name: str) -> Segment:
        return self._by_name[name]

    def segment_for(self, addr: int) -> Optional[Segment]:
        for s in self._segments:
            if s.base <= addr < s.base + s.size:
                return s
        return None

    def map_into(self, uc: Uc) -> None:
        for s in self._segments:
            uc.mem_map(s.base, s.size, s.perms)

    def read(self, uc: Uc, addr: int, size: int) -> bytes:
        return bytes(uc.mem_read(addr, size))

    def write(self, uc: Uc, addr: int, data: bytes) -> None:
        uc.mem_write(addr, data)

    def snapshot(self, uc: Uc) -> Dict[str, bytes]:
        return {s.name: self.read(uc, s.base, s.size) for s in self._segments if s.writable}
