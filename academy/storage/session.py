from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from .store import JsonStore

SECTIONS = ("progress", "sandbox", "challenges", "achievements", "notebook")


class SessionStore:
    def __init__(self, store: JsonStore) -> None:
        self._store = store

    def save_progress(self, progress: Dict[str, Any]) -> None:
        self._store.set("progress", progress)
        self._store.save()

    def load_progress(self) -> Dict[str, Any]:
        return dict(self._store.get("progress", {}))

    def save_sandbox_state(self, state: Dict[str, Any]) -> None:
        self._store.set("sandbox", state)
        self._store.save()

    def load_sandbox_state(self) -> Dict[str, Any]:
        return dict(self._store.get("sandbox", {}))

    def save_challenges(self, results: List[Dict[str, Any]]) -> None:
        self._store.set("challenges", results)
        self._store.save()

    def load_challenges(self) -> List[Dict[str, Any]]:
        return list(self._store.get("challenges", []))

    def save_notebook(self, entries: List[Dict[str, Any]]) -> None:
        self._store.set("notebook", entries)
        self._store.save()

    def load_notebook(self) -> List[Dict[str, Any]]:
        return list(self._store.get("notebook", []))

    def save_achievements(self, unlocked: List[str]) -> None:
        self._store.set("achievements", unlocked)
        self._store.save()

    def load_achievements(self) -> List[str]:
        return list(self._store.get("achievements", []))

    def snapshot(self) -> Dict[str, Any]:
        return {
            section: self._store.get(section)
            for section in SECTIONS
            if self._store.get(section) is not None
        }

    def export_to(self, path: str | Path) -> Path:
        """Write the full profile snapshot to a JSON file."""
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(self.snapshot(), indent=2))
        return target

    def import_from(self, path: str | Path) -> Dict[str, Any]:
        """Load a profile snapshot from a JSON file and restore it."""
        target = Path(path)
        data = json.loads(target.read_text())
        if not isinstance(data, dict):
            raise ValueError("profile file must contain a JSON object")
        self.restore(data)
        return data

    def restore(self, data: Dict[str, Any]) -> None:
        self._store.update(data)
        self._store.save()

    def reset(self) -> None:
        for section in SECTIONS:
            self._store.remove(section)
        self._store.save()
