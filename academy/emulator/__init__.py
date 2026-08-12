"""Emulator layer: x86-64 execution engine with single-step, snapshots,
breakpoints, watchpoints, and reverse stepping."""

from .executor import (
    DEFAULT_SEGMENTS,
    STACK_TOP,
    STATUS_BREAKPOINT,
    STATUS_ERROR,
    STATUS_EXITED,
    STATUS_HALTED,
    STATUS_READY,
    STATUS_RUNNING,
    ExecutionHalted,
    Executor,
)
from .memory import MemoryModel, Segment
from .snapshot import StateDiff, StateSnapshot
from .stack import Stack

__all__ = [
    "DEFAULT_SEGMENTS",
    "STACK_TOP",
    "STATUS_BREAKPOINT",
    "STATUS_ERROR",
    "STATUS_EXITED",
    "STATUS_HALTED",
    "STATUS_READY",
    "STATUS_RUNNING",
    "ExecutionHalted",
    "Executor",
    "MemoryModel",
    "Segment",
    "Stack",
    "StateDiff",
    "StateSnapshot",
]
