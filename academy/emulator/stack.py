"""Stack model view over the emulator memory."""

from __future__ import annotations

from typing import List, Tuple

from unicorn import Uc
from unicorn.x86_const import UC_X86_REG_RSP

from .memory import MemoryModel


class Stack:
    def __init__(self, memory: MemoryModel, uc: Uc):
        self._memory = memory
        self._uc = uc

    def read_qword(self, addr: int) -> int:
        return int.from_bytes(self._memory.read(self._uc, addr, 8), "little")

    def peek(self, offset: int = 0, size: int = 8) -> bytes:
        rsp = self._uc.reg_read(UC_X86_REG_RSP)
        return self._memory.read(self._uc, rsp + offset, size)

    def view(self, count: int = 16) -> List[Tuple[int, bytes]]:
        rsp = self._uc.reg_read(UC_X86_REG_RSP)
        rows: List[Tuple[int, bytes]] = []
        for i in range(count):
            addr = rsp + i * 8
            seg = self._memory.segment_for(addr)
            if seg is None:
                break
            end = min(addr + 8, seg.base + seg.size)
            rows.append((addr, self._memory.read(self._uc, addr, end - addr)))
        return rows
