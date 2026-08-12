
from academy.grading import (
    DIFFICULTIES,
    Grader,
    HintEngine,
    sample_challenges,
)


def test_hint_engine_levels_and_penalty():
    challenge = sample_challenges()[0]
    hints = HintEngine()
    assert len(hints.hints_for(challenge, 1)) == 1
    assert len(hints.hints_for(challenge, 5)) == 5
    assert len(hints.hints_for(challenge, 99)) == 5
    assert hints.penalty(0) == 0
    assert hints.penalty(2) == 20


def test_grader_passes_correct_submission():
    challenge = sample_challenges()[0]
    grade = Grader().grade(challenge, "mov rax, 42\nmov rbx, rax")
    assert grade.passed
    assert grade.correctness == 1.0
    assert grade.total >= 80


def test_grader_fails_wrong_value():
    challenge = sample_challenges()[0]
    grade = Grader().grade(challenge, "mov rax, 43\nmov rbx, rax")
    assert not grade.passed
    assert grade.correctness == 0.0
    assert any("register rbx" in f for f in grade.feedback)
    assert any("review" in r for r in grade.review)


def test_grader_hint_penalty_lowers_score():
    challenge = sample_challenges()[0]
    base = Grader().grade(challenge, "mov rax, 42\nmov rbx, rax", hints_used=0)
    hinted = Grader().grade(challenge, "mov rax, 42\nmov rbx, rax", hints_used=4)
    assert hinted.total < base.total
    assert hinted.understanding < 1.0


def test_grader_efficiency_rewards_shorter_program():
    challenge = next(c for c in sample_challenges() if c.id == "ch5")
    grader = Grader()
    long_grade = grader.grade(challenge, "mov rbx, 0x2004\nmov rax, rbx")
    short_grade = grader.grade(challenge, "mov rbx, 0x2000\nlea rax, [rbx + 4]")
    assert short_grade.efficiency >= long_grade.efficiency


def test_grader_flags_challenge():
    challenge = next(c for c in sample_challenges() if c.id == "ch3")
    grade = Grader().grade(challenge, "mov rax, 5\nsub rax, 5")
    assert grade.passed
    assert grade.correctness == 1.0


def test_grader_explanation_affects_score():
    challenge = sample_challenges()[0]
    grader = Grader()
    no_expl = grader.grade(challenge, "mov rax, 42\nmov rbx, rax", explanation="")
    with_expl = grader.grade(
        challenge,
        "mov rax, 42\nmov rbx, rax",
        explanation="MOV copies the value of RAX into RBX after loading 42 into RAX.",
    )
    assert with_expl.total > no_expl.total


def test_difficulties_and_types_valid():
    challenges = sample_challenges()
    assert len(challenges) >= 10
    for challenge in challenges:
        assert challenge.difficulty in DIFFICULTIES


def test_grader_invalid_assembly_reports_zero():
    challenge = sample_challenges()[0]
    grade = Grader().grade(challenge, "mov rax,")
    assert grade.correctness == 0.0
    assert not grade.passed
