from __future__ import annotations

from configparser import ConfigParser
from pathlib import Path


CONFIG_FILE = Path(__file__).resolve().parents[2] / "config.ini"


def load_telegram_config() -> tuple[int, str]:
    parser = ConfigParser()

    if not CONFIG_FILE.exists():
        raise FileNotFoundError(
            f"Config file not found: {CONFIG_FILE}"
        )

    parser.read(CONFIG_FILE, encoding="utf-8")

    if not parser.has_section("telegram"):
        raise ValueError("Missing [telegram] section in config.ini")

    api_id_raw = parser.get("telegram", "api_id", fallback="").strip()
    api_hash = parser.get("telegram", "api_hash", fallback="").strip()

    if not api_id_raw:
        raise ValueError("telegram.api_id is empty in config.ini")

    if not api_hash:
        raise ValueError("telegram.api_hash is empty in config.ini")

    try:
        api_id = int(api_id_raw)
    except ValueError as exc:
        raise ValueError("telegram.api_id must be an integer") from exc

    return api_id, api_hash
