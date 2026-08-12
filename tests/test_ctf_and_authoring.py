import pytest

from academy.grading import Grader, sample_challenges
from academy.grading.ctf import ctf_challenges
from academy.storage import JsonStore, UserContent


def test_ctf_challenges_all_pass_reference():
    for challenge in ctf_challenges():
        grade = Grader().grade(challenge, challenge.program)
        assert grade.passed, f"{challenge.id}: reference did not pass ({grade.feedback})"
        assert grade.correctness == 1.0


def test_ctf_challenges_are_distinct_from_sample_practice():
    sample_titles = {c.title for c in sample_challenges()}
    ctf_titles = {c.title for c in ctf_challenges()}
    assert not sample_titles & ctf_titles
    assert len(ctf_challenges()) >= 5


def test_user_content_persists_challenge(tmp_path):
    store = JsonStore(tmp_path / "state.json")
    uc = UserContent(store)
    uc.add_challenge(
        title="MyChallenge",
        spec="Make RAX = 9.",
        reference="mov rax, 9",
        expected={"registers": {"rax": 9}},
    )
    reloaded = UserContent(store)
    assert len(reloaded.challenge_dicts()) == 1
    assert reloaded.challenge_dicts()[0]["title"] == "MyChallenge"


def test_user_content_persists_lesson(tmp_path):
    store = JsonStore(tmp_path / "state.json")
    uc = UserContent(store)
    uc.add_lesson(
        module="user1",
        order=1,
        title="MyLesson",
        steps=[
            {"kind": "concept", "content": "intro", "program": ""},
            {"kind": "challenge", "content": "do it", "program": "mov rax, 1"},
        ],
    )
    reloaded = UserContent(store)
    assert len(reloaded.lesson_dicts()) == 1
    assert reloaded.lesson_dicts()[0]["title"] == "MyLesson"
    assert len(reloaded.lesson_dicts()[0]["steps"]) == 2


def test_user_content_remove_challenge(tmp_path):
    store = JsonStore(tmp_path / "state.json")
    uc = UserContent(store)
    c = uc.add_challenge(
        title="T", spec="S", reference="mov rax, 1", expected={"registers": {"rax": 1}}
    )
    uc.remove_challenge(c["id"])
    assert uc.challenge_dicts() == []


def test_authoring_screen_saves_practice(tmp_path):
    pytest.importorskip("textual")
    import asyncio

    from academy.ui import AcademyApp, AppState
    from academy.ui.authoring import AddContentScreen
    from academy.ui.screens import PracticeScreen

    async def scenario():
        app = AcademyApp(state=AppState(tmp_path / "data"))
        async with app.run_test(size=(120, 60)) as pilot:
            await pilot.pause()
            await pilot.click("#menu-practice")
            await pilot.pause()
            ps = app.screen
            assert isinstance(ps, PracticeScreen)
            ascreen = AddContentScreen(ps, app.state)
            app.push_screen(ascreen)
            await pilot.pause()
            await pilot.pause()
            # wizard flow: path (skip import), title, spec, reg, asm, solution
            ascreen._advance_field("")  # no file import — type asm by hand
            ascreen._advance_field("Sum to 9")
            ascreen._advance_field("Leave 3 + 6 in RAX")
            ascreen._advance_field("rax:9")
            ascreen._advance_field("")  # no more registers
            ascreen._advance_field("mov rax, 3\nadd rax, 6")
            ascreen._advance_field("Load 3 into RAX\\nAdd 6 to RAX")
            await pilot.pause()
            assert len(app.state.user_content.challenge_dicts()) == 1
            titles = [c.title for c in ps._all_challenges()]
            assert "Sum to 9" in titles
            assert app.state.user_content.challenge_dicts()[0]["solution"] == (
                "Load 3 into RAX\nAdd 6 to RAX"
            )

    asyncio.run(scenario())


def test_authoring_import_from_asm_file(tmp_path):
    import asyncio

    from academy.ui import AcademyApp, AppState
    from academy.ui.authoring import AddContentScreen
    from academy.ui.screens import PracticeScreen

    source = tmp_path / "sum.asm"
    source.write_text("mov rax, 3\nadd rax, 6\n")

    async def scenario():
        app = AcademyApp(state=AppState(tmp_path / "data"))
        async with app.run_test(size=(120, 60)) as pilot:
            await pilot.pause()
            await pilot.click("#menu-practice")
            await pilot.pause()
            ps = app.screen
            assert isinstance(ps, PracticeScreen)
            ascreen = AddContentScreen(ps, app.state)
            app.push_screen(ascreen)
            await pilot.pause()
            await pilot.pause()
            ascreen._advance_field(str(source))  # import from absolute path
            assert ascreen._fields["asm"] == "mov rax, 3\nadd rax, 6\n"
            assert "imported_from" in ascreen._fields
            ascreen._advance_field("Sum from file")
            ascreen._advance_field("Leave 9 in RAX")
            ascreen._advance_field("rax:9")
            ascreen._advance_field("")  # no more registers
            ascreen._advance_field("mov rax, 3\nadd rax, 6")  # keep imported asm
            ascreen._advance_field("")  # empty solution
            await pilot.pause()
            assert len(app.state.user_content.challenge_dicts()) == 1
            assert app.state.user_content.challenge_dicts()[0]["title"] == "Sum from file"

    asyncio.run(scenario())


def test_authoring_import_rejects_bad_path(tmp_path):
    import asyncio

    from academy.ui import AcademyApp, AppState
    from academy.ui.authoring import AddContentScreen
    from academy.ui.screens import PracticeScreen

    async def scenario():
        app = AcademyApp(state=AppState(tmp_path / "data"))
        async with app.run_test(size=(120, 60)) as pilot:
            await pilot.pause()
            await pilot.click("#menu-practice")
            await pilot.pause()
            ps = app.screen
            ascreen = AddContentScreen(ps, app.state)
            app.push_screen(ascreen)
            await pilot.pause()
            await pilot.pause()
            # relative path is rejected with guidance
            ascreen._advance_field("not/absolute.asm")
            assert "isn't absolute" in ascreen.query_one("#author-status").content
            assert "title" not in ascreen._fields
            # nonexistent absolute path is rejected
            ascreen._advance_field("/nonexistent/nope.asm")
            assert "no file at" in ascreen.query_one("#author-status").content
            # empty path skips the import
            ascreen._advance_field("")
            assert ascreen._stage == "title"

    asyncio.run(scenario())
    import asyncio


    async def scenario():
        app = AcademyApp(state=AppState(tmp_path / "data"))
        async with app.run_test(size=(120, 60)) as pilot:
            await pilot.pause()
            await pilot.click("#menu-practice")
            await pilot.pause()
            ps = app.screen
            assert isinstance(ps, PracticeScreen)
            ascreen = AddContentScreen(ps, app.state)
            ascreen._mode = "lesson"
            app.push_screen(ascreen)
            await pilot.pause()
            await pilot.pause()
            ascreen._advance_field("My Lesson")
            ascreen._advance_field("concept|A register is a tiny cell")
            ascreen._advance_field("challenge|Write RAX = 7")
            ascreen._advance_field("")  # no more steps
            ascreen._advance_field("concept|mov rax, 1")  # prog for concept
            ascreen._advance_field("challenge|mov rax, 7")  # prog for challenge
            await pilot.pause()
            lessons = app.state.user_content.lesson_dicts()
            assert len(lessons) == 1
            assert lessons[0]["title"] == "My Lesson"
            assert len(lessons[0]["steps"]) == 2
            assert lessons[0]["steps"][0]["program"] == "mov rax, 1"

    asyncio.run(scenario())


def test_authoring_challenge_saves_flag_and_output(tmp_path):
    import asyncio

    from academy.ui import AcademyApp, AppState
    from academy.ui.authoring import AddContentScreen
    from academy.ui.screens import ChallengesScreen

    async def scenario():
        app = AcademyApp(state=AppState(tmp_path / "data"))
        async with app.run_test(size=(120, 60)) as pilot:
            await pilot.pause()
            await pilot.click("#menu-challenges")
            await pilot.pause()
            cs = app.screen
            assert isinstance(cs, ChallengesScreen)
            ascreen = AddContentScreen(cs, app.state, mode="challenge")
            app.push_screen(ascreen)
            await pilot.pause()
            ascreen._advance_field("")  # no import
            ascreen._advance_field("Serial Gate")
            ascreen._advance_field("Make RAX the accepted serial, and print ACCEPTED.")
            ascreen._advance_field("rax:4660")  # reg auto-advances to next field
            ascreen._advance_field("ACCEPTED")  # expected output
            ascreen._advance_field("ASM{SERIAL_GATE_1337}")  # final flag
            ascreen._advance_field("mov rax, 0x4242\nxor rax, 0x1337")
            ascreen._advance_field("XOR the serial tag\\nStore into RAX")
            ascreen._advance_field("registers")
            ascreen._advance_field("medium")
            await pilot.pause()
            dicts = app.state.user_content.challenge_dicts()
            assert dicts[0]["title"] == "Serial Gate"
            assert dicts[0]["flag"] == "ASM{SERIAL_GATE_1337}"
            assert dicts[0]["expected"]["output"] == "ACCEPTED"
            assert dicts[0]["challenge_type"] == "registers"
            assert dicts[0]["difficulty"] == "medium"

    asyncio.run(scenario())


def test_user_content_flag_round_trips_into_challenge_model(tmp_path):
    from academy.storage import JsonStore, UserContent
    from academy.ui.screens import _challenge_from_dict

    store = JsonStore(tmp_path / "state.json")
    uc = UserContent(store)
    uc.add_challenge(
        title="T", spec="S", reference="mov rax, 1",
        expected={"registers": {"rax": 1}}, flag="ASM{FLAG}",
    )
    ch = _challenge_from_dict(uc.challenge_dicts()[0])
    assert ch.flag == "ASM{FLAG}"


def test_lesson_save_generates_per_line_register_trace(tmp_path):
    import asyncio

    from academy.ui import AcademyApp, AppState
    from academy.ui.authoring import AddContentScreen

    async def scenario():
        app = AcademyApp(state=AppState(tmp_path / "data"))
        async with app.run_test(size=(120, 60)) as pilot:
            await pilot.pause()
            ps = app.screen
            ascreen = AddContentScreen(ps, app.state, mode="lesson")
            app.push_screen(ascreen)
            await pilot.pause()
            ascreen._advance_field("Registers lesson")
            ascreen._advance_field("concept|A register holds a value")
            ascreen._advance_field("challenge|Make RAX 9")
            ascreen._advance_field("")  # no more steps
            ascreen._advance_field("concept|mov rax, 3\nadd rax, 6")
            ascreen._advance_field("challenge|mov rax, 3\nadd rax, 6")
            await pilot.pause()
            lessons = app.state.user_content.lesson_dicts()
            assert lessons[0]["title"] == "Registers lesson"
            assert len(lessons[0]["steps"]) == 2
            trace = lessons[0]["steps"][0].get("trace", "")
            assert "mov rax, 3" in trace
            assert "rax=0x3" in trace
            assert "register effects per line" in trace

    asyncio.run(scenario())


def test_trace_describes_per_line_register_change():
    from academy.ui.authoring import AddContentScreen

    trace = AddContentScreen._trace_program("mov rax, 5\nadd rax, 4")
    assert "mov rax, 5" in trace
    assert "rax=0x5" in trace
    assert "add rax, 4" in trace
    assert "rax=0x9" in trace


def test_trace_empty_on_invalid_asm():
    from academy.ui.authoring import AddContentScreen

    assert AddContentScreen._trace_program("not real asm (((") == ""
