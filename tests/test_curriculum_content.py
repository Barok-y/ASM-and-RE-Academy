from academy.curriculum import STEP_KINDS, LessonSession, all_modules
from academy.curriculum.content._asm import asm_root
from academy.emulator import Executor


def test_every_module_has_ordered_11_step_lessons():
    for module in all_modules():
        assert module.id.startswith("module")
        assert module.lessons, module.id
        for lesson in module.lessons:
            kinds = [step.kind for step in lesson.steps]
            assert kinds == list(STEP_KINDS), lesson.id
            assert lesson.module == module.id
            assert lesson.title


def test_all_runnable_programs_assemble_and_run():
    for module in all_modules():
        for lesson in module.lessons:
            for index, step in enumerate(lesson.steps):
                if not step.program:
                    continue
                ex = Executor()
                ex.load_asm(step.program)
                ex.run()
                assert ex.status in (
                    "exited",
                    "halted",
                    "error",
                ), (lesson.id, index, ex.status, ex._error)
                if module.id != "module1":
                    # Authored programs end with a clean exit syscall.
                    assert ex.status == "exited", (lesson.id, index, ex.status, ex._error)
                    assert ex.exit_code == 0, (lesson.id, index, ex.exit_code)


def test_every_challenge_reference_passes_verification():
    failures = []
    for module in all_modules():
        for lesson in module.lessons:
            session = LessonSession(lesson)
            while session.current.kind != "challenge":
                session.advance()
            step = session.current
            assert step.expected, lesson.id
            passed, message = session.verify_challenge()
            if not passed:
                failures.append((lesson.id, message))
    assert not failures, failures


def test_runnable_steps_are_backed_by_programs():
    for module in all_modules():
        for lesson in module.lessons:
            for index, step in enumerate(lesson.steps):
                if step.kind in ("example", "walkthrough", "challenge"):
                    assert step.program, (lesson.id, index)
            assert lesson.steps[4].program, lesson.id  # example step
            assert lesson.steps[5].program, lesson.id  # walkthrough step


def test_asm_root_is_under_content_package():
    root = asm_root()
    assert root.is_dir()
    assert root.name == "asm"
