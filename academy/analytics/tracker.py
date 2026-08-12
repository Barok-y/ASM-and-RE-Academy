from __future__ import annotations

import time
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Attempt:
    item_id: str
    topic: str
    correct: bool
    hints_used: int = 0
    retries: int = 0
    duration: float = 0.0
    timestamp: float = 0.0


class StudentTracker:
    def __init__(self) -> None:
        self._attempts: List[Attempt] = []

    def reset(self) -> None:
        self._attempts.clear()

    def record_attempt(self, attempt: Attempt) -> None:
        self._attempts.append(attempt)

    @property
    def attempts(self) -> List[Attempt]:
        return list(self._attempts)

    def accuracy(self, topic: Optional[str] = None) -> float:
        items = self._attempts_for(topic)
        if not items:
            return 0.0
        return sum(1 for a in items if a.correct) / len(items)

    def average_hints(self, topic: Optional[str] = None) -> float:
        items = self._attempts_for(topic)
        if not items:
            return 0.0
        return sum(a.hints_used for a in items) / len(items)

    def total_retries(self, topic: Optional[str] = None) -> int:
        return sum(a.retries for a in self._attempts_for(topic))

    def completion_time(self, topic: Optional[str] = None) -> float:
        return sum(a.duration for a in self._attempts_for(topic))

    def topics(self) -> List[str]:
        seen = []
        for a in self._attempts:
            if a.topic not in seen:
                seen.append(a.topic)
        return seen

    def _attempts_for(self, topic: Optional[str]) -> List[Attempt]:
        if topic is None:
            return list(self._attempts)
        return [a for a in self._attempts if a.topic == topic]

    @staticmethod
    def now() -> float:
        return time.time()
