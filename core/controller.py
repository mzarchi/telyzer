from telegram.auth import TelegramAuth
import config
import asyncio
import os


class TelyzerController:
    def __init__(self):
        self.ta = TelegramAuth(
            config.session_path,
            config.api_id,
            config.api_hash
        )
        self.client = None

    def connect(self):
        return asyncio.run(self.ta.login())

    def cls(self):
        os.system('cls' if os.name == 'nt' else 'clear')
