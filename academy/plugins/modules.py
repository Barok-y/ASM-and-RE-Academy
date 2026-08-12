from __future__ import annotations

from .api import KIND_MODULE, Plugin, PluginInfo


class ModulePlugin(Plugin):
    info: PluginInfo = PluginInfo(
        "module", "content module plugin", kind=KIND_MODULE
    )


class MalwareAnalysisPlugin(ModulePlugin):
    info = PluginInfo(
        "malware_analysis",
        "Malware analysis: unpacking, deobfuscation, and behavior labs",
        version="1.0.0",
        kind=KIND_MODULE,
    )


class WindowsInternalsPlugin(ModulePlugin):
    info = PluginInfo(
        "windows_internals",
        "Windows internals: PE files, syscalls, and the Win64 ABI",
        version="1.0.0",
        kind=KIND_MODULE,
    )


class LinuxKernelInternalsPlugin(ModulePlugin):
    info = PluginInfo(
        "linux_kernel_internals",
        "Linux kernel internals: syscall tables and the x86-64 SysV ABI",
        version="1.0.0",
        kind=KIND_MODULE,
    )


BUILTIN_MODULES = (
    MalwareAnalysisPlugin(),
    WindowsInternalsPlugin(),
    LinuxKernelInternalsPlugin(),
)
