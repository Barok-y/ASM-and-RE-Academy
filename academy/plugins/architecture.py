from __future__ import annotations

from typing import Dict, List

from capstone import (
    CS_ARCH_ARM,
    CS_ARCH_ARM64,
    CS_ARCH_MIPS,
    CS_ARCH_RISCV,
    CS_ARCH_X86,
    CS_MODE_64,
    CS_MODE_ARM,
    CS_MODE_BIG_ENDIAN,
    CS_MODE_LITTLE_ENDIAN,
    CS_MODE_MIPS32,
    CS_MODE_RISCV64,
    Cs,
)
from keystone import (
    KS_ARCH_ARM,
    KS_ARCH_ARM64,
    KS_ARCH_MIPS,
    KS_ARCH_X86,
    KS_MODE_64,
    KS_MODE_ARM,
    KS_MODE_BIG_ENDIAN,
    KS_MODE_LITTLE_ENDIAN,
    KS_MODE_MIPS32,
    Ks,
    KsError,
)
from unicorn import (
    UC_ARCH_ARM,
    UC_ARCH_ARM64,
    UC_ARCH_MIPS,
    UC_ARCH_RISCV,
    UC_ARCH_X86,
    UC_MODE_64,
    UC_MODE_ARM,
    UC_MODE_BIG_ENDIAN,
    UC_MODE_LITTLE_ENDIAN,
    UC_MODE_MIPS32,
    UC_MODE_RISCV64,
    Uc,
    UcError,
)
from unicorn import (
    arm64_const as arm64,
)
from unicorn import (
    arm_const as arm,
)
from unicorn import (
    mips_const as mips,
)
from unicorn import (
    riscv_const as riscv,
)

from academy.emulator import registers as regs

from .api import KIND_ARCHITECTURE, Insn, Plugin, PluginInfo

DEFAULT_BASE = 0x100000
PAGE_SIZE = 0x10000


class ArchitecturePlugin(Plugin):
    info: PluginInfo = PluginInfo("arch", "architecture plugin", kind=KIND_ARCHITECTURE)
    bits: int = 64
    base_address: int = DEFAULT_BASE

    def assemble(self, source: str) -> bytes:
        raise NotImplementedError(f"{self.info.name} has no assembler")

    def disassemble(self, code: bytes, base: int = 0) -> List[Insn]:
        raise NotImplementedError

    def create_engine(self) -> Uc:
        raise NotImplementedError

    def load_program(self, engine: Uc, code: bytes, base: int | None = None) -> int:
        base = base or self.base_address
        engine.mem_write(base, code)
        return base

    def read_pc(self, engine: Uc) -> int:
        raise NotImplementedError

    def step(self, engine: Uc, address: int) -> Insn:
        code = engine.mem_read(address, 16)
        insns = self.disassemble(code, base=address)
        if not insns:
            raise UcError("could not decode instruction at pc")
        engine.emu_start(address, 0, count=1)
        return insns[0]

    def registers(self, engine: Uc) -> Dict[str, int]:
        raise NotImplementedError

    def _disassemble_all(
        self, cs: Cs, code: bytes, base: int
    ) -> List[Insn]:
        return [
            Insn(i.address, i.size, i.mnemonic, i.op_str)
            for i in cs.disasm(code, base)
        ]


class X8664Plugin(ArchitecturePlugin):
    info = PluginInfo(
        "x86_64",
        "x86-64 target (Intel syntax) backed by the full Executor",
        version="1.0.0",
        kind=KIND_ARCHITECTURE,
    )
    bits = 64
    base_address = 0x400000

    def __init__(self) -> None:
        self._ks = Ks(KS_ARCH_X86, KS_MODE_64)
        self._cs = Cs(CS_ARCH_X86, CS_MODE_64)
        self._cs.detail = True

    def assemble(self, source: str) -> bytes:
        try:
            encoding, _ = self._ks.asm(source)
        except KsError as exc:
            raise ValueError(f"assembly failed: {exc}") from exc
        if not encoding:
            raise ValueError("assembly produced no code")
        return bytes(encoding)

    def disassemble(self, code: bytes, base: int = 0) -> List[Insn]:
        return self._disassemble_all(self._cs, code, base)

    def create_engine(self) -> Uc:
        engine = Uc(UC_ARCH_X86, UC_MODE_64)
        engine.mem_map(self.base_address, PAGE_SIZE * 16)
        for name in regs.BASE_REGISTERS:
            regs.write_register(engine, name, 0)
        return engine

    def read_pc(self, engine: Uc) -> int:
        return regs.read_register(engine, "rip")

    def registers(self, engine: Uc) -> Dict[str, int]:
        return regs.read_all_registers(engine)


class Arm64Plugin(ArchitecturePlugin):
    info = PluginInfo(
        "arm64",
        "AArch64 target (little-endian)",
        version="1.0.0",
        kind=KIND_ARCHITECTURE,
    )
    bits = 64

    def __init__(self) -> None:
        self._ks = Ks(KS_ARCH_ARM64, KS_MODE_LITTLE_ENDIAN)
        self._cs = Cs(CS_ARCH_ARM64, CS_MODE_LITTLE_ENDIAN)

    def assemble(self, source: str) -> bytes:
        try:
            encoding, _ = self._ks.asm(source)
        except KsError as exc:
            raise ValueError(f"assembly failed: {exc}") from exc
        if not encoding:
            raise ValueError("assembly produced no code")
        return bytes(encoding)

    def disassemble(self, code: bytes, base: int = 0) -> List[Insn]:
        return self._disassemble_all(self._cs, code, base)

    def create_engine(self) -> Uc:
        engine = Uc(UC_ARCH_ARM64, UC_MODE_LITTLE_ENDIAN)
        engine.mem_map(self.base_address, PAGE_SIZE * 16)
        return engine

    def read_pc(self, engine: Uc) -> int:
        return engine.reg_read(arm64.UC_ARM64_REG_PC)

    def registers(self, engine: Uc) -> Dict[str, int]:
        out = {}
        for index in range(31):
            out[f"x{index}"] = engine.reg_read(getattr(arm64, f"UC_ARM64_REG_X{index}"))
        out["pc"] = self.read_pc(engine)
        return out


class Arm32Plugin(ArchitecturePlugin):
    info = PluginInfo(
        "arm32",
        "ARM (AArch32) target",
        version="1.0.0",
        kind=KIND_ARCHITECTURE,
    )
    bits = 32

    def __init__(self) -> None:
        self._ks = Ks(KS_ARCH_ARM, KS_MODE_ARM)
        self._cs = Cs(CS_ARCH_ARM, CS_MODE_ARM)

    def assemble(self, source: str) -> bytes:
        try:
            encoding, _ = self._ks.asm(source)
        except KsError as exc:
            raise ValueError(f"assembly failed: {exc}") from exc
        if not encoding:
            raise ValueError("assembly produced no code")
        return bytes(encoding)

    def disassemble(self, code: bytes, base: int = 0) -> List[Insn]:
        return self._disassemble_all(self._cs, code, base)

    def create_engine(self) -> Uc:
        engine = Uc(UC_ARCH_ARM, UC_MODE_ARM)
        engine.mem_map(self.base_address, PAGE_SIZE * 16)
        return engine

    def read_pc(self, engine: Uc) -> int:
        return engine.reg_read(arm.UC_ARM_REG_PC)

    def registers(self, engine: Uc) -> Dict[str, int]:
        out = {}
        for index in range(16):
            out[f"r{index}"] = engine.reg_read(getattr(arm, f"UC_ARM_REG_R{index}"))
        out["pc"] = self.read_pc(engine)
        return out


class Mips32Plugin(ArchitecturePlugin):
    info = PluginInfo(
        "mips32",
        "MIPS32 target (big-endian)",
        version="1.0.0",
        kind=KIND_ARCHITECTURE,
    )
    bits = 32

    def __init__(self) -> None:
        self._ks = Ks(KS_ARCH_MIPS, KS_MODE_MIPS32 + KS_MODE_BIG_ENDIAN)
        self._cs = Cs(CS_ARCH_MIPS, CS_MODE_MIPS32 + CS_MODE_BIG_ENDIAN)

    def assemble(self, source: str) -> bytes:
        try:
            encoding, _ = self._ks.asm(source)
        except KsError as exc:
            raise ValueError(f"assembly failed: {exc}") from exc
        if not encoding:
            raise ValueError("assembly produced no code")
        return bytes(encoding)

    def disassemble(self, code: bytes, base: int = 0) -> List[Insn]:
        return self._disassemble_all(self._cs, code, base)

    def create_engine(self) -> Uc:
        engine = Uc(UC_ARCH_MIPS, UC_MODE_MIPS32 + UC_MODE_BIG_ENDIAN)
        engine.mem_map(self.base_address, PAGE_SIZE * 16)
        return engine

    def read_pc(self, engine: Uc) -> int:
        return engine.reg_read(mips.UC_MIPS_REG_PC)

    def registers(self, engine: Uc) -> Dict[str, int]:
        out = {}
        for index in range(32):
            out[f"${index}"] = engine.reg_read(getattr(mips, f"UC_MIPS_REG_{index}"))
        out["pc"] = self.read_pc(engine)
        return out


class Riscv64Plugin(ArchitecturePlugin):
    info = PluginInfo(
        "riscv64",
        "RISC-V 64-bit target (disassembly + emulation; Keystone lacks RISC-V)",
        version="1.0.0",
        kind=KIND_ARCHITECTURE,
    )
    bits = 64

    def __init__(self) -> None:
        self._cs = Cs(CS_ARCH_RISCV, CS_MODE_RISCV64)

    def disassemble(self, code: bytes, base: int = 0) -> List[Insn]:
        return self._disassemble_all(self._cs, code, base)

    def create_engine(self) -> Uc:
        engine = Uc(UC_ARCH_RISCV, UC_MODE_RISCV64)
        engine.mem_map(self.base_address, PAGE_SIZE * 16)
        return engine

    def read_pc(self, engine: Uc) -> int:
        return engine.reg_read(riscv.UC_RISCV_REG_PC)

    def registers(self, engine: Uc) -> Dict[str, int]:
        out = {}
        for index in range(32):
            out[f"x{index}"] = engine.reg_read(getattr(riscv, f"UC_RISCV_REG_X{index}"))
        out["pc"] = self.read_pc(engine)
        return out


BUILTIN_ARCHITECTURES = (
    X8664Plugin(),
    Arm64Plugin(),
    Arm32Plugin(),
    Mips32Plugin(),
    Riscv64Plugin(),
)
