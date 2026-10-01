"""Count characters, words, reading time."""

from __future__ import annotations

import math
import re
from dataclasses import dataclass

_WORD_RE = re.compile(r"\S+", re.UNICODE)


@dataclass
class Stats:
    chars: int
    words: int
    read_min: float

    def read_label(self) -> str:
        if self.words == 0:
            return "—"
        secs = max(1, int(round(self.read_min * 60)))
        if secs < 60:
            return f"~{secs} с"
        mins = self.read_min
        if mins < 10:
            return f"~{mins:.1f} мин"
        return f"~{math.ceil(mins)} мин"


def analyze(text: str, wpm: int = 200) -> Stats:
    wpm = max(1, int(wpm))
    words = len(_WORD_RE.findall(text))
    return Stats(
        chars=len(text),
        words=words,
        read_min=(words / wpm) if words else 0.0,
    )
