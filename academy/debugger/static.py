from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from capstone import CS_ARCH_X86, CS_MODE_64, Cs, CsInsn

_JUMP_MNEMONICS = {
    "jmp",
    "je",
    "jne",
    "jz",
    "jnz",
    "ja",
    "jae",
    "jb",
    "jbe",
    "jg",
    "jge",
    "jl",
    "jle",
    "js",
    "jns",
    "jc",
    "jnc",
    "jo",
    "jno",
    "jp",
    "jpe",
    "jnp",
    "loop",
    "loope",
    "loopne",
    "jcxz",
    "jecxz",
    "jrcxz",
}


def _parse_hex(token: str) -> Optional[int]:
    token = token.strip()
    if token.lower().startswith("0x"):
        return int(token, 16)
    return None


def _branch_target(insn: CsInsn) -> Optional[int]:
    for token in insn.op_str.replace(",", " ").split():
        value = _parse_hex(token)
        if value is not None:
            return value
    return None


def _disassemble(code: bytes, base: int) -> List[CsInsn]:
    return list(Cs(CS_ARCH_X86, CS_MODE_64).disasm(code, base))


@dataclass
class BasicBlock:
    start: int
    end: int
    instructions: List[Tuple[int, str]] = field(default_factory=list)
    successors: List[int] = field(default_factory=list)


class ControlFlowGraph:
    def __init__(self, blocks: List[BasicBlock]):
        self._blocks = blocks
        self._by_addr: Dict[int, BasicBlock] = {b.start: b for b in blocks}

    @property
    def blocks(self) -> List[BasicBlock]:
        return list(self._blocks)

    def block_at(self, addr: int) -> Optional[BasicBlock]:
        return self._by_addr.get(addr)

    def render(self) -> str:
        lines = []
        for block in self._blocks:
            succ = ", ".join(f"0x{s:x}" for s in block.successors)
            lines.append(
                f"block 0x{block.start:x}-0x{block.end:x} -> [{succ}]"
            )
            for addr, text in block.instructions:
                lines.append(f"    {addr:016x}  {text}")
        return "\n".join(lines)


def build_cfg(code: bytes, base: int = 0) -> ControlFlowGraph:
    insns = _disassemble(code, base)
    if not insns:
        return ControlFlowGraph([])
    by_addr = {insn.address: insn for insn in insns}
    entry = insns[0].address
    targets = set()
    terminators = set()
    for insn in insns:
        target = _branch_target(insn)
        if insn.mnemonic in _JUMP_MNEMONICS or insn.mnemonic == "call":
            if target is not None:
                targets.add(target)
        if insn.mnemonic in _JUMP_MNEMONICS or insn.mnemonic == "ret":
            terminators.add(insn.address)
    block_starts = {entry}
    block_starts.update(targets)
    for insn in insns:
        if insn.address in terminators:
            block_starts.add(insn.address + insn.size)
    starts = sorted(block_starts)
    blocks = []
    for index, start in enumerate(starts):
        end = starts[index + 1] if index + 1 < len(starts) else None
        members = [
            by_addr[addr]
            for addr in sorted(by_addr)
            if addr >= start and (end is None or addr < end)
        ]
        if not members:
            continue
        last = members[-1]
        successors: List[int] = []
        if last.mnemonic in _JUMP_MNEMONICS:
            target = _branch_target(last)
            if target is not None:
                successors.append(target)
            if last.mnemonic != "jmp" and (last.address + last.size) in by_addr:
                successors.append(last.address + last.size)
        elif last.mnemonic == "ret":
            pass
        elif (last.address + last.size) in by_addr:
            successors.append(last.address + last.size)
        blocks.append(
            BasicBlock(
                start=members[0].address,
                end=last.address + last.size,
                instructions=[
                    (m.address, f"{m.mnemonic} {m.op_str}".strip()) for m in members
                ],
                successors=successors,
            )
        )
    return ControlFlowGraph(blocks)


@dataclass
class Function:
    name: str
    start: int
    end: int
    instructions: List[Tuple[int, str]] = field(default_factory=list)


def find_functions(code: bytes, base: int = 0, entry: Optional[int] = None) -> List[Function]:
    insns = _disassemble(code, base)
    by_addr = {insn.address: insn for insn in insns}
    entry = entry if entry is not None else base
    starts = {entry}
    for insn in insns:
        if insn.mnemonic == "call":
            target = _branch_target(insn)
            if target is not None:
                starts.add(target)
    functions: List[Function] = []
    for start in sorted(starts):
        members = []
        addr = start
        end = None
        while addr in by_addr:
            insn = by_addr[addr]
            members.append((addr, f"{insn.mnemonic} {insn.op_str}".strip()))
            if insn.mnemonic == "ret":
                end = addr + insn.size
                break
            addr += insn.size
        if members:
            functions.append(
                Function(name=f"func_{start:x}", start=start, end=end or addr, instructions=members)
            )
    return functions


def find_strings(data: bytes, min_length: int = 3) -> List[str]:
    strings = []
    current = bytearray()
    for byte in data:
        if 32 <= byte < 127:
            current.append(byte)
        else:
            if len(current) >= min_length:
                strings.append(bytes(current).decode())
            current.clear()
    if len(current) >= min_length:
        strings.append(bytes(current).decode())
    return strings
