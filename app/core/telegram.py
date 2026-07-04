from __future__ import annotations

import asyncio
import queue
import threading
from dataclasses import dataclass
from typing import Optional

from PySide6.QtCore import QThread, Signal

from telethon import TelegramClient
from telethon.errors import (
    FloodWaitError,
    PhoneNumberBannedError,
    PhoneNumberFloodError,
    SessionPasswordNeededError,
    SendCodeUnavailableError,
)
from telethon.sessions import MemorySession, SQLiteSession

from app.core.config import load_telegram_config
from app.core.session import get_session_path


@dataclass
class _Action:
    name: str
    payload: dict


class TelegramLoginWorker(QThread):
    code_sent = Signal()
    need_password = Signal()
    login_success = Signal(object)
    error_occurred = Signal(str)

    session_checked = Signal(bool)

    def __init__(self, phone_number: str, remember: bool = True) -> None:
        super().__init__()
        self.phone_number = (phone_number or "").strip()
        self.remember = bool(remember)

        self.client: Optional[TelegramClient] = None
        self.loop: Optional[asyncio.AbstractEventLoop] = None

        self._actions: "queue.Queue[_Action]" = queue.Queue()
        self._stop_evt = threading.Event()

        self._phone_code_hash = None

        cfg = load_telegram_config()
        self.api_id = int(cfg["api_id"])
        self.api_hash = str(cfg["api_hash"])

    def run(self) -> None:
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        try:
            self.loop.run_until_complete(self._main())
        finally:
            try:
                pending = asyncio.all_tasks(self.loop)
                for t in pending:
                    t.cancel()
                if pending:
                    self.loop.run_until_complete(
                        asyncio.gather(*pending, return_exceptions=True))
            except Exception:
                pass
            self.loop.close()

    async def _main(self) -> None:
        session = self._make_session()
        self.client = TelegramClient(
            session=session,
            api_id=self.api_id,
            api_hash=self.api_hash,
            device_model="Telyzer (Telegram Analyzer)",
            system_version="Windows",
            app_version="vC36-2607",
            lang_code="en",
        )

        try:
            await self.client.connect()
        except Exception as e:
            self.error_occurred.emit(f"Connect failed: {e}")
            return

        try:
            while not self._stop_evt.is_set():
                try:
                    act = self._actions.get(timeout=0.2)
                except queue.Empty:
                    await asyncio.sleep(0.05)
                    continue

                name = act.name
                try:
                    if name == "stop":
                        break
                    elif name == "check_session":
                        await self._check_session_impl()
                    elif name == "send_code":
                        await self._send_code_impl()
                    elif name == "submit_code":
                        await self._submit_code_impl(act.payload.get("code", ""))
                    elif name == "submit_password":
                        await self._submit_password_impl(act.payload.get("password", ""))
                except Exception as e:
                    self.error_occurred.emit(str(e))
        finally:
            try:
                await self.client.disconnect()
            except Exception:
                pass

    def _make_session(self):
        if self.remember:
            if not self.phone_number:
                return MemorySession()
            path = get_session_path(self.phone_number)
            return SQLiteSession(str(path))
        return MemorySession()

    def stop(self) -> None:
        self._stop_evt.set()
        self._actions.put(_Action("stop", {}))

    def check_active_session(self) -> None:
        self._actions.put(_Action("check_session", {}))

    async def _check_session_impl(self) -> None:
        if not self.client:
            self.session_checked.emit(False)
            return
        try:
            ok = await self.client.is_user_authorized()
            self.session_checked.emit(bool(ok))
        except Exception:
            self.session_checked.emit(False)

    def send_code(self) -> None:
        self._actions.put(_Action("send_code", {}))

    async def _send_code_impl(self) -> None:
        if not self.client:
            self.error_occurred.emit("Client not ready.")
            return

        phone = (self.phone_number or "").strip()
        if not phone.startswith("+"):
            self.error_occurred.emit(
                "Phone must be in international format, e.g. +98912xxxxxxx")
            return

        try:
            self._phone_code_hash = await self.client.send_code_request(phone)
            self.code_sent.emit()
        except FloodWaitError as e:
            self.error_occurred.emit(f"Flood wait: wait {e.seconds} seconds.")
        except PhoneNumberBannedError:
            self.error_occurred.emit("This phone number is banned.")
        except PhoneNumberFloodError:
            self.error_occurred.emit(
                "Too many attempts for this phone number. Try later.")
        except SendCodeUnavailableError:
            self.error_occurred.emit(
                "Send code unavailable. Try later or use Telegram app code.")
        except Exception as e:
            self.error_occurred.emit(str(e))

    def submit_code(self, code: str) -> None:
        self._actions.put(_Action("submit_code", {"code": code}))

    async def _submit_code_impl(self, code: str) -> None:
        if not self.client:
            self.error_occurred.emit("Client not ready.")
            return

        phone = (self.phone_number or "").strip()
        if not phone.startswith("+"):
            self.error_occurred.emit(
                "Phone must be in international format, e.g. +98912xxxxxxx")
            return

        if not self._phone_code_hash:
            self.error_occurred.emit("No code hash. Please send code first.")
            return

        try:
            await self.client.sign_in(
                phone=phone,
                code=str(code).strip(),
                phone_code_hash=self._phone_code_hash.phone_code_hash,
            )
            self.login_success.emit(True)
        except SessionPasswordNeededError:
            self.need_password.emit()
        except FloodWaitError as e:
            self.error_occurred.emit(f"Flood wait: wait {e.seconds} seconds.")
        except Exception as e:
            self.error_occurred.emit(str(e))

    def submit_password(self, password: str) -> None:
        self._actions.put(_Action("submit_password", {"password": password}))

    async def _submit_password_impl(self, password: str) -> None:
        if not self.client:
            self.error_occurred.emit("Client not ready.")
            return
        try:
            await self.client.sign_in(password=str(password))
            self.login_success.emit(True)
        except FloodWaitError as e:
            self.error_occurred.emit(f"Flood wait: wait {e.seconds} seconds.")
        except Exception as e:
            self.error_occurred.emit(str(e))
