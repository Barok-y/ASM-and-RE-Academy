from __future__ import annotations

from academy.emulator import ExecutionHalted, Executor
from academy.sandbox.explain import explain_diff, format_flags, format_registers, hexdump


class Debugger:
    def __init__(self, executor: Executor | None = None):
        self.executor = executor or Executor()

    def load_asm(self, source: str, entry: int | None = None) -> None:
        self.executor.load_asm(source, entry)

    def load_bytes(self, code: bytes, entry: int | None = None) -> None:
        self.executor.load_bytes(code, entry)

    def step_into(self) -> str:
        try:
            self.executor.step()
        except ExecutionHalted as exc:
            return f"cannot step: {exc}"
        return self._last_change()

    def step_over(self) -> str:
        try:
            self.executor.step_over()
        except ExecutionHalted as exc:
            return f"cannot step: {exc}"
        return self._last_change()

    def step_out(self) -> str:
        try:
            self.executor.step_out()
        except ExecutionHalted as exc:
            return f"cannot step: {exc}"
        return self._last_change()

    def continue_execution(self) -> str:
        self.executor.run()
        return f"status: {self.executor.status}"

    def view_registers(self) -> str:
        return format_registers(self.executor.registers())

    def view_flags(self) -> str:
        return format_flags(self.executor.flags())

    def view_memory(self, addr: int, size: int) -> str:
        return hexdump(self.executor.read_memory(addr, size), base=addr)

    def view_stack(self, count: int = 16) -> str:
        rows = self.executor.stack_view(count)
        lines = []
        for addr, data in rows:
            lines.append(f"{addr:016x}  {data.hex()}")
        return "\n".join(lines) or "(stack empty)"

    def _last_change(self) -> str:
        hist = self.executor.history()
        if len(hist) < 2:
            return ""
        return explain_diff(hist[-2], hist[-1])
