from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List


@dataclass
class ReviewItem:
    item_id: str
    repetitions: int = 0
    interval_days: int = 0
    due_day: int = 0
    last_result: bool = False


class SpacedRepetition:
    INTERVALS = (1, 3, 7, 14, 30)

    def __init__(self) -> None:
        self._items: Dict[str, ReviewItem] = {}

    def add(self, item_id: str) -> None:
        self._items[item_id] = ReviewItem(item_id=item_id)

    def review(self, item_id: str, correct: bool, day: int) -> ReviewItem:
        item = self._items.setdefault(item_id, ReviewItem(item_id=item_id))
        item.last_result = correct
        if not correct:
            item.repetitions = 0
            item.interval_days = self.INTERVALS[0]
        else:
            item.repetitions += 1
            index = min(item.repetitions - 1, len(self.INTERVALS) - 1)
            item.interval_days = self.INTERVALS[index]
        item.due_day = day + item.interval_days
        return item

    def due_on(self, day: int) -> List[str]:
        return sorted(
            item_id for item_id, item in self._items.items() if item.due_day <= day
        )

    def items(self) -> Dict[str, ReviewItem]:
        return dict(self._items)
