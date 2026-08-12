import asyncio

import pytest

pytest.importorskip("textual")

from academy.ui import (
    AcademyApp,
    AppState,
    ChallengesScreen,
    DebuggerScreen,
    LearnScreen,
    MainMenuScreen,
    NotebookScreen,
    PracticeScreen,
    ProgressScreen,
    ProjectsScreen,
    SandboxScreen,
    SettingsScreen,
)

SIZE = (120, 60)


def _make_app(tmp_path):
    return AcademyApp(state=AppState(tmp_path / "data"))


def _run(coro):
    return asyncio.run(coro)


def _select(screen, list_id, index):
    list_view = screen.query_one(list_id)
    list_view.index = index
    item = list_view.children[index]
    screen.on_list_view_selected(list_view.Selected(list_view, item, index))


class _Submitted:
    def __init__(self, value, input_widget):
        self.value = value
        self.input = input_widget


def _submit(screen, input_id, value):
    widget = screen.query_one(input_id)
    widget.value = value
    screen.on_input_submitted(_Submitted(value, widget))


def test_main_menu_has_all_options(tmp_path):
    async def scenario():
        app = _make_app(tmp_path)
        async with app.run_test(size=SIZE) as pilot:
            await pilot.pause()
            assert isinstance(app.screen, MainMenuScreen)
            for option in ("learn", "practice", "sandbox", "debugger", "quit"):
                assert app.screen.query_one(f"#menu-{option}") is not None

    _run(scenario())


def test_main_menu_shows_yotod_logo(tmp_path):
    async def scenario():
        app = _make_app(tmp_path)
        async with app.run_test(size=SIZE) as pilot:
            await pilot.pause()
            assert isinstance(app.screen, MainMenuScreen)
            logo = app.screen.query_one("#logo")
            assert "█" in logo.content  # pixel-font wordmark renders
            assert "YOTOD" in logo.content
            assert "0x59" in logo.content  # hex-flavoured footer
            # brand title carries the Yotod name
            assert "Yotod" in app.TITLE

    _run(scenario())


def test_quit_button_exits_app(tmp_path):
    async def scenario():
        app = _make_app(tmp_path)
        async with app.run_test(size=SIZE) as pilot:
            await pilot.pause()
            assert isinstance(app.screen, MainMenuScreen)
            await pilot.click("#menu-quit")
            await pilot.pause()
            assert app._running is False

    _run(scenario())


def test_menu_quit_reachable_on_small_terminals(tmp_path):
    async def scenario():
        app = _make_app(tmp_path)
        async with app.run_test(size=(80, 35)) as pilot:
            await pilot.pause()
            quit_button = app.screen.query_one("#menu-quit")
            assert quit_button.region.bottom <= app.screen.size.height
            await pilot.click("#menu-quit")
            await pilot.pause()
            assert app._running is False

    _run(scenario())


def test_settings_path_input_does_not_steal_focus(tmp_path):
    async def scenario():
        app = _make_app(tmp_path)
        async with app.run_test(size=SIZE) as pilot:
            await pilot.pause()
            await pilot.click("#menu-settings")
            await pilot.pause()
            screen = app.screen
            assert isinstance(screen, SettingsScreen)
            # the profile-path Input must not auto-focus and swallow hotkeys
            assert screen.focused is None
            before = app.current_theme.dark
            await pilot.press("d")
            await pilot.pause()
            assert app.current_theme.dark is not before
            # P focuses the path box for editing; Enter hands focus back
            await pilot.press("p")
            await pilot.pause()
            assert screen.focused is not None and screen.focused.id == "profile-path"
            path_input = screen.query_one("#profile-path")
            path_input.value = path_input.value + "-edited"
            await pilot.press("enter")
            await pilot.pause()
            assert screen.focused is None
            assert app.state.session  # still on the settings screen
            assert isinstance(app.screen, SettingsScreen)

    _run(scenario())


def test_settings_clear_state_action(tmp_path):
    async def scenario():
        app = _make_app(tmp_path)
        async with app.run_test(size=SIZE) as pilot:
            await pilot.pause()
            app.state.record_attempt("q1", "registers", True)
            app.state.record_attempt("q2", "flags", False)
            app.state.mark_lesson_complete("module1.lesson1", "module1")
            app.state.notebook.add("note", "hi", "world")
            assert app.state.sqlite.count() == 2
            assert len(app.state.notebook.entries()) == 1
            await pilot.click("#menu-settings")
            await pilot.pause()
            assert isinstance(app.screen, SettingsScreen)
            app.screen.action_clear_state()
            assert len(app.state.notebook.entries()) == 0
            assert app.state.sqlite.count() == 0
            assert app.state.session.load_progress().get("lessons") in (None, {})
            assert dict(app.state.mastery.all()) == {}
            assert len(app.state.tracker.attempts) == 0

    _run(scenario())


def test_every_menu_screen_mounts(tmp_path):
    async def scenario():
        app = _make_app(tmp_path)
        async with app.run_test(size=SIZE) as pilot:
            await pilot.pause()
            for option, expected in (
                ("learn", LearnScreen),
                ("practice", PracticeScreen),
                ("sandbox", SandboxScreen),
                ("debugger", DebuggerScreen),
                ("challenges", ChallengesScreen),
                ("projects", ProjectsScreen),
                ("notebook", NotebookScreen),
                ("progress", ProgressScreen),
                ("settings", SettingsScreen),
            ):
                await pilot.click(f"#menu-{option}")
                await pilot.pause()
                await pilot.pause()
                assert isinstance(app.screen, expected), f"{option} did not open"
                app.pop_screen()
                await pilot.pause()
                await pilot.pause()
                assert isinstance(app.screen, MainMenuScreen)

    _run(scenario())


def test_author_menu_opens_wizard(tmp_path):
    async def scenario():
        app = _make_app(tmp_path)
        async with app.run_test(size=SIZE) as pilot:
            await pilot.pause()
            await pilot.click("#menu-author")
            await pilot.pause()
            from academy.ui.authoring import AuthorModeScreen

            assert isinstance(app.screen, AuthorModeScreen)
            from academy.ui.authoring import AddContentScreen

            await pilot.press("enter")
            await pilot.pause()
            assert isinstance(app.screen, AddContentScreen)
            assert "Add a practice" in app.screen.query_one("#author-title").content

    _run(scenario())


def test_learn_opens_lesson(tmp_path):
    async def scenario():
        app = _make_app(tmp_path)
        async with app.run_test(size=SIZE) as pilot:
            await pilot.pause()
            await pilot.click("#menu-learn")
            await pilot.pause()
            screen = app.screen
            assert isinstance(screen, LearnScreen)
            from academy.ui.screens import LessonListScreen, LessonScreen

            _select(screen, "#learn-list", 0)
            await pilot.pause()
            assert isinstance(app.screen, LessonListScreen)
            _select(app.screen, "#lesson-list", 0)
            await pilot.pause()
            assert isinstance(app.screen, LessonScreen)
            assert "Fetch-Decode" in app.screen.query_one("#lesson-header").content

    _run(scenario())


def test_lesson_prediction_answer_tracks_attempt(tmp_path):
    async def scenario():
        app = _make_app(tmp_path)
        async with app.run_test(size=SIZE) as pilot:
            await pilot.pause()
            await pilot.click("#menu-learn")
            await pilot.pause()
            _select(app.screen, "#learn-list", 0)
            await pilot.pause()
            _select(app.screen, "#lesson-list", 0)
            await pilot.pause()
            lesson = app.screen
            # advance to the prediction step (index 6, kind "prediction")
            while lesson.session.current.kind != "prediction":
                lesson.action_advance()
            lesson._choose(1)
            assert "Correct" in lesson.query_one("#lesson-feedback").content
            assert app.state.sqlite.count() == 1

    _run(scenario())


def test_challenge_grade_records_attempt(tmp_path):
    async def scenario():
        app = _make_app(tmp_path)
        async with app.run_test(size=SIZE) as pilot:
            await pilot.pause()
            await pilot.click("#menu-challenges")
            await pilot.pause()
            _select(app.screen, "#challenge-list", 0)
            await pilot.pause()
            from academy.ui.screens import ChallengeScreen

            screen = app.screen
            assert isinstance(screen, ChallengeScreen)
            # first CTF challenge is ctf1: key ^ 0x1337 == 0x4242
            screen._grade("mov rax, 0x4242\nxor rax, 0x1337")
            assert "PASSED" in screen.query_one("#challenge-result").content
            assert app.state.sqlite.count() == 1

    _run(scenario())


def test_notebook_add_and_delete(tmp_path):
    async def scenario():
        app = _make_app(tmp_path)
        async with app.run_test(size=SIZE) as pilot:
            await pilot.pause()
            await pilot.click("#menu-notebook")
            await pilot.pause()
            screen = app.screen
            assert isinstance(screen, NotebookScreen)
            _submit(screen, "#notebook-input", "note|My note|content here")
            assert len(app.state.notebook.entries()) == 1
            _submit(screen, "#notebook-input", "code|mov example|mov rax, 1")
            assert len(app.state.notebook.entries()) == 2
            screen.query_one("#notebook-list").index = 0
            screen.action_delete_entry()
            assert len(app.state.notebook.entries()) == 1

    _run(scenario())


def test_projects_mission_auto(tmp_path):
    async def scenario():
        app = _make_app(tmp_path)
        async with app.run_test(size=SIZE) as pilot:
            await pilot.pause()
            await pilot.click("#menu-projects")
            await pilot.pause()
            assert isinstance(app.screen, ProjectsScreen)
            # unlock the chain so patch_license (chapter 2) is reachable
            app.state.session.save_progress({"missions": {"recover_password": "complete"}})
            entries = app.screen._missions
            patch_index = next(
                i for i, m in enumerate(entries) if m.mission_id == "patch_license"
            )
            _select(app.screen, "#missions-list", patch_index)
            await pilot.pause()
            from academy.ui.screens import MissionScreen

            screen = app.screen
            assert isinstance(screen, MissionScreen)
            screen.action_auto()
            assert "verified" in screen.query_one("#mission-result").content

    _run(scenario())


def test_mission_reference_hidden_until_hint(tmp_path):
    async def scenario():
        app = _make_app(tmp_path)
        async with app.run_test(size=SIZE) as pilot:
            await pilot.pause()
            await pilot.click("#menu-projects")
            await pilot.pause()
            assert isinstance(app.screen, ProjectsScreen)
            _select(app.screen, "#missions-list", 0)
            await pilot.pause()
            from academy.ui.screens import MissionScreen

            screen = app.screen
            assert isinstance(screen, MissionScreen)
            body = screen.query_one("#mission-body").content
            assert "reference:" not in body
            assert "mov rax, 0x5A" not in body
            assert "challenge:" in body
            # hint level 1+2: guidance, no full solution
            screen.action_hint()
            assert "mov rax, 0x5A" not in screen.query_one("#mission-result").content
            screen.action_hint()
            assert "mov rax, 0x5A" not in screen.query_one("#mission-result").content
            # third hint finally reveals the working reference
            screen.action_hint()
            assert "mov rax, 0x5A" in screen.query_one("#mission-result").content

    _run(scenario())


def test_story_campaign_final_flag_auto(tmp_path):
    async def scenario():
        app = _make_app(tmp_path)
        async with app.run_test(size=SIZE) as pilot:
            await pilot.pause()
            await pilot.click("#menu-projects")
            await pilot.pause()
            assert isinstance(app.screen, ProjectsScreen)
            app.state.session.save_progress(
                {
                    "missions": {
                        "recover_password": "complete",
                        "patch_license": "complete",
                        "map_functions": "complete",
                    }
                }
            )
            entries = app.screen._missions
            flag_idx = next(i for i, m in enumerate(entries) if m.mission_id == "extract_flag")
            _select(app.screen, "#missions-list", flag_idx)
            await pilot.pause()
            from academy.ui.screens import MissionScreen

            screen = app.screen
            assert isinstance(screen, MissionScreen)
            screen.action_auto()
            assert "FLAG CAPTURED" in screen.query_one("#mission-result").content
            assert "ASM{" in screen.query_one("#mission-result").content

    _run(scenario())


def test_challenge_input_shift_enter_inserts_newline(tmp_path):
    async def scenario():
        from academy.ui.screens import ChallengeScreen, CodeArea

        app = _make_app(tmp_path)
        async with app.run_test(size=SIZE) as pilot:
            await pilot.pause()
            await pilot.click("#menu-challenges")
            await pilot.pause()
            _select(app.screen, "#challenge-list", 0)
            await pilot.pause()
            screen = app.screen
            assert isinstance(screen, ChallengeScreen)
            area = screen.query_one("#challenge-input")
            assert isinstance(area, CodeArea)
            area.focus()
            await pilot.press("m", "o", "v")
            await pilot.press("shift+enter")
            await pilot.press("4", "2")
            await pilot.pause()
            assert area.value == "mov\n42"

    _run(scenario())


def test_sandbox_help_and_run(tmp_path):
    async def scenario():
        app = _make_app(tmp_path)
        async with app.run_test(size=SIZE) as pilot:
            await pilot.pause()
            await pilot.click("#menu-sandbox")
            await pilot.pause()
            screen = app.screen
            assert isinstance(screen, SandboxScreen)
            result = screen.handle_command("help")
            assert "step" in result.text
            result = screen.handle_command("run")
            assert "status:" in result.text
            assert "rax" in screen.query_one("#registers-panel").content

    _run(scenario())


def test_sandbox_handles_bad_command(tmp_path):
    async def scenario():
        app = _make_app(tmp_path)
        async with app.run_test(size=SIZE) as pilot:
            await pilot.pause()
            await pilot.click("#menu-sandbox")
            await pilot.pause()
            screen = app.screen
            try:
                screen.handle_command("bogus")
                raise AssertionError("expected ValueError")
            except ValueError:
                pass

    _run(scenario())


def test_debugger_steps(tmp_path):
    async def scenario():
        app = _make_app(tmp_path)
        async with app.run_test(size=SIZE) as pilot:
            await pilot.pause()
            await pilot.click("#menu-debugger")
            await pilot.pause()
            screen = app.screen
            assert isinstance(screen, DebuggerScreen)
            screen.action_step_into()
            assert "rip" in screen.query_one("#debug-status").content.lower()

    _run(scenario())


def test_progress_screen_shows_data(tmp_path):
    async def scenario():
        app = _make_app(tmp_path)
        async with app.run_test(size=SIZE) as pilot:
            await pilot.pause()
            app.state.record_attempt("q1", "registers", True)
            app.state.mark_lesson_complete("module1.lesson1", "module1")
            await pilot.click("#menu-progress")
            await pilot.pause()
            body = app.screen.query_one("#progress-body").content
            assert "lessons complete: 1" in body
            assert "module1.lesson1" in body

    _run(scenario())


def test_lesson_navigation_keys_advance_and_escape_pops(tmp_path):
    async def scenario():
        app = _make_app(tmp_path)
        async with app.run_test(size=SIZE) as pilot:
            await pilot.pause()
            await pilot.click("#menu-learn")
            await pilot.pause()
            _select(app.screen, "#learn-list", 0)
            await pilot.pause()
            _select(app.screen, "#lesson-list", 0)
            await pilot.pause()
            from academy.ui.screens import LessonListScreen, LessonScreen

            lesson = app.screen
            assert isinstance(lesson, LessonScreen)
            # lesson content and the three view panels are populated on mount
            assert lesson.query_one("#lesson-step").content
            assert lesson.query_one("#view-source").content
            assert lesson.query_one("#views").display is True
            # hidden input must not swallow keys: n advances
            await pilot.press("n")
            await pilot.pause()
            assert lesson.session.index == 1
            # escape returns to the lesson list
            await pilot.press("escape")
            await pilot.pause()
            await pilot.pause()
            assert isinstance(app.screen, LessonListScreen)

    _run(scenario())


def test_lesson_complete_advances_to_next_lesson(tmp_path):
    async def scenario():
        app = _make_app(tmp_path)
        async with app.run_test(size=SIZE) as pilot:
            await pilot.pause()
            await pilot.click("#menu-learn")
            await pilot.pause()
            _select(app.screen, "#learn-list", 0)
            await pilot.pause()
            _select(app.screen, "#lesson-list", 0)
            await pilot.pause()
            from academy.ui.screens import LessonScreen

            lesson = app.screen
            assert isinstance(lesson, LessonScreen)
            first_id = lesson.session.lesson.id
            while lesson.session.index < len(lesson.session.lesson.steps) - 1:
                lesson.action_advance()
            lesson.action_advance()
            assert "complete" in lesson.query_one("#lesson-feedback").content
            lesson.action_advance()
            await pilot.pause()
            await pilot.pause()
            assert isinstance(app.screen, LessonScreen)
            assert app.screen.session.lesson.id != first_id

    _run(scenario())


def test_lesson_verify_never_crashes_on_bad_assembly(tmp_path):
    async def scenario():
        app = _make_app(tmp_path)
        async with app.run_test(size=SIZE) as pilot:
            await pilot.pause()
            await pilot.click("#menu-learn")
            await pilot.pause()
            _select(app.screen, "#learn-list", 0)
            await pilot.pause()
            _select(app.screen, "#lesson-list", 0)
            await pilot.pause()
            from academy.ui.screens import LessonScreen

            lesson = app.screen
            assert isinstance(lesson, LessonScreen)
            while lesson.session.current.kind != "challenge":
                lesson.action_advance()
            # malformed assembly must be caught, not crash the TUI
            lesson.query_one("#lesson-input").value = "mov rax,"
            lesson.action_run_challenge()
            assert "error" in lesson.query_one("#lesson-feedback").content
            # verify on a non-challenge step gives guidance instead of silent no-op
            lesson.action_advance()  # -> reflection
            lesson.action_run_challenge()
            assert "challenge" in lesson.query_one("#lesson-feedback").content

    _run(scenario())


def test_lesson_state_panel_tracks_programs(tmp_path):
    async def scenario():
        app = _make_app(tmp_path)
        async with app.run_test(size=SIZE) as pilot:
            await pilot.pause()
            from academy.curriculum import get_module
            from academy.ui.screens import LessonScreen

            lesson_screen = LessonScreen(get_module("module1").lessons[0], app.state)
            app.push_screen(lesson_screen)
            await pilot.pause()
            await pilot.pause()
            # concept step carries an illustrative program that auto-runs
            state = app.screen.query_one("#view-state").content
            assert "rax" in state
            assert "status:" in state
            # hint action populates feedback
            app.screen.action_show_hint()
            assert "hint" in app.screen.query_one("#lesson-feedback").content

    _run(scenario())


def test_settings_toggle_dark(tmp_path):
    async def scenario():
        app = _make_app(tmp_path)
        async with app.run_test(size=SIZE) as pilot:
            await pilot.pause()
            await pilot.click("#menu-settings")
            await pilot.pause()
            assert isinstance(app.screen, SettingsScreen)
            before = app.current_theme.dark
            app.screen.action_toggle_dark()
            assert app.current_theme.dark is not before

    _run(scenario())


def test_custom_purple_theme_applied(tmp_path):
    async def scenario():
        app = _make_app(tmp_path)
        async with app.run_test(size=SIZE) as pilot:
            await pilot.pause()
            assert app.theme == "archont-ink"
            assert app.current_theme.dark
            # dark-purple/blue-black canvas, light-purple accent
            assert app.current_theme.background.startswith("#0a0")
            assert app.current_theme.accent == "#c4b5fd"

    _run(scenario())
