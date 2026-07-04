import os
import sys
from telethon.sessions import MemorySession, SQLiteSession

def get_session_storage(phone_number: str, remember: bool):
    if remember:
        if sys.platform == "win32":
            base_dir = os.path.join(os.environ.get("APPDATA", ""), "Telyzer")
        else:
            base_dir = os.path.expanduser("~/.config/telyzer")
            
        session_dir = os.path.join(base_dir, "sessions")
        os.makedirs(session_dir, exist_ok=True)
        
        session_path = os.path.join(session_dir, f"sess_{phone_number.replace('+', '')}")
        return SQLiteSession(session_path)
    else:
        return MemorySession()
