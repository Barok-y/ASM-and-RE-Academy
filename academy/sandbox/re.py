from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from capstone import CS_ARCH_X86, CS_MODE_64, Cs

from academy.debugger.static import (
    ControlFlowGraph,
    Function,
    build_cfg,
    find_functions,
    find_strings,
)


@dataclass
class ToyBinary:
    name: str
    code: bytes
    data: bytes
    entry: int
    description: str
    task: str
    expected_output: Optional[bytes] = None
    expected_exit: Optional[int] = None


@dataclass
class AnalysisResult:
    disassembly: str
    cfg: ControlFlowGraph
    functions: List[Function]
    strings: List[str]

    def summary(self) -> str:
        lines = [
            f"functions: {len(self.functions)}",
            f"basic blocks: {len(self.cfg.blocks)}",
            f"strings: {self.strings}",
        ]
        return "\n".join(lines)


class ReverseEngineeringLab:
    def analyze(self, binary: ToyBinary) -> AnalysisResult:
        cs = Cs(CS_ARCH_X86, CS_MODE_64)
        lines = []
        for insn in cs.disasm(binary.code, binary.entry):
            lines.append(f"{insn.address:016x}  {insn.mnemonic} {insn.op_str}".rstrip())
        cfg = build_cfg(binary.code, binary.entry)
        functions = find_functions(binary.code, binary.entry)
        strings = find_strings(binary.data)
        return AnalysisResult(
            disassembly="\n".join(lines),
            cfg=cfg,
            functions=functions,
            strings=strings,
        )
