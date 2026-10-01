"""Persist reading-speed unlock."""

from __future__ import annotations

import json
from pathlib import Path

_DIR = Path.home() / "AppData" / "Local" / "CountIt"
_FILE = _DIR / "settings.json"


def load() -> dict:
    try:
        data = json.loads(_FILE.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            return data
    except (OSError, json.JSONDecodeError):
        pass
    return {}


def save(data: dict) -> None:
    _DIR.mkdir(parents=True, exist_ok=True)
    _FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def get_wpm() -> int | None:
    data = load()
    if not data.get("unlocked"):
        return None
    try:
        wpm = int(data.get("wpm", 0))
    except (TypeError, ValueError):
        return None
    if wpm < 50 or wpm > 1000:
        return None
    return wpm


def set_wpm(wpm: int) -> None:
    save({"unlocked": True, "wpm": int(wpm)})


def lock() -> None:
    save({"unlocked": False})
