from telethon import TelegramClient


class TelegramAuth:
    def __init__(self, api_id, api_hash, session_path):
        self.client = TelegramClient(
            session_path,
            api_id,
            api_hash
        )

    async def login(self):
        await self.client.start()
        if await self.client.is_user_authorized():
            return True
        return False
