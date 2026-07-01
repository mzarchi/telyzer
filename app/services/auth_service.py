import asyncio
from PySide6.QtCore import QObject, Signal


class AuthService(QObject):
    status_changed = Signal(str)
    auth_success = Signal()
    error_occurred = Signal(str)