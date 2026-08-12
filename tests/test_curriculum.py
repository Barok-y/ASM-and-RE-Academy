from academy.curriculum import (
    STEP_KINDS,
    LessonSession,
    all_modules,
    get_module,
    module_index,
)


def test_module1_structure():
    module = get_module("module1")
    assert module is not None
    assert module.title == "CPU Architecture and Registers"
    assert len(module.lessons) == 7


def test_scaffolded_modules():
    index = module_index()
    assert set(index) == {
        "module1",
        "module2",
        "module3",
        "module4",
        "module5",
        "module6",
        "module7",
    }
    assert index["module2"].title == "Memory and Stack"
    assert index["module7"].title == "Dynamic Analysis"
    assert all(len(module.lessons) > 0 for module in index.values())


def test_all_modules_ordered():
    modules = all_modules()
    assert [m.order for m in modules] == list(range(1, len(modules) + 1))


def test_template_lesson_has_all_11_steps():
    module = get_module("module1")
    mov = next(lesson for lesson in module.lessons if lesson.id == "module1.lesson3")
    kinds = [s.kind for s in mov.steps]
    assert kinds == list(STEP_KINDS)


def test_session_prediction_grading():
    module = get_module("module1")
    mov = next(lesson for lesson in module.lessons if lesson.id == "module1.lesson3")
    session = LessonSession(mov)
    while session.current.kind != "prediction":
        session.advance()
    assert "Incorrect" in session.respond(3)
    assert "14" in session.respond(3)
    assert "Correct" in session.respond(1)


def test_session_walkthrough_runs_program():
    module = get_module("module1")
    mov = next(lesson for lesson in module.lessons if lesson.id == "module1.lesson3")
    session = LessonSession(mov)
    while session.current.kind != "walkthrough":
        session.advance()
    result = session.run_program()
    assert "status:" in result
    assert session.executor.get_register("rbx") == 5


def test_challenge_verification_pass_and_fail():
    module = get_module("module1")
    add = next(lesson for lesson in module.lessons if lesson.id == "module1.lesson4")
    session = LessonSession(add)
    while session.current.kind != "challenge":
        session.advance()
    passed, message = session.verify_challenge()
    assert passed, message
    failed, _ = session.verify_challenge("mov rax, 0\nmov rbx, 0")
    assert not failed


def test_challenge_accepts_plain_value_answer():
    from academy.curriculum.content.module1 import lesson_fde

    session = LessonSession(lesson_fde())
    while session.current.kind != "challenge":
        session.advance()
    passed, message = session.verify_challenge("5")
    assert passed, message
    passed_hex, _ = session.verify_challenge("0x5")
    assert passed_hex
    wrong, _ = session.verify_challenge("6")
    assert not wrong


def test_challenge_flags():
    module = get_module("module1")
    flags = next(lesson for lesson in module.lessons if lesson.id == "module1.lesson6")
    session = LessonSession(flags)
    while session.current.kind != "challenge":
        session.advance()
    passed, message = session.verify_challenge()
    assert passed, message


def test_three_views():
    module = get_module("module1")
    mov = next(lesson for lesson in module.lessons if lesson.id == "module1.lesson3")
    session = LessonSession(mov)
    while session.current.kind != "example":
        session.advance()
    views = session.three_views()
    assert set(views) == {"source", "assembly", "state"}
    assert "mov rax, 5" in views["assembly"]
    assert "rax" in views["state"]


def test_advance_through_lesson():
    module = get_module("module1")
    fde = next(lesson for lesson in module.lessons if lesson.id == "module1.lesson1")
    session = LessonSession(fde)
    count = 0
    while session.advance() is not None:
        count += 1
    assert count == len(fde.steps) - 1
