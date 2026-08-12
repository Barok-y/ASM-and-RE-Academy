"""Interactive sandbox: emulator command surface, explain engine, compiler
explorer, reverse engineering lab, and patching lab."""

from .compiler import LANGUAGES, OPTIMIZATIONS, CompileResult, CompilerExplorer
from .explain import (
    explain_diff,
    explain_steps,
    fmt_hex,
    format_flags,
    format_registers,
    hexdump,
)
from .patching import PatchingLab
from .re import AnalysisResult, ReverseEngineeringLab, ToyBinary
from .sandbox import CommandResult, Sandbox
from .toy import toy_binaries

__all__ = [
    "AnalysisResult",
    "CommandResult",
    "CompileResult",
    "CompilerExplorer",
    "LANGUAGES",
    "OPTIMIZATIONS",
    "PatchingLab",
    "ReverseEngineeringLab",
    "Sandbox",
    "ToyBinary",
    "explain_diff",
    "explain_steps",
    "fmt_hex",
    "format_flags",
    "format_registers",
    "hexdump",
    "toy_binaries",
]
