import asyncio

from PySide6.QtCore import QThread, Signal
from telethon import TelegramClient
from telethon.errors import (
    PasswordHashInvalidError,
    PhoneCodeInvalidError,
    SessionPasswordNeededError,
)

from app.core.config import load_telegram_config
from app.core.session import get_session_storage


class TelegramLoginWorker(QThread):
    code_sent = Signal()
    login_success = Signal(str)
    need_password = Signal()
    error_occurred = Signal(str)

    def __init__(self, phone: str, remember: bool) -> None:
        super().__init__()
        self.phone = phone
        self.remember = remember
        self.client = None
        self.phone_code_hash = None
        self._loop = None
        self.session = get_session_storage(self.phone, self.remember)

    def run(self):
        try:
            api_id, api_hash = load_telegram_config()
        except Exception as exc:
            self.error_occurred.emit(str(exc))
            return

        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)

        self.client = TelegramClient(self.session, api_id, api_hash, app_version="0.0.1")

        self._loop.run_until_complete(self._connect_and_send())
        self._loop.run_forever()

    async def _connect_and_send(self):
        try:
            await self.client.connect()
            sent_code = await self.client.send_code_request(self.phone)
            self.phone_code_hash = sent_code.phone_code_hash
            self.code_sent.emit()
        except Exception as exc:
            self.error_occurred.emit(str(exc))
            self.stop()

    def submit_code(self, code: str):
        if self._loop and self._loop.is_running():
            asyncio.run_coroutine_threadsafe(
                self._submit_code_async(code),
                self._loop,
            )

    async def _submit_code_async(self, code: str):
        try:
            await self.client.sign_in(
                phone=self.phone,
                code=code,
                phone_code_hash=self.phone_code_hash,
            )
            self.login_success.emit("success")
            self.stop()
        except SessionPasswordNeededError:
            self.need_password.emit()
        except PhoneCodeInvalidError:
            self.error_occurred.emit("Invalid verification code.")
        except Exception as exc:
            self.error_occurred.emit(str(exc))

    def submit_password(self, password: str):
        if self._loop and self._loop.is_running():
            asyncio.run_coroutine_threadsafe(
                self._submit_password_async(password),
                self._loop,
            )

    async def _submit_password_async(self, password: str):
        try:
            await self.client.sign_in(password=password)
            self.login_success.emit("success_2fa")
            self.stop()
        except PasswordHashInvalidError:
            self.error_occurred.emit("Invalid 2FA password.")
        except Exception as exc:
            self.error_occurred.emit(str(exc))

    def stop(self):
        if self._loop and self._loop.is_running():
            if self.client:
                if not self.remember and self.client.is_connected():
                    asyncio.run_coroutine_threadsafe(
                        self.client.log_out(),
                        self._loop,
                    )
                elif self.client.is_connected():
                    asyncio.run_coroutine_threadsafe(
                        self.client.disconnect(),
                        self._loop,
                    )

            self._loop.call_soon_threadsafe(self._loop.stop)
