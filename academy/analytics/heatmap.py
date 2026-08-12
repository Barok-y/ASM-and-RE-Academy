from __future__ import annotations

from collections import Counter
from typing import Dict, List

from .tracker import StudentTracker

_WEAK_ACCURACY = 0.6
_SLOW_SECONDS = 20.0
_TOPIC_LABELS = {
    "registers": "register moves",
    "arith": "arithmetic",
    "lea": "LEA/addresses",
    "flags": "flags and conditionals",
    "stack": "stack",
    "functions": "functions and ABI",
}


def _label(topic: str) -> str:
    return _TOPIC_LABELS.get(topic, topic.replace("_", " "))


class HeatmapAnalyzer:
    def __init__(self, tracker: StudentTracker) -> None:
        self._tracker = tracker

    def common_mistakes(self) -> Dict[str, int]:
        mistakes: Counter[str] = Counter()
        for attempt in self._tracker.attempts:
            if not attempt.correct:
                mistakes[attempt.topic] += 1
        return dict(mistakes.most_common())

    def weak_topics(self, threshold: float = _WEAK_ACCURACY) -> List[str]:
        weak = []
        for topic in self._tracker.topics():
            if self._tracker.accuracy(topic) < threshold:
                weak.append(topic)
        return sorted(weak)

    def slow_topics(self, threshold: float = _SLOW_SECONDS) -> List[str]:
        slow = []
        for topic in self._tracker.topics():
            attempts = [a for a in self._tracker.attempts if a.topic == topic]
            if attempts and sum(a.duration for a in attempts) / len(attempts) > threshold:
                slow.append(topic)
        return sorted(slow)

    def recommendations(self) -> List[str]:
        suggestions: List[str] = []
        weak = self.weak_topics()
        if weak:
            labels = ", ".join(_label(t) for t in weak)
            suggestions.append(f"Review {labels} — accuracy is below 60%.")
        slow = self.slow_topics()
        if slow:
            labels = ", ".join(_label(t) for t in slow)
            suggestions.append(f"Practice {labels} — these take longer than average.")
        mistakes = self.common_mistakes()
        if mistakes:
            topic = max(mistakes, key=mistakes.get)
            suggestions.append(
                f"Most common mistakes happen on {_label(topic)} ({mistakes[topic]} missed)."
            )
        if not suggestions:
            suggestions.append("No weak areas detected — consider harder challenges.")
        return suggestions

    def heatmap(self) -> Dict[str, Dict[str, float]]:
        return {
            "accuracy": {t: self._tracker.accuracy(t) for t in self._tracker.topics()},
            "average_hints": {t: self._tracker.average_hints(t) for t in self._tracker.topics()},
            "completion_time": {
                t: self._tracker.completion_time(t) for t in self._tracker.topics()
            },
        }
