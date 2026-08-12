from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List


@dataclass(frozen=True)
class LearningPath:
    path_id: str
    name: str
    module_ids: List[str]
    description: str = ""

    def as_dict(self) -> dict:
        return {
            "id": self.path_id,
            "name": self.name,
            "module_ids": list(self.module_ids),
            "description": self.description,
        }


LEARNING_PATHS: List[LearningPath] = [
    LearningPath(
        "path_a",
        "Beginner Assembly",
        ["module1", "module2", "module3", "module4", "module5", "module6", "module7"],
        "Core curriculum from first program through ABI and OS internals.",
    ),
    LearningPath(
        "path_b",
        "Reverse Engineering",
        ["module1", "module2", "module4", "module5", "module7"],
        "Assembly fundamentals plus RE lab and binary patching.",
    ),
    LearningPath(
        "path_c",
        "CTF Preparation",
        ["module1", "module2", "module4", "module5", "module6", "module7"],
        "Focus on challenges, exploits, and patching.",
    ),
    LearningPath(
        "path_d",
        "Systems Programming",
        ["module1", "module2", "module3", "module4", "module6"],
        "Compilers, ABIs, and systems-facing assembly.",
    ),
    LearningPath(
        "path_e",
        "OS Internals",
        ["module1", "module2", "module4", "module6", "module7"],
        "From registers to kernel-facing concerns.",
    ),
    LearningPath(
        "path_f",
        "Compiler Internals",
        ["module1", "module3", "module4", "module5"],
        "Instruction semantics and generated code reading.",
    ),
]


def path_index() -> Dict[str, LearningPath]:
    return {path.path_id: path for path in LEARNING_PATHS}


def get_path(path_id: str) -> LearningPath | None:
    return path_index().get(path_id)
