from __future__ import annotations

import importlib.util
import inspect
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

KIND_ARCHITECTURE = "architecture"
KIND_MODULE = "module"


@dataclass(frozen=True)
class PluginInfo:
    name: str
    description: str
    version: str = "0.1.0"
    kind: str = KIND_MODULE


@dataclass(frozen=True)
class Insn:
    address: int
    size: int
    mnemonic: str
    op_str: str

    def __str__(self) -> str:
        text = f"{self.mnemonic} {self.op_str}".rstrip()
        return f"{self.address:08x}: {text}"


class Plugin:
    info: PluginInfo = field(
        default_factory=lambda: PluginInfo("anonymous", "no description")
    )

    def activate(self) -> None:
        """Called when the plugin is selected. Override to wire resources."""


class PluginRegistry:
    def __init__(self) -> None:
        self._plugins: Dict[str, Plugin] = {}

    def register(self, plugin: Plugin) -> None:
        if plugin.info.name in self._plugins:
            raise ValueError(f"plugin already registered: {plugin.info.name}")
        self._plugins[plugin.info.name] = plugin

    def get(self, name: str) -> Optional[Plugin]:
        return self._plugins.get(name)

    def require(self, name: str) -> Plugin:
        plugin = self.get(name)
        if plugin is None:
            raise KeyError(f"unknown plugin: {name}")
        return plugin

    def all(self) -> List[Plugin]:
        return list(self._plugins.values())

    def by_kind(self, kind: str) -> List[Plugin]:
        return [p for p in self._plugins.values() if p.info.kind == kind]

    def names(self) -> List[str]:
        return sorted(self._plugins)

    def discover(self, directory: str | Path) -> int:
        added = 0
        for path in sorted(Path(directory).glob("*.py")):
            if path.name == "__init__.py":
                continue
            module_name = f"{Path(directory).name}_{path.stem}"
            spec = importlib.util.spec_from_file_location(module_name, path)
            if spec is None or spec.loader is None:
                continue
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            for _, member in inspect.getmembers(module, inspect.isclass):
                if member is Plugin:
                    continue
                if issubclass(member, Plugin) and member is not Plugin:
                    plugin = member()
                    self.register(plugin)
                    added += 1
        return added
