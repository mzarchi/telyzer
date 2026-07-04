from configparser import ConfigParser
from pathlib import Path


def load_telegram_config():
    base = Path(__file__).resolve().parents[2]
    path = base / "config.ini"

    if not path.exists():
        raise FileNotFoundError("config.ini not found")

    parser = ConfigParser()
    parser.read(path, encoding="utf-8")

    if "telegram" not in parser:
        raise KeyError("[telegram] section missing")

    api_id = parser.getint("telegram", "api_id", fallback=None)
    api_hash = parser.get("telegram", "api_hash", fallback=None)

    if not api_id or not api_hash:
        raise ValueError("Invalid api_id or api_hash in config.ini")

    return {"api_id": api_id, "api_hash": api_hash}
