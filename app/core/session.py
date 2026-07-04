from __future__ import annotations

import os
from pathlib import Path
from typing import Optional


def _sessions_dir() -> Path:
    """
    Returns the directory where Telegram session files are stored.
    Windows: %APPDATA%\\Telyzer\\sessions
    Fallback: ~/.telyzer/sessions
    """
    appdata = os.getenv("APPDATA")
    if appdata:
        base = Path(appdata) / "Telyzer" / "sessions"
    else:
        base = Path.home() / ".telyzer" / "sessions"

    base.mkdir(parents=True, exist_ok=True)
    return base


def _clean_digits(phone_number: str) -> str:
    return "".join(ch for ch in (phone_number or "") if ch.isdigit())


def get_session_path(phone_number: str) -> Path:
    """
    Example output:
      %APPDATA%\\Telyzer\\sessions\\session_98912xxxxxxx.session
    """
    digits = _clean_digits(phone_number)
    if not digits:
        # avoid creating "session_.session"
        digits = "unknown"
    return _sessions_dir() / f"session_{digits}.session"


def get_last_session_phone() -> Optional[str]:
    """
    Tries to find the newest saved session file and returns a phone string like '+98912...'.
    It scans:
      %APPDATA%\\Telyzer\\sessions\\session_<digits>.session

    Returns None if no valid session file exists.
    """
    base = _sessions_dir()

    candidates: list[Path] = []
    for p in base.glob("session_*.session"):
        # ignore weird ones
        digits = p.stem.replace("session_", "")
        if digits.isdigit() and len(digits) >= 7:
            candidates.append(p)

    if not candidates:
        return None

    newest = max(candidates, key=lambda x: x.stat().st_mtime)
    digits = newest.stem.replace("session_", "")
    return f"+{digits}"
