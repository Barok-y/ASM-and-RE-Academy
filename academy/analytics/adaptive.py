from __future__ import annotations

from typing import List

_DIFFICULTIES = ("easy", "medium", "hard", "expert")


class DifficultyAdjuster:
    BAND_UP = 0.85
    BAND_DOWN = 0.4

    def __init__(self, difficulties: List[str] = list(_DIFFICULTIES)) -> None:
        self._difficulties = difficulties

    def next_difficulty(self, current: str, recent_accuracy: float) -> str:
        if current not in self._difficulties:
            return self._difficulties[0]
        index = self._difficulties.index(current)
        if recent_accuracy >= self.BAND_UP and index < len(self._difficulties) - 1:
            return self._difficulties[index + 1]
        if recent_accuracy <= self.BAND_DOWN and index > 0:
            return self._difficulties[index - 1]
        return current
