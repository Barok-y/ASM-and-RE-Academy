"""Textual TUI for the academy."""

from .app import AcademyApp
from .screens import (
    DEFAULT_PROGRAM,
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
from .state import AppState

__all__ = [
    "AcademyApp",
    "AppState",
    "ChallengesScreen",
    "DEFAULT_PROGRAM",
    "DebuggerScreen",
    "LearnScreen",
    "MainMenuScreen",
    "NotebookScreen",
    "PracticeScreen",
    "ProgressScreen",
    "ProjectsScreen",
    "SandboxScreen",
    "SettingsScreen",
]
