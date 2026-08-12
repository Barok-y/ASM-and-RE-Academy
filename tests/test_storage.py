import json

from academy.storage import (
    AchievementSystem,
    JsonStore,
    Notebook,
    SessionStore,
    SqliteStore,
)


def test_json_store_roundtrip(tmp_path):
    path = tmp_path / "state.json"
    store = JsonStore(path)
    store.set("a", 1)
    store.set("b", {"x": [1, 2]})
    store.save()

    reloaded = JsonStore(path)
    assert reloaded.get("a") == 1
    assert reloaded.get("b") == {"x": [1, 2]}
    assert reloaded.get("missing", "d") == "d"
    assert json.loads(path.read_text())["a"] == 1


def test_session_store_snapshot_and_resume(tmp_path):
    session = SessionStore(JsonStore(tmp_path / "session.json"))
    session.save_progress({"module1": {"lesson3": "done"}})
    session.save_sandbox_state({"source": "mov rax, 1", "ip": 4194304})

    resumed = SessionStore(JsonStore(tmp_path / "session.json"))
    assert resumed.load_progress() == {"module1": {"lesson3": "done"}}
    assert resumed.load_sandbox_state() == {"source": "mov rax, 1", "ip": 4194304}

    snap = resumed.snapshot()
    assert set(snap) == {"progress", "sandbox"}

    fresh = SessionStore(JsonStore(tmp_path / "fresh.json"))
    fresh.restore(snap)
    assert fresh.load_progress() == {"module1": {"lesson3": "done"}}


def test_session_reset(tmp_path):
    session = SessionStore(JsonStore(tmp_path / "session.json"))
    session.save_progress({"module1": {"lesson1": "done"}})
    session.reset()
    assert SessionStore(JsonStore(tmp_path / "session.json")).load_progress() == {}


def test_notebook_kinds_and_crud(tmp_path):
    notebook = Notebook(JsonStore(tmp_path / "notebook.json"))
    note = notebook.add("note", "Memory model", "segments: text/data/bss/heap/stack")
    notebook.add("code", "mov example", "mov rax, 5")
    notebook.add("bookmark", "Lesson 3")
    assert [e.kind for e in notebook.entries()] == ["note", "code", "bookmark"]
    assert notebook.get(note.entry_id).title == "Memory model"
    assert len(notebook.entries("code")) == 1
    assert notebook.delete(note.entry_id)
    assert not notebook.delete(note.entry_id)
    assert len(notebook.entries()) == 2


def test_notebook_unknown_kind_rejected(tmp_path):
    notebook = Notebook(JsonStore(tmp_path / "notebook.json"))
    try:
        notebook.add("mystery", "x")
        raise AssertionError("expected ValueError")
    except ValueError:
        pass


def test_achievement_unlock_on_events(tmp_path):
    store = JsonStore(tmp_path / "ach.json")
    system = AchievementSystem(store)
    assert not system.is_unlocked("first_program")
    assert len(system.check_event("program_run")) == 1
    assert system.is_unlocked("first_program")
    assert system.check_event("program_run") == []
    assert system.unlocked()[0].name == "First Program"


def test_achievement_persists(tmp_path):
    path = tmp_path / "ach.json"
    system = AchievementSystem(JsonStore(path))
    system.check_event("binary_analyzed")
    reloaded = AchievementSystem(JsonStore(path))
    assert reloaded.is_unlocked("reverse_engineer")


def test_achievement_conditions_module_and_count(tmp_path):
    system = AchievementSystem(JsonStore(tmp_path / "ach.json"))
    system.check_event("module_complete", {"module": "module2"})
    assert system.is_unlocked("stack_master")
    assert not system.is_unlocked("abi_expert")
    for _ in range(5):
        system.check_event("correct_answers", {"count": 1})
    assert system.is_unlocked("hot_streak")


def test_sqlite_store_attempts(tmp_path):
    store = SqliteStore(tmp_path / "attempts.db")
    store.log_attempt("lesson-3-q2", "registers", True, hints_used=1)
    store.log_attempt("challenge-1", "arith", False, retries=2, duration=30.0)
    assert store.count() == 2
    rows = store.recent_attempts()
    assert rows[0]["topic"] == "arith"
    assert rows[0]["correct"] == 0
    assert rows[1]["correct"] == 1
    store.close()
