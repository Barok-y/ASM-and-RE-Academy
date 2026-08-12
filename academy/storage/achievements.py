from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from .store import JsonStore


@dataclass(frozen=True)
class Achievement:
    achievement_id: str
    name: str
    description: str
    event: str
    module: Optional[str] = None
    count: int = 1


ACHIEVEMENTS: List[Achievement] = [
    Achievement(
        achievement_id="first_program",
        name="First Program",
        description="Run your first assembly program",
        event="program_run",
    ),
    Achievement(
        achievement_id="stack_master",
        name="Stack Master",
        description="Finish the Memory and Stack module",
        event="module_complete",
        module="module2",
    ),
    Achievement(
        achievement_id="abi_expert",
        name="ABI Expert",
        description="Finish the Functions and ABI module",
        event="module_complete",
        module="module4",
    ),
    Achievement(
        achievement_id="reverse_engineer",
        name="Reverse Engineer",
        description="Analyze a toy binary",
        event="binary_analyzed",
    ),
    Achievement(
        achievement_id="binary_surgeon",
        name="Binary Surgeon",
        description="Patch a toy binary",
        event="binary_patched",
    ),
    Achievement(
        achievement_id="hot_streak",
        name="Hot Streak",
        description="Answer 5 questions correctly",
        event="correct_answers",
        count=5,
    ),
    Achievement(
        achievement_id="first_solve",
        name="First Blood",
        description="Solve your first practice or challenge exercise",
        event="challenge_complete",
    ),
    Achievement(
        achievement_id="challenge_hunter",
        name="Challenge Hunter",
        description="Solve 10 practice or challenge exercises",
        event="challenge_complete",
        count=10,
    ),
]


class AchievementSystem:
    def __init__(self, store: JsonStore) -> None:
        self._store = store
        self._unlocked = set(store.get("achievements", []))
        self._counters = dict(store.get("achievement_counters", {}))
        self._by_id = {a.achievement_id: a for a in ACHIEVEMENTS}

    def unlocked(self) -> List[Achievement]:
        return [self._by_id[i] for i in sorted(self._unlocked) if i in self._by_id]

    def reset(self) -> None:
        self._unlocked.clear()
        self._counters.clear()
        self._store.remove("achievements")
        self._store.remove("achievement_counters")
        self._store.save()

    def is_unlocked(self, achievement_id: str) -> bool:
        return achievement_id in self._unlocked

    def check_event(self, event: str, data: Optional[Dict[str, Any]] = None) -> List[Achievement]:
        data = data or {}
        if "count" in data:
            self._counters[event] = self._counters.get(event, 0) + data["count"]
            self._persist()
        cumulative = self._counters.get(event, 0)
        newly = []
        for achievement in ACHIEVEMENTS:
            if achievement.achievement_id in self._unlocked:
                continue
            if achievement.event != event:
                continue
            if achievement.module and data.get("module") != achievement.module:
                continue
            if achievement.count > 1 and cumulative < achievement.count:
                continue
            self._unlocked.add(achievement.achievement_id)
            newly.append(achievement)
        if newly:
            self._persist()
        return newly

    def _persist(self) -> None:
        self._store.set("achievements", sorted(self._unlocked))
        self._store.set("achievement_counters", dict(self._counters))
        self._store.save()
