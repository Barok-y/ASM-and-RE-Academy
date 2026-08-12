"""Unicorn-backed x86-64 execution engine with single-step, breakpoints,
watchpoints, reverse stepping, and state snapshots."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Dict, List, Optional, Set, Tuple

from capstone import CS_ARCH_X86, CS_MODE_64, Cs, CsInsn
from keystone import KS_ARCH_X86, KS_MODE_64, Ks, KsError
from unicorn import (
    UC_ARCH_X86,
    UC_ERR_FETCH_UNMAPPED,
    UC_MODE_64,
    Uc,
    UcError,
)

from . import flags as fflags
from . import registers as regs
from .memory import MemoryModel, Segment
from .snapshot import StateSnapshot
from .stack import Stack

STATUS_READY = "ready"
STATUS_RUNNING = "running"
STATUS_BREAKPOINT = "breakpoint"
STATUS_EXITED = "exited"
STATUS_ERROR = "error"
STATUS_HALTED = "halted"

DEFAULT_SEGMENTS: Sequence[Segment] = (
    Segment("text", 0x400000, 0x100000, kind="text", writable=False),
    Segment("data", 0x600000, 0x10000, kind="data"),
    Segment("bss", 0x610000, 0x10000, kind="bss"),
    Segment("heap", 0x700000, 0x10000, kind="heap"),
    Segment("stack", 0x7FFFF00000, 0x20000, kind="stack"),
)

STACK_TOP = 0x7FFFF00000 + 0x20000

_SYSCALL_EXIT = (60, 231)
_SYSCALL_WRITE = 1


class ExecutionHalted(RuntimeError):
    pass


class Executor:
    def __init__(
        self,
        segments: Sequence[Segment] = DEFAULT_SEGMENTS,
        stack_top: int = STACK_TOP,
        max_history: int = 200,
    ):
        self._segments = segments
        self._memory = MemoryModel(segments)
        self._stack_top = stack_top
        self._max_history = max_history
        self._cs = Cs(CS_ARCH_X86, CS_MODE_64)
        self._cs.detail = True
        self._ks = Ks(KS_ARCH_X86, KS_MODE_64)
        self._breakpoints: Set[int] = set()
        self._watchpoints: Dict[int, int] = {}
        self._watch_prev: Dict[int, bytes] = {}
        self.watch_events: List[Tuple[int, bytes, bytes]] = []
        self._error: Optional[str] = None
        self.exit_code: Optional[int] = None
        self._loaded: Optional[Tuple[bytes, int]] = None
        self.last_instruction: Optional[str] = None
        self._new_engine()
        self.reset()

    def _new_engine(self) -> None:
        self._uc = Uc(UC_ARCH_X86, UC_MODE_64)
        self._memory.map_into(self._uc)
        self._reset_registers()

    def _reset_registers(self) -> None:
        for name in regs.BASE_REGISTERS:
            regs.write_register(self._uc, name, 0)
        fflags.write_rflags(self._uc, 0)
        regs.write_register(self._uc, "rsp", self._stack_top - 0x100)

    @property
    def loaded(self) -> bool:
        return self._loaded is not None

    def reset(self) -> None:
        self._new_engine()
        self._output: bytes = b""
        self._history: List[StateSnapshot] = []
        self._watch_prev = {}
        self.watch_events = []
        self._error = None
        self.exit_code = None
        self._step_index = 0
        self.status = STATUS_READY
        self.last_instruction = None
        if self._loaded is not None:
            code, entry = self._loaded
            self._memory.write(self._uc, self._memory.segment("text").base, code)
            regs.write_register(self._uc, "rip", entry)
        self._history = [self._snapshot()]

    def load_asm(self, source: str, entry: int | None = None) -> None:
        try:
            encoding, _ = self._ks.asm(source)
        except KsError as exc:
            raise ValueError(f"assembly failed: {exc}") from exc
        if not encoding:
            raise ValueError("assembly produced no code")
        self.load_bytes(bytes(encoding), entry)

    def load_bytes(self, code: bytes, entry: int | None = None) -> None:
        text = self._memory.segment("text")
        if len(code) > text.size:
            raise ValueError("code too large for text segment")
        if entry is None:
            entry = text.base
        self._loaded = (code, entry)
        self.reset()

    def snapshot(self) -> StateSnapshot:
        return self._snapshot()

    def _snapshot(self) -> StateSnapshot:
        return StateSnapshot(
            registers=regs.read_all_registers(self._uc),
            flags=fflags.read_flags(self._uc),
            rflags_raw=fflags.read_rflags(self._uc),
            segments=self._memory.snapshot(self._uc),
            output=self._output,
            status=self.status,
            exit_code=self.exit_code,
            step_index=self._step_index,
        )

    def step(self) -> StateSnapshot:
        if self.status in (STATUS_EXITED, STATUS_ERROR, STATUS_HALTED):
            raise ExecutionHalted(f"cannot step in status {self.status!r}")
        rip = self.get_register("rip")
        executed = None
        if rip in self._breakpoints:
            self.status = STATUS_BREAKPOINT
        else:
            insn = self._disassemble_at(rip)
            if insn is None:
                self.status = STATUS_HALTED
            elif insn.mnemonic in ("syscall", "int"):
                self.status = STATUS_RUNNING
                self._exec_syscall(insn)
                executed = insn
            else:
                self.status = STATUS_RUNNING
                try:
                    self._uc.emu_start(rip, 0, 0, count=1)
                except UcError as exc:
                    if exc.errno == UC_ERR_FETCH_UNMAPPED:
                        self.status = STATUS_HALTED
                    else:
                        self.status = STATUS_ERROR
                        self._error = str(exc)
                else:
                    executed = insn
        if executed is not None:
            self.last_instruction = f"{executed.mnemonic} {executed.op_str}".strip()
        self._step_index += 1
        snap = self._snapshot()
        self._append_history(snap)
        self._check_watchpoints()
        return snap

    def step_over(self, max_steps: int = 10_000) -> StateSnapshot:
        insn = self._disassemble_at(self.get_register("rip"))
        if insn is not None and insn.mnemonic == "call":
            next_addr = insn.address + insn.size
            steps = 0
            while self.status == STATUS_RUNNING and self.get_register("rip") != next_addr:
                self.step()
                steps += 1
                if steps > max_steps:
                    break
        else:
            self.step()
        return self._snapshot()

    def step_out(self, max_steps: int = 10_000) -> StateSnapshot:
        steps = 0
        while self.status == STATUS_RUNNING:
            insn = self._disassemble_at(self.get_register("rip"))
            if insn is not None and insn.mnemonic == "ret":
                self.step()
                break
            self.step()
            steps += 1
            if steps > max_steps:
                break
        return self._snapshot()

    def run(self, max_steps: int = 1_000_000) -> StateSnapshot:
        self.status = STATUS_RUNNING
        steps = 0
        while self.status == STATUS_RUNNING:
            rip = self.get_register("rip")
            if rip in self._breakpoints:
                self.status = STATUS_BREAKPOINT
                break
            steps += 1
            if steps > max_steps:
                self.status = STATUS_ERROR
                self._error = f"step limit {max_steps} exceeded"
                break
            self.step()
        return self._snapshot()

    def step_back(self) -> Optional[StateSnapshot]:
        if len(self._history) < 2:
            return None
        self._history.pop()
        previous = self._history[-1]
        self._restore(previous)
        return previous

    def _restore(self, snap: StateSnapshot) -> None:
        for name, value in snap.registers.items():
            regs.write_register(self._uc, name, value)
        fflags.write_rflags(self._uc, snap.rflags_raw)
        for seg_name, data in snap.segments.items():
            self._memory.write(self._uc, self._memory.segment(seg_name).base, data)
        self._output = snap.output
        self.status = snap.status
        self.exit_code = snap.exit_code
        self._step_index = snap.step_index

    def _append_history(self, snap: StateSnapshot) -> None:
        self._history.append(snap)
        if len(self._history) > self._max_history:
            del self._history[: len(self._history) - self._max_history]

    def history(self) -> List[StateSnapshot]:
        return list(self._history)

    def _exec_syscall(self, insn: CsInsn) -> None:
        if insn.mnemonic == "int":
            number = self.get_register("eax")
            a1 = self.get_register("ebx")
            a2 = self.get_register("ecx")
            a3 = self.get_register("edx")
        else:
            number = self.get_register("rax")
            a1 = self.get_register("rdi")
            a2 = self.get_register("rsi")
            a3 = self.get_register("rdx")
        if number in _SYSCALL_EXIT:
            self.exit_code = a1 & 0xFF
            self.status = STATUS_EXITED
            return
        if number == _SYSCALL_WRITE and a1 in (1, 2):
            try:
                chunk = self._memory.read(self._uc, a2, a3)
            except UcError:
                chunk = b""
            self._output = self._output + chunk
        regs.write_register(self._uc, "rip", self.get_register("rip") + insn.size)

    def _disassemble_at(self, addr: int) -> Optional[CsInsn]:
        try:
            code = self._memory.read(self._uc, addr, 15)
        except UcError:
            return None
        for insn in self._cs.disasm(code, addr, 1):
            return insn
        return None

    def current_instruction(self) -> str:
        insn = self._disassemble_at(self.get_register("rip"))
        if insn is None:
            return "<invalid>"
        return f"{insn.mnemonic} {insn.op_str}".strip()

    def disassemble(self, addr: int | None = None, count: int = 10) -> List[str]:
        start = addr if addr is not None else self.get_register("rip")
        code = self._memory.read(self._uc, start, 15 * count)
        lines: List[str] = []
        for insn in self._cs.disasm(code, start):
            if len(lines) >= count:
                break
            lines.append(f"{insn.address:016x}  {insn.mnemonic} {insn.op_str}".rstrip())
        return lines

    def get_register(self, name: str) -> int:
        return regs.read_register(self._uc, name)

    def set_register(self, name: str, value: int) -> None:
        regs.write_register(self._uc, name, value)

    def get_flag(self, name: str) -> bool:
        return fflags.read_flags(self._uc)[name]

    def registers(self) -> Dict[str, int]:
        return regs.read_all_registers(self._uc)

    def flags(self) -> Dict[str, bool]:
        return fflags.read_flags(self._uc)

    def stack_view(self, count: int = 16) -> List[Tuple[int, bytes]]:
        return Stack(self._memory, self._uc).view(count)

    def read_memory(self, name_or_addr: str | int, size: int) -> bytes:
        base = self._resolve(name_or_addr)
        return self._memory.read(self._uc, base, size)

    def write_memory(self, name_or_addr: str | int, data: bytes) -> None:
        base = self._resolve(name_or_addr)
        self._memory.write(self._uc, base, data)

    def write_string(self, name_or_addr: str | int, text: str) -> None:
        self.write_memory(name_or_addr, text.encode("utf-8") + b"\x00")

    def segment_base(self, name: str) -> int:
        return self._memory.segment(name).base

    def _resolve(self, name_or_addr: str | int) -> int:
        if isinstance(name_or_addr, str):
            return self._memory.segment(name_or_addr).base
        return name_or_addr

    def add_breakpoint(self, addr: int) -> None:
        self._breakpoints.add(addr)

    def remove_breakpoint(self, addr: int) -> None:
        self._breakpoints.discard(addr)

    @property
    def breakpoints(self) -> List[int]:
        return sorted(self._breakpoints)

    def add_watch(self, addr: int, size: int = 8) -> None:
        self._watchpoints[addr] = size
        self._watch_prev[addr] = self._memory.read(self._uc, addr, size)

    def remove_watch(self, addr: int) -> None:
        self._watchpoints.pop(addr, None)
        self._watch_prev.pop(addr, None)

    @property
    def watchpoints(self) -> Dict[int, int]:
        return dict(self._watchpoints)

    def _check_watchpoints(self) -> None:
        self.watch_events = []
        for addr, size in self._watchpoints.items():
            current = self._memory.read(self._uc, addr, size)
            previous = self._watch_prev[addr]
            if current != previous:
                self.watch_events.append((addr, previous, current))
                self._watch_prev[addr] = current

    @property
    def output(self) -> bytes:
        return self._output
