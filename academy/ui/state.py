"""Shared per-run state for the TUI: wires storage, notebook, achievements,
and analytics so every screen reads and writes the same data."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Optional

from academy.analytics import (
    Gamification,
    HeatmapAnalyzer,
    MasteryGraph,
    SpacedRepetition,
    StudentTracker,
)
from academy.analytics.tracker import Attempt
from academy.storage import (
    AchievementSystem,
    JsonStore,
    Notebook,
    SessionStore,
    SqliteStore,
    UserContent,
)

DEFAULT_DATA_DIR = Path.home() / ".asm-academy"


class AppState:
    def __init__(self, data_dir: str | Path | None = None) -> None:
        self.data_dir = Path(data_dir) if data_dir else DEFAULT_DATA_DIR
        self.store = JsonStore(self.data_dir / "state.json")
        self.session = SessionStore(self.store)
        self.notebook = Notebook(self.store)
        self.achievements = AchievementSystem(self.store)
        self.user_content = UserContent(self.store)
        self.tracker = StudentTracker()
        self.mastery = MasteryGraph()
        self.srs = SpacedRepetition()
        self.sqlite = SqliteStore(self.data_dir / "attempts.db")
        self.gamification = Gamification(self.store)

    def record_attempt(
        self,
        item_id: str,
        topic: str,
        correct: bool,
        hints_used: int = 0,
        retries: int = 0,
        duration: float = 0.0,
    ) -> None:
        self.tracker.record_attempt(
            Attempt(
                item_id=item_id,
                topic=topic,
                correct=correct,
                hints_used=hints_used,
                retries=retries,
                duration=duration,
            )
        )
        self.mastery.record(topic, correct)
        self.srs.review(item_id, correct, day=0)
        self.sqlite.log_attempt(item_id, topic, correct, hints_used, retries, duration)
        if correct:
            self.achievements.check_event("correct_answers", {"count": 1})
            self.gamification.record("correct_answer", correct=True)
        else:
            self.gamification.record("", correct=False)

    def mark_lesson_complete(self, lesson_id: str, module_id: str) -> None:
        from academy.curriculum import all_modules

        progress = self.session.load_progress()
        progress.setdefault("lessons", {})[lesson_id] = "complete"
        self.session.save_progress(progress)
        self.achievements.check_event("lesson_complete", {"lesson": lesson_id})
        completed = set(progress.get("lessons", {}))
        module = next((m for m in all_modules() if m.id == module_id), None)
        if module is not None and all(
            lesson.id in completed for lesson in module.lessons
        ):
            self.achievements.check_event("module_complete", {"module": module_id})
        self.gamification.record("lesson_complete", correct=True)

    def save_lesson_position(self, lesson_id: str, step_index: int) -> None:
        progress = self.session.load_progress()
        progress.setdefault("lesson_positions", {})[lesson_id] = step_index
        self.session.save_progress(progress)

    def lesson_position(self, lesson_id: str) -> Optional[int]:
        try:
            progress = self.session.load_progress()
            return progress.get("lesson_positions", {}).get(lesson_id)
        except Exception:
            return None

    def clear_lesson_position(self, lesson_id: str) -> None:
        progress = self.session.load_progress()
        positions = progress.get("lesson_positions", {})
        if lesson_id in positions:
            del positions[lesson_id]
            self.session.save_progress(progress)

    def heatmap(self) -> HeatmapAnalyzer:
        return HeatmapAnalyzer(self.tracker)

    def clear_state(self) -> None:
        """Erase saved learning state (progress, notebook, achievements,
        gamification). User-authored content is kept."""
        for key in (
            "progress",
            "sandbox",
            "challenges",
            "gamification",
        ):
            self.store.remove(key)
        self.store.save()
        self.notebook.reset()
        self.achievements.reset()
        self.tracker.reset()
        self.mastery.reset()
        try:
            self.sqlite.clear()
        except Exception:
            pass

    def achievements_unlocked(self) -> List[str]:
        return [a.name for a in self.achievements.unlocked()]

    def progress_summary(self) -> Dict[str, object]:
        progress = self.session.load_progress()
        lessons = progress.get("lessons", {})
        return {
            "lessons_complete": sorted(lessons),
            "mastery": dict(self.mastery.all()),
            "weakest": dict(self.mastery.weakest(3)),
            "achievements": self.achievements_unlocked(),
            "recommendations": self.heatmap().recommendations(),
            "gamification": self.gamification.as_dict(),
        }
