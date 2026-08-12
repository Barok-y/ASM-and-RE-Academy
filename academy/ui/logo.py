from __future__ import annotations

from typing import List

_PIXELS = {
    "Y": ["█ █ █", " █ █ ", "  █  ", "  █  ", "  █  "],
    "O": [" ███ ", "█   █", "█   █", "█   █", " ███ "],
    "T": ["█████", "  █  ", "  █  ", "  █  ", "  █  "],
    "D": ["████ ", "█   █", "█   █", "█   █", "████ "],
}

_HEX_BYTES = "0x59  0x4F  0x54  0x4F  0x44"


def wordmark(text: str = "YOTOD") -> List[str]:
    """Render ``text`` (default YOTOD) as 5 rows of 5-wide block letters."""
    glyphs = [_PIXELS[ch.upper()] for ch in text]
    return ["  ".join(g[i] for g in glyphs) for i in range(5)]


def _pad(line: str, width: int) -> str:
    return line.center(width)


def academy_logo(accent: str = "#c4b5fd") -> str:
    """Return the logo block as a Rich-markup string for a ``Static``."""
    width = 44
    rows = wordmark()
    lines = [
        _pad("[b #a78bfa]0x0000  fetch · decode · execute[/b #a78bfa]", width),
        "",
        *[_pad(f"[bold {accent}]{row}[/bold {accent}]", width) for row in rows],
        "",
        _pad("[b #8b5cf6]ASSEMBLY · REVERSE ENGINEERING · SYSTEMS[/b #8b5cf6]", width),
        _pad("[#a69bcb]learn it. build it. break it.[/#a69bcb]", width),
        "",
        _pad(f"[#e879f9]{_HEX_BYTES}[/#e879f9]  [dim]# YOTOD in hex[/dim]", width),
    ]
    return "\n".join(lines)


ACADEMY_LOGO = academy_logo()

__all__ = ["ACADEMY_LOGO", "academy_logo", "wordmark"]
