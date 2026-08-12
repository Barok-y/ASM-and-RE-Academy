from __future__ import annotations

from typing import Dict

_GAIN = 0.25
_LOSS = 0.5


class MasteryGraph:
    def __init__(self) -> None:
        self._topics: Dict[str, float] = {}

    def reset(self) -> None:
        self._topics.clear()

    def record(self, topic: str, correct: bool) -> float:
        current = self._topics.get(topic, 0.0)
        if correct:
            current += (100.0 - current) * _GAIN
        else:
            current *= _LOSS
        self._topics[topic] = round(current, 1)
        return self._topics[topic]

    def get(self, topic: str) -> float:
        return self._topics.get(topic, 0.0)

    def all(self) -> Dict[str, float]:
        return dict(self._topics)

    def weakest(self, limit: int = 5) -> Dict[str, float]:
        return dict(sorted(self._topics.items(), key=lambda kv: kv[1])[:limit])

    def strongest(self, limit: int = 5) -> Dict[str, float]:
        return dict(sorted(self._topics.items(), key=lambda kv: kv[1], reverse=True)[:limit])
