from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Optional

from academy.storage import JsonStore

DAYS = 60 * 60 * 24
XP_PER_LEVEL = 100

_ACTIVITY_XP: dict = {
    "program_run": 5,
    "lesson_complete": 20,
    "correct_answer": 10,
    "challenge_complete": 30,
    "binary_analyzed": 25,
    "binary_patched": 25,
}


def level_for_xp(xp: int) -> int:
    return xp // XP_PER_LEVEL + 1


@dataclass
class Gamification:
    def __init__(self, store: JsonStore) -> None:
        self._store = store
        data = store.get("gamification", {})
        self.xp: int = int(data.get("xp", 0))
        self.streak: int = int(data.get("streak", 0))
        self.best_streak: int = int(data.get("best_streak", 0))
        self.last_day: int = int(data.get("last_day", 0))
        self.total_correct: int = int(data.get("total_correct", 0))
        self.total_attempts: int = int(data.get("total_attempts", 0))

    @property
    def level(self) -> int:
        return level_for_xp(self.xp)

    def xp_to_next(self) -> int:
        return XP_PER_LEVEL - (self.xp % XP_PER_LEVEL)

    def _today(self) -> int:
        return int(time.time()) // DAYS

    def _persist(self) -> None:
        self._store.set(
            "gamification",
            {
                "xp": self.xp,
                "streak": self.streak,
                "best_streak": self.best_streak,
                "last_day": self.last_day,
                "total_correct": self.total_correct,
                "total_attempts": self.total_attempts,
            },
        )
        self._store.save()

    def record(self, event: str, correct: Optional[bool] = None) -> None:
        today = self._today()
        if self.last_day != today:
            if self.last_day == today - 1:
                self.streak += 1
            else:
                self.streak = 1
            self.last_day = today
            if self.streak > self.best_streak:
                self.best_streak = self.streak
        self.total_attempts += 1
        if correct:
            self.total_correct += 1
        if event in _ACTIVITY_XP:
            self.xp += _ACTIVITY_XP[event]
        self._persist()

    def as_dict(self) -> dict:
        return {
            "xp": self.xp,
            "level": self.level,
            "streak": self.streak,
            "best_streak": self.best_streak,
            "xp_to_next": self.xp_to_next(),
            "total_correct": self.total_correct,
            "total_attempts": self.total_attempts,
            "accuracy": (
                round(100.0 * self.total_correct / self.total_attempts, 1)
                if self.total_attempts
                else 0.0
            ),
        }
