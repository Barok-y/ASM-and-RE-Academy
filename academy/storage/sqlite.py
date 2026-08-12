from __future__ import annotations

import sqlite3
import time
from pathlib import Path
from typing import Any, Dict, List


class SqliteStore:
    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(str(self.path))
        self._conn.execute(
            """
            CREATE TABLE IF NOT EXISTS attempts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_id TEXT NOT NULL,
                topic TEXT NOT NULL,
                correct INTEGER NOT NULL,
                hints_used INTEGER DEFAULT 0,
                retries INTEGER DEFAULT 0,
                duration REAL DEFAULT 0.0,
                ts REAL DEFAULT 0.0
            )
            """
        )
        self._conn.commit()

    def log_attempt(
        self,
        item_id: str,
        topic: str,
        correct: bool,
        hints_used: int = 0,
        retries: int = 0,
        duration: float = 0.0,
        ts: float = 0.0,
    ) -> int:
        cur = self._conn.execute(
            """
            INSERT INTO attempts (item_id, topic, correct, hints_used, retries, duration, ts)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (item_id, topic, int(correct), hints_used, retries, duration, ts or time.time()),
        )
        self._conn.commit()
        return cur.lastrowid

    def recent_attempts(self, limit: int = 100) -> List[Dict[str, Any]]:
        rows = self._conn.execute(
            "SELECT item_id, topic, correct, hints_used, retries, duration, ts "
            "FROM attempts ORDER BY id DESC LIMIT ?",
            (limit,),
        ).fetchall()
        keys = ("item_id", "topic", "correct", "hints_used", "retries", "duration", "ts")
        return [dict(zip(keys, row)) for row in rows]

    def count(self) -> int:
        (count,) = self._conn.execute("SELECT COUNT(*) FROM attempts").fetchone()
        return count

    def clear(self) -> None:
        self._conn.execute("DELETE FROM attempts")
        self._conn.commit()

    def close(self) -> None:
        self._conn.close()
