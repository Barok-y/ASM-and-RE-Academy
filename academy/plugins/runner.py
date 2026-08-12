from __future__ import annotations

from typing import Dict, List, Tuple

from unicorn import UcError

from .architecture import ArchitecturePlugin


class ProgramRanTooLong(RuntimeError):
    pass


def run_code(
    plugin: ArchitecturePlugin,
    code: bytes,
    base: int | None = None,
    max_steps: int = 1000,
) -> Tuple[List[str], Dict[str, int]]:
    engine = plugin.create_engine()
    entry = plugin.load_program(engine, code, base)
    trace: List[str] = []
    address = entry
    for _ in range(max_steps):
        try:
            insn = plugin.step(engine, address)
        except UcError:
            break
        trace.append(str(insn))
        address = plugin.read_pc(engine)
    if len(trace) == max_steps:
        raise ProgramRanTooLong(f"program did not terminate after {max_steps} steps")
    return trace, plugin.registers(engine)


def run_source(
    plugin: ArchitecturePlugin,
    source: str,
    base: int | None = None,
    max_steps: int = 1000,
) -> Tuple[List[str], Dict[str, int]]:
    return run_code(plugin, plugin.assemble(source), base, max_steps)
