from __future__ import annotations

from typing import Any, Dict, List

from .store import JsonStore


class UserContent:
    def __init__(self, store: JsonStore) -> None:
        self._store = store
        self._challenges = list(store.get("custom_challenges", []) or [])
        self._lessons = list(store.get("custom_lessons", []) or [])

    def add_challenge(
        self,
        title: str,
        spec: str,
        reference: str,
        expected: Dict[str, Any],
        challenge_type: str = "registers",
        difficulty: str = "easy",
        solution: str = "",
        flag: str = "",
    ) -> Dict[str, Any]:
        challenge = {
            "id": f"user_{len(self._challenges) + 1}",
            "title": title,
            "spec": spec,
            "program": reference,
            "expected": expected,
            "challenge_type": challenge_type,
            "difficulty": difficulty,
            "solution": solution,
            "flag": flag,
            "user_added": True,
        }
        self._challenges.append(challenge)
        self._persist()
        return challenge

    def add_practice(
        self,
        title: str,
        spec: str,
        reference: str,
        expected: Dict[str, Any],
        solution: str = "",
    ) -> Dict[str, Any]:
        return self.add_challenge(
            title=title,
            spec=spec,
            reference=reference,
            expected=expected,
            challenge_type="registers",
            difficulty="easy",
            solution=solution,
        )

    def remove_challenge(self, challenge_id: str) -> None:
        self._challenges = [c for c in self._challenges if c["id"] != challenge_id]
        self._persist()

    def challenge_dicts(self) -> List[Dict[str, Any]]:
        return list(self._challenges)

    def add_lesson(
        self,
        module: str,
        order: int,
        title: str,
        steps: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        lesson = {
            "id": f"user{module.replace('user', '')}{order}",
            "module": module,
            "order": order,
            "title": title,
            "steps": steps,
        }
        self._lessons.append(lesson)
        # keep the module's lessons ordered when multiple are added
        self._lessons.sort(key=lambda item: (item["module"], item["order"]))
        self._persist()
        return lesson

    def remove_lesson(self, lesson_id: str) -> None:
        self._lessons = [lesson for lesson in self._lessons if lesson["id"] != lesson_id]
        self._persist()

    def lesson_dicts(self) -> List[Dict[str, Any]]:
        return list(self._lessons)

    def _persist(self) -> None:
        self._store.set("custom_challenges", self._challenges)
        self._store.set("custom_lessons", self._lessons)
        self._store.save()
