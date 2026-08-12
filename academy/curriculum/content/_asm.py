from __future__ import annotations

from pathlib import Path

_ASM_ROOT = Path(__file__).parent / "asm"


def read_asm(relative_path: str) -> str:
    """Read a lesson program from ``asm/<relative_path>`` as text."""
    path = _ASM_ROOT / relative_path
    if not path.is_file():
        raise FileNotFoundError(f"missing assembly file: {path}")
    return path.read_text().strip()


def asm_root() -> Path:
    """Absolute path of the directory holding the authored ``.asm`` files."""
    return _ASM_ROOT
