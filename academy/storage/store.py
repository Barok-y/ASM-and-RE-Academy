from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from typing import Any, Dict


class JsonStore:
    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self._data: Dict[str, Any] = {}
        if self.path.exists():
            self._data = json.loads(self.path.read_text())

    def get(self, key: str, default: Any = None) -> Any:
        return self._data.get(key, default)

    def set(self, key: str, value: Any) -> None:
        self._data[key] = value

    def update(self, mapping: Dict[str, Any]) -> None:
        self._data.update(mapping)

    def remove(self, key: str) -> None:
        self._data.pop(key, None)

    def as_dict(self) -> Dict[str, Any]:
        return dict(self._data)

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp = tempfile.mkstemp(dir=self.path.parent, suffix=".tmp")
        try:
            with os.fdopen(fd, "w") as fh:
                json.dump(self._data, fh, indent=2)
            os.replace(tmp, self.path)
        finally:
            if os.path.exists(tmp):
                os.unlink(tmp)
