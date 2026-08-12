"""Curriculum data model: modules, lessons, and the 11-step lesson loop."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

STEP_KINDS = (
    "concept",
    "intuition",
    "analogy",
    "visualization",
    "example",
    "walkthrough",
    "prediction",
    "response",
    "feedback",
    "challenge",
    "reflection",
)


@dataclass
class LessonStep:
    kind: str
    content: str = ""
    high_level: str = ""
    program: str = ""
    question: str = ""
    options: List[str] = field(default_factory=list)
    answer: Optional[int] = None
    feedback: Dict[int, str] = field(default_factory=dict)
    expected: Dict[str, Any] = field(default_factory=dict)
    hint: str = ""
    model_answer: str = ""
    keywords: List[str] = field(default_factory=list)
    trace: str = ""


@dataclass
class Lesson:
    id: str
    module: str
    title: str
    order: int
    steps: List[LessonStep] = field(default_factory=list)


@dataclass
class Module:
    id: str
    title: str
    order: int
    lessons: List[Lesson] = field(default_factory=list)
