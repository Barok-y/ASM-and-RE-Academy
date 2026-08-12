from __future__ import annotations

from textual.app import App
from textual.binding import Binding
from textual.screen import Screen
from textual.theme import Theme

from .screens import (
    ChallengesScreen,
    DebuggerScreen,
    LearnScreen,
    MainMenuScreen,
    NotebookScreen,
    PracticeScreen,
    ProfileScreen,
    ProgressScreen,
    ProjectsScreen,
    SandboxScreen,
    SettingsScreen,
)
from .state import AppState

_ARCH_PLUM_INK = Theme(
    name="archont-ink",
    primary="#8b5cf6",
    secondary="#a78bfa",
    accent="#c4b5fd",
    warning="#e879f9",
    error="#fb7185",
    success="#34d399",
    foreground="#e8e0f8",
    background="#0a0614",
    surface="#140c26",
    panel="#1b1034",
    boost="#6d28d9",
    dark=True,
    variables={
        "text-muted": "#a69bcb",
        "text": "#e8e0f8",
        "block-cursor-text": "#0a0614",
    },
)


class AcademyApp(App):
    TITLE = "Yotod — Assembly & Reverse Engineering Academy"
    SUB_TITLE = "learn assembly · reverse engineer · break things"
    BINDINGS = [
        Binding("ctrl+q", "quit", "Quit", priority=True),
        Binding("ctrl+k", "command_palette", "Command palette", priority=True),
    ]
    CSS_PATH = "app.tcss"

    SCREENS = {
        "learn": LearnScreen,
        "practice": PracticeScreen,
        "sandbox": SandboxScreen,
        "debugger": DebuggerScreen,
        "challenges": ChallengesScreen,
        "projects": ProjectsScreen,
        "notebook": NotebookScreen,
        "profile": ProfileScreen,
        "progress": ProgressScreen,
        "settings": SettingsScreen,
    }

    def __init__(self, state: AppState | None = None) -> None:
        super().__init__()
        self.state = state or AppState()

    def on_mount(self) -> None:
        try:
            self.register_theme(_ARCH_PLUM_INK)
            self.theme = _ARCH_PLUM_INK.name
        except Exception:
            pass
        self.push_screen(MainMenuScreen())

    def get_screen(self, screen_name: str) -> Screen:
        if isinstance(screen_name, Screen):
            return screen_name
        if screen_name not in self.SCREENS:
            raise KeyError(f"unknown screen: {screen_name}")
        return super().get_screen(screen_name)

    def action_command_palette(self) -> None:
        from .screens import PaletteScreen

        self.push_screen(PaletteScreen(self.state))
