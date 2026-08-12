from __future__ import annotations

import shutil
import subprocess
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List

from capstone import CS_ARCH_X86, CS_MODE_64, Cs
from keystone import KS_ARCH_X86, KS_MODE_64, Ks, KsError

OPTIMIZATIONS = ("O0", "O1", "O2", "O3")
LANGUAGES = ("c", "cpp", "asm")

_GCC_FLAGS = ("-masm=intel", "-fno-asynchronous-unwind-tables")


@dataclass
class CompileResult:
    language: str
    compiler: str
    variants: Dict[str, str] = field(default_factory=dict)
    errors: Dict[str, str] = field(default_factory=dict)

    @property
    def available(self) -> bool:
        return bool(self.compiler)


class CompilerExplorer:
    def __init__(self) -> None:
        self._candidates = [
            shutil.which("gcc"),
            shutil.which("clang"),
        ]
        self.cc: str | None = next((c for c in self._candidates if c), None)

    @property
    def available(self) -> bool:
        return self.cc is not None

    @property
    def compiler(self) -> str:
        return self.cc or "<none>"

    def compile(self, source: str, language: str, optimizations=None) -> CompileResult:
        if language not in LANGUAGES:
            raise ValueError(f"unsupported language: {language}")
        variants = optimizations or OPTIMIZATIONS
        result = CompileResult(language=language, compiler=self.compiler)
        if language == "asm":
            try:
                listing = self._assemble(source)
            except ValueError as exc:
                result.errors["asm"] = str(exc)
            else:
                result.variants["asm"] = listing
            return result
        if self.cc is None:
            result.errors["all"] = "no C/C++ compiler found on host"
            return result
        with tempfile.TemporaryDirectory() as tmp:
            source_path = Path(tmp) / self._filename_for(language)
            source_path.write_text(source)
            for opt in variants:
                asm, err = self._invoke_compiler(source_path, language, opt)
                if err:
                    result.errors[opt] = err
                else:
                    result.variants[opt] = self._clean_asm(asm)
        return result

    def _invoke_compiler(self, source_path: Path, language: str, opt: str):
        if language == "cpp" and shutil.which("g++"):
            compiler = "g++"
        else:
            compiler = self.cc
        output = source_path.with_suffix(".s")
        cmd = [compiler, "-x", "c++" if language == "cpp" else "c", "-S", f"-{opt}"]
        cmd.extend(_GCC_FLAGS)
        cmd.extend(["-o", str(output), str(source_path)])
        proc = subprocess.run(cmd, capture_output=True, text=True)
        if proc.returncode != 0:
            return "", proc.stderr.strip()
        return output.read_text(), ""

    def _assemble(self, source: str) -> str:
        try:
            encoding, _ = Ks(KS_ARCH_X86, KS_MODE_64).asm(source)
        except KsError as exc:
            raise ValueError(f"assembly failed: {exc}") from exc
        if not encoding:
            raise ValueError("assembly produced no code")
        cs = Cs(CS_ARCH_X86, CS_MODE_64)
        lines: List[str] = []
        for insn in cs.disasm(bytes(encoding), 0x400000):
            lines.append(f"{insn.address:016x}  {insn.mnemonic} {insn.op_str}".rstrip())
        return "\n".join(lines)

    def _filename_for(self, language: str) -> str:
        return {"c": "prog.c", "cpp": "prog.cpp", "asm": "prog.asm"}[language]

    def _clean_asm(self, asm: str) -> str:
        lines = []
        for raw in asm.splitlines():
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            if line.startswith(".") and ":" not in line:
                if line.startswith(".file") or line.startswith(".ident"):
                    continue
                if line.startswith(".section"):
                    continue
                if line.startswith(".note"):
                    continue
            lines.append(line)
        return "\n".join(lines)
