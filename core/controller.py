import config
import asyncio
import os


class TelyzerController:
    def __init__(self):
        if config.ta is None:
            from telegram.auth import TelegramAuth
            config.ta = TelegramAuth(
                config.session_path,
                config.api_id,
                config.api_hash,
                config.app_version
            )
            
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

    def connect(self):
        is_valid = self.loop.run_until_complete(config.ta.connect())
        if not is_valid:
            self.loop.run_until_complete(config.ta.login())

    def cls(self):
        os.system('cls' if os.name == 'nt' else 'clear')