from __future__ import annotations

import shlex
from dataclasses import dataclass
from typing import List

from academy.emulator import (
    STATUS_ERROR,
    STATUS_EXITED,
    STATUS_HALTED,
    Executor,
)

from .explain import explain_diff, explain_steps, format_flags, format_registers, hexdump


@dataclass
class CommandResult:
    command: str
    text: str
    explanation: str = ""


class Sandbox:
    COMMANDS = (
        "run",
        "step",
        "next",
        "continue",
        "reset",
        "registers",
        "flags",
        "stack",
        "memory",
        "break",
        "watch",
        "disassemble",
        "hexdump",
        "input",
        "loadelf",
        "trace",
        "explain",
        "rewind",
        "help",
        "demo",
    )

    def __init__(self, executor: Executor | None = None):
        self.executor = executor or Executor()

    def execute(self, cmdline: str) -> CommandResult:
        parts = shlex.split(cmdline)
        if not parts:
            raise ValueError("empty command")
        command = parts[0].lower()
        if command not in self.COMMANDS:
            raise ValueError(f"unknown command: {command}")
        return getattr(self, "cmd_" + command)(*parts[1:])

    def cmd_help(self) -> CommandResult:
        text = (
            "available commands:\n  " + "\n  ".join(self.COMMANDS)
            + "\nusage: <command> [args]  e.g. memory 0x600000 16, step 3, break 0x400000"
        )
        return CommandResult("help", text)

    def cmd_demo(self) -> CommandResult:
        """Run a short guided walkthrough so a new user sees the sandbox explain
        a real program end-to-end."""
        if not self.executor.loaded:
            self.executor.load_asm(
                "mov rax, 10\nadd rax, 5\nsub rax, 3\nmov rdi, rax\n"
                "mov rax, 60\nsyscall"
            )
        lines = [
            "DEMO: watch what a tiny program does to the machine.",
            "",
            "1) disassemble: here is your program in CPU bytes",
        ]
        lines.extend(f"   {d}" for d in self.executor.disassemble(count=10))
        self.executor.reset()
        self.executor.step()
        lines.append("")
        lines.append(
            "2) stepped one instruction: 'mov rax, 10' ran — RAX is now 10"
        )
        lines.append(f"   {format_registers(self.executor.registers())}")
        self.executor.step()
        lines.append("")
        lines.append("3) another step: 'add rax, 5' ran — RAX is now 15")
        lines.append(f"   {format_registers(self.executor.registers())}")
        self.executor.step()
        lines.append("")
        lines.append("4) 'sub rax, 3' — RAX is now 12")
        lines.append(f"   {format_registers(self.executor.registers())}")
        lines.append("")
        lines.append("5) 'mov rax, 60; syscall' — the program EXITS (status exited)")
        self.executor.run()
        lines.append(f"   status: {self.executor.status}")
        lines.append("")
        lines.append(
            "That is all the sandbox does: move one instruction, inspect the "
            "change, repeat. Try step, registers, flags, memory, stack yourself."
        )
        return CommandResult("demo", "\n".join(lines))

    def _status_line(self) -> str:
        return f"status: {self.executor.status}"

    def _output_line(self) -> str:
        output = self.executor.output
        if not output:
            return "(no output)"
        return f"output: {output!r}"

    def cmd_run(self) -> CommandResult:
        before = self.executor.snapshot()
        self.executor.run()
        snap = self.executor.snapshot()
        text = f"{self._output_line()}\n{self._status_line()}"
        explanation = explain_diff(before, snap)
        return CommandResult("run", text, explanation)

    def cmd_step(self, count: str = "1") -> CommandResult:
        try:
            n = int(count)
        except ValueError as exc:
            raise ValueError(f"invalid step count: {count!r}") from exc
        if n < 1:
            raise ValueError("step count must be >= 1")
        lines: List[str] = []
        for i in range(1, n + 1):
            if self.executor.status in (STATUS_EXITED, STATUS_ERROR, STATUS_HALTED):
                lines.append(f"cannot step: status is {self.executor.status}")
                break
            self.executor.step()
            hist = self.executor.history()
            detail = explain_diff(hist[-2], hist[-1]) if len(hist) >= 2 else ""
            lines.append(f"[{i}] {self.executor.last_instruction or '<none>'}")
            if detail:
                lines.append(f"    {detail}")
        return CommandResult("step", "\n".join(lines))

    def cmd_next(self) -> CommandResult:
        before = self.executor.history()
        self.executor.step_over()
        return self._stepping_result("next", before)

    def cmd_continue(self) -> CommandResult:
        return self.cmd_run()

    def cmd_reset(self) -> CommandResult:
        self.executor.reset()
        return CommandResult("reset", "execution reset")

    def cmd_registers(self) -> CommandResult:
        return CommandResult("registers", format_registers(self.executor.registers()))

    def cmd_flags(self) -> CommandResult:
        return CommandResult("flags", format_flags(self.executor.flags()))

    def cmd_stack(self, count: str = "16") -> CommandResult:
        rows = self.executor.stack_view(int(count))
        lines = []
        for addr, data in rows:
            lines.append(f"{addr:016x}  {data.hex()}")
        return CommandResult("stack", "\n".join(lines) or "(stack empty)")

    def cmd_memory(self, addr: str, size: str = "16") -> CommandResult:
        base = self._parse_addr(addr)
        data = self.executor.read_memory(base, int(size))
        return CommandResult("memory", hexdump(data, base=base))

    def cmd_hexdump(self, addr: str, size: str = "16") -> CommandResult:
        return self.cmd_memory(addr, size)

    def cmd_input(self, data: str) -> CommandResult:
        self.executor.set_input(data.encode())
        return CommandResult("input", f"stdin set to {data!r}")

    def cmd_loadelf(self, path: str) -> CommandResult:
        try:
            self.executor.load_elf(path)
        except Exception as exc:
            return CommandResult("loadelf", f"failed to load {path}: {exc}")
        info = self.executor.elf_info() or {}
        imports = ", ".join(str(i) for i in info.get("imports", []) or [])
        lines = [
            f"loaded ELF: {info.get('path')}",
            f"  entry:   {info.get('entry', 0):#x}",
            f"  type:    {'PIE' if info.get('pie') else 'ET_EXEC'}",
            f"  imports: {imports or '(none)'}",
            f"  status:  {self.executor.status}",
            "",
            "hint: 'run' executes it; feed it stdin with 'input <bytes>' before "
            "running, and 'registers' / 'disassemble' inspect it.",
        ]
        return CommandResult("loadelf", "\n".join(lines))

    def cmd_disassemble(self, count: str = "10", addr: str = "") -> CommandResult:
        n = int(count)
        lines = (
            self.executor.disassemble(count=n)
            if not addr
            else self.executor.disassemble(addr=self._parse_addr(addr), count=n)
        )
        return CommandResult("disassemble", "\n".join(lines))

    def cmd_break(self, addr: str = "") -> CommandResult:
        if addr:
            self.executor.add_breakpoint(self._parse_addr(addr))
            return CommandResult("break", f"breakpoint set at {addr}")
        lines = [f"0x{b:016x}" for b in self.executor.breakpoints]
        return CommandResult("break", "\n".join(lines) or "(no breakpoints)")

    def cmd_watch(self, addr: str = "", size: str = "8") -> CommandResult:
        if addr:
            self.executor.add_watch(self._parse_addr(addr), int(size))
            return CommandResult("watch", f"watchpoint set at {addr}")
        lines = [f"0x{a:016x} (size {s})" for a, s in self.executor.watchpoints.items()]
        events = [
            f"0x{a:016x}: {old.hex()} -> {new.hex()}"
            for a, old, new in self.executor.watch_events
        ]
        if events:
            lines.append("events:")
            lines.extend(f"  {e}" for e in events)
        return CommandResult("watch", "\n".join(lines) or "(no watchpoints)")

    def cmd_trace(self, max_steps: str = "50") -> CommandResult:
        limit = int(max_steps)
        snapshots = [self.executor.snapshot()]
        steps = 0
        while steps < limit:
            if self.executor.status in (STATUS_EXITED, STATUS_ERROR, STATUS_HALTED):
                break
            if self.executor.get_register("rip") in self.executor.breakpoints:
                break
            self.executor.step()
            steps += 1
            snapshots.append(self.executor.snapshot())
        lines = [f"[{i}] {d}" for i, d in enumerate(explain_steps(snapshots), 1)]
        return CommandResult("trace", "\n".join(lines) or "(no steps)")

    def cmd_explain(self) -> CommandResult:
        hist = self.executor.history()
        if len(hist) >= 2:
            detail = explain_diff(hist[-2], hist[-1])
        else:
            detail = "initial state"
        text = f"last instruction: {self.executor.last_instruction or '<none>'}\n{detail}"
        return CommandResult("explain", text)

    def cmd_rewind(self) -> CommandResult:
        snap = self.executor.step_back()
        if snap is None:
            return CommandResult(
                "rewind", "at the start — nothing to rewind", "no earlier snapshot"
            )
        text = (
            f"rewound to step {snap.step_index}: "
            f"{self.executor.last_instruction or '<start>'}"
        )
        return CommandResult("rewind", text, explain_diff(snap, self.executor.snapshot()))

    def _stepping_result(self, command: str, before: List) -> CommandResult:
        hist = self.executor.history()
        detail = explain_diff(hist[-2], hist[-1]) if len(hist) >= 2 else ""
        lines = [f"instruction: {self.executor.last_instruction or '<none>'}", detail]
        return CommandResult(command, "\n".join(lines))

    def _parse_addr(self, value: str) -> int:
        try:
            return int(value, 16)
        except ValueError as exc:
            raise ValueError(f"invalid address: {value!r}") from exc
