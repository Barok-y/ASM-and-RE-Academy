from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import List, Optional

from .store import JsonStore

ENTRY_KINDS = ("note", "code", "session", "bookmark")


@dataclass
class NotebookEntry:
    kind: str
    title: str
    content: str = ""
    entry_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    created: float = field(default_factory=time.time)

    def to_dict(self) -> dict:
        return {
            "id": self.entry_id,
            "kind": self.kind,
            "title": self.title,
            "content": self.content,
            "created": self.created,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "NotebookEntry":
        return cls(
            kind=data["kind"],
            title=data["title"],
            content=data.get("content", ""),
            entry_id=data.get("id", uuid.uuid4().hex[:12]),
            created=data.get("created", 0.0),
        )


class Notebook:
    def __init__(self, store: JsonStore) -> None:
        self._store = store
        self._entries: List[NotebookEntry] = [
            NotebookEntry.from_dict(d) for d in store.get("notebook_entries", [])
        ]

    def add(self, kind: str, title: str, content: str = "") -> NotebookEntry:
        if kind not in ENTRY_KINDS:
            raise ValueError(f"unknown notebook kind: {kind}")
        entry = NotebookEntry(kind=kind, title=title, content=content)
        self._entries.append(entry)
        self._persist()
        return entry

    def get(self, entry_id: str) -> Optional[NotebookEntry]:
        for entry in self._entries:
            if entry.entry_id == entry_id:
                return entry
        return None

    def entries(self, kind: Optional[str] = None) -> List[NotebookEntry]:
        if kind is None:
            return list(self._entries)
        return [e for e in self._entries if e.kind == kind]

    def delete(self, entry_id: str) -> bool:
        before = len(self._entries)
        self._entries = [e for e in self._entries if e.entry_id != entry_id]
        if len(self._entries) != before:
            self._persist()
            return True
        return False

    def reset(self) -> None:
        self._entries = []
        self._store.remove("notebook_entries")
        self._store.save()

    def _persist(self) -> None:
        self._store.set("notebook_entries", [e.to_dict() for e in self._entries])
        self._store.save()
