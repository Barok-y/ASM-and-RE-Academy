from academy.analytics import (
    Attempt,
    DifficultyAdjuster,
    MasteryGraph,
    SpacedRepetition,
    StudentTracker,
)


def test_tracker_accuracy():
    tracker = StudentTracker()
    tracker.record_attempt(Attempt(item_id="a", topic="registers", correct=True))
    tracker.record_attempt(Attempt(item_id="b", topic="registers", correct=False))
    tracker.record_attempt(Attempt(item_id="c", topic="flags", correct=True))
    assert tracker.accuracy() == 2 / 3
    assert tracker.accuracy("registers") == 0.5
    assert tracker.accuracy("flags") == 1.0


def test_tracker_metrics():
    tracker = StudentTracker()
    tracker.record_attempt(
        Attempt(
            item_id="a",
            topic="registers",
            correct=False,
            hints_used=2,
            retries=3,
            duration=15.0,
        )
    )
    assert tracker.average_hints("registers") == 2
    assert tracker.total_retries("registers") == 3
    assert tracker.completion_time("registers") == 15.0
    assert tracker.topics() == ["registers"]


def test_mastery_graph():
    graph = MasteryGraph()
    graph.record("registers", True)
    graph.record("registers", True)
    graph.record("registers", False)
    value = graph.get("registers")
    assert 0.0 <= value <= 100.0
    assert graph.get("unknown") == 0.0
    assert "registers" in graph.all()
    assert "registers" in graph.weakest()


def test_spaced_repetition_intervals():
    srs = SpacedRepetition()
    srs.add("lesson1")
    item = srs.review("lesson1", True, day=0)
    assert item.interval_days == 1
    item = srs.review("lesson1", True, day=1)
    assert item.interval_days == 3
    item = srs.review("lesson1", True, day=4)
    assert item.interval_days == 7
    item = srs.review("lesson1", False, day=11)
    assert item.interval_days == 1
    assert item.repetitions == 0


def test_spaced_repetition_due():
    srs = SpacedRepetition()
    srs.add("a")
    srs.add("b")
    srs.review("a", True, day=0)
    srs.review("b", True, day=1)
    assert "a" in srs.due_on(1)
    assert "b" not in srs.due_on(1)
    assert "b" in srs.due_on(2)
    assert "a" in srs.due_on(2)


def test_difficulty_adjuster():
    adjuster = DifficultyAdjuster()
    assert adjuster.next_difficulty("easy", 0.9) == "medium"
    assert adjuster.next_difficulty("hard", 0.2) == "medium"
    assert adjuster.next_difficulty("easy", 0.5) == "easy"
    assert adjuster.next_difficulty("expert", 0.95) == "expert"
