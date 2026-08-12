from __future__ import annotations

import pathlib
import tempfile

from academy.analytics import Gamification, level_for_xp
from academy.curriculum.reference import cheat_sheet_text, lookup
from academy.grading import (
    Grader,
    HintEngine,
    daily_challenge,
    random_challenge,
    sample_challenges,
)
from academy.sandbox import Sandbox
from academy.storage import JsonStore, SessionStore
from academy.ui.screens import _fuzzy_score, _normalize
from academy.ui.state import AppState


def _store(tmp: str) -> JsonStore:
    return JsonStore(pathlib.Path(tmp) / "state.json")


def test_level_for_xp():
    assert level_for_xp(0) == 1
    assert level_for_xp(99) == 1
    assert level_for_xp(100) == 2
    assert level_for_xp(250) == 3


def test_gamification_xp_and_level():
    with tempfile.TemporaryDirectory() as tmp:
        g = Gamification(_store(tmp))
        g.record("correct_answer", correct=True)
        g.record("correct_answer", correct=True)
        g.record("program_run")
        info = g.as_dict()
        assert info["xp"] == 25
        assert info["level"] == 1
        assert info["total_correct"] == 2
        assert info["accuracy"] == round(100.0 * 2 / 3, 1)


def test_gamification_streak_persists():
    with tempfile.TemporaryDirectory() as tmp:
        store = _store(tmp)
        g = Gamification(store)
        g.record("correct_answer", correct=True)
        g2 = Gamification(store)  # reload from disk
        assert g2.streak == 1
        assert g2.xp == 10


def test_daily_challenge_deterministic():
    a = daily_challenge("2026-08-07")
    b = daily_challenge("2026-08-07")
    assert a.id == b.id
    pool = sample_challenges()
    assert a.id in {c.id for c in pool}  # picked from the pool


def test_random_challenge_in_pool():
    pool = sample_challenges()
    pick = random_challenge(pool)
    assert pick.id in {c.id for c in pool}


def test_adaptive_hint_penalty_grows_with_failures():
    engine = HintEngine()
    assert engine.penalty(1, 0) == 10
    assert engine.penalty(1, 3) == 19
    assert engine.penalty(2, 5) == 35


def test_grade_carries_related_lesson():
    challenge = next(c for c in sample_challenges() if c.challenge_type == "registers")
    grade = Grader().grade(challenge, "mov rax, 5")
    assert grade.related_lessons
    assert any("register" in lesson for lesson in grade.related_lessons)


def test_cheat_sheet_lookup():
    assert "copy" in lookup("mov")
    assert "Zero Flag" in lookup("zf")
    assert "accumulator" in lookup("rax")
    assert "exit" in lookup("60")
    assert "syscall" in lookup("syscall")
    text = cheat_sheet_text()
    assert "INSTRUCTIONS" in text and "FLAGS" in text and "SYSCALLS" in text


def test_sandbox_rewind():
    sandbox = Sandbox()
    sandbox.executor.load_asm("mov rax, 10\nadd rax, 5")
    sandbox.execute("step")
    sandbox.execute("step")
    assert sandbox.executor.get_register("rax") == 15
    result = sandbox.execute("rewind")
    assert sandbox.executor.get_register("rax") == 10
    assert "rewound" in result.text
    result = sandbox.execute("rewind")
    assert sandbox.executor.get_register("rax") == 0
    assert result.text.startswith("rewound")
    result = sandbox.execute("rewind")
    assert "nothing to rewind" in result.text


def test_lesson_position_save_and_resume():
    with tempfile.TemporaryDirectory() as tmp:
        state = AppState(pathlib.Path(tmp) / "data")
        assert state.lesson_position("module1.lesson1") is None
        state.save_lesson_position("module1.lesson1", 4)
        assert state.lesson_position("module1.lesson1") == 4
        state.clear_lesson_position("module1.lesson1")
        assert state.lesson_position("module1.lesson1") is None


def test_profile_export_and_import():
    with tempfile.TemporaryDirectory() as tmp:
        root = pathlib.Path(tmp)
        state = AppState(root / "data")
        state.session.save_progress({"lessons": {"a": "complete"}})
        path = state.session.export_to(root / "profile.json")
        assert path.exists()

        state2 = AppState(root / "data2")
        state2.session.import_from(path)
        assert state2.session.load_progress()["lessons"] == {"a": "complete"}


def test_session_import_rejects_bad_files():
    with tempfile.TemporaryDirectory() as tmp:
        root = pathlib.Path(tmp)
        bad = root / "bad.json"
        bad.write_text("[1,2,3]")
        store = JsonStore(root / "state.json")
        session = SessionStore(store)
        try:
            session.import_from(bad)
            raise AssertionError("expected ValueError")
        except ValueError:
            pass


def test_fuzzy_score_and_normalize():
    assert _fuzzy_score("mov", "MOV: moving data") > 0
    assert _fuzzy_score("", "anything") > 0
    assert _fuzzy_score("zz", "Registers and the RAX family") == 0
    assert _normalize("Control-Flow Graphs") == "controlflowgraphs"
