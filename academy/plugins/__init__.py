from .api import (
    KIND_ARCHITECTURE,
    KIND_MODULE,
    Insn,
    Plugin,
    PluginInfo,
    PluginRegistry,
)
from .architecture import (
    BUILTIN_ARCHITECTURES,
    ArchitecturePlugin,
    Arm32Plugin,
    Arm64Plugin,
    Mips32Plugin,
    Riscv64Plugin,
    X8664Plugin,
)
from .modules import (
    BUILTIN_MODULES,
    LinuxKernelInternalsPlugin,
    MalwareAnalysisPlugin,
    ModulePlugin,
    WindowsInternalsPlugin,
)
from .runner import ProgramRanTooLong, run_code, run_source

BUILTIN_PLUGINS = (*BUILTIN_ARCHITECTURES, *BUILTIN_MODULES)


def builtin_registry() -> PluginRegistry:
    registry = PluginRegistry()
    for plugin in BUILTIN_PLUGINS:
        registry.register(plugin)
    return registry


def executor_for(arch: str = "x86_64"):
    """Return the full emulator Executor for x86-64; other targets run through
    the generic plugin runner instead."""
    if arch != "x86_64":
        raise ValueError(
            f"the full Executor is x86-64 only; run {arch!r} via plugins.run_source"
        )
    from academy.emulator import Executor

    return Executor()


__all__ = [
    "ArchitecturePlugin",
    "Arm32Plugin",
    "Arm64Plugin",
    "BUILTIN_ARCHITECTURES",
    "BUILTIN_MODULES",
    "BUILTIN_PLUGINS",
    "Insn",
    "KIND_ARCHITECTURE",
    "KIND_MODULE",
    "LinuxKernelInternalsPlugin",
    "MalwareAnalysisPlugin",
    "Mips32Plugin",
    "ModulePlugin",
    "Plugin",
    "PluginInfo",
    "PluginRegistry",
    "ProgramRanTooLong",
    "Riscv64Plugin",
    "WindowsInternalsPlugin",
    "X8664Plugin",
    "builtin_registry",
    "executor_for",
    "run_code",
    "run_source",
]
