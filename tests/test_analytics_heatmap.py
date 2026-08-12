from academy.analytics import HeatmapAnalyzer, StudentTracker
from academy.analytics.tracker import Attempt


def _tracker_with_history() -> StudentTracker:
    tracker = StudentTracker()
    tracker.record_attempt(Attempt("q1", "registers", True, duration=5.0))
    tracker.record_attempt(Attempt("q2", "registers", True, duration=4.0))
    tracker.record_attempt(Attempt("q3", "registers", False, duration=6.0))
    tracker.record_attempt(Attempt("q4", "arith", False, duration=40.0))
    tracker.record_attempt(Attempt("q5", "arith", False, duration=50.0))
    return tracker


def test_common_mistakes_ranking():
    analyzer = HeatmapAnalyzer(_tracker_with_history())
    mistakes = analyzer.common_mistakes()
    assert mistakes == {"arith": 2, "registers": 1}


def test_weak_topics():
    analyzer = HeatmapAnalyzer(_tracker_with_history())
    assert analyzer.weak_topics() == ["arith"]
    assert analyzer.weak_topics(threshold=0.8) == ["arith", "registers"]


def test_slow_topics():
    analyzer = HeatmapAnalyzer(_tracker_with_history())
    assert analyzer.slow_topics() == ["arith"]


def test_recommendations_generated():
    analyzer = HeatmapAnalyzer(_tracker_with_history())
    recs = analyzer.recommendations()
    assert any("arith" in r for r in recs)
    assert any("60%" in r for r in recs)


def test_no_weak_areas_recommendation():
    analyzer = HeatmapAnalyzer(StudentTracker())
    recs = analyzer.recommendations()
    assert recs == ["No weak areas detected — consider harder challenges."]


def test_heatmap_shape():
    analyzer = HeatmapAnalyzer(_tracker_with_history())
    heatmap = analyzer.heatmap()
    assert set(heatmap) == {"accuracy", "average_hints", "completion_time"}
    assert heatmap["accuracy"]["arith"] == 0.0
    assert round(heatmap["accuracy"]["registers"], 3) == round(2 / 3, 3)
