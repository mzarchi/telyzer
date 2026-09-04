from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError


class TelegramAuth:
    def __init__(self, session_path, api_id, api_hash, app_version):
        self.session_path = session_path
        self.api_id = api_id
        self.api_hash = api_hash
        self.app_version = app_version
        self.client = None

    async def _create_client(self):
        if self.client is None:
            self.client = TelegramClient(
                session=self.session_path,
                api_id=self.api_id,
                api_hash=self.api_hash,
                app_version=self.app_version,
            )
        return self.client

    async def connect(self):
        await self._create_client()
        await self.client.connect()
        return await self.client.is_user_authorized()

    async def login(self):
        await self._create_client()
        await self.client.connect()
        
        if await self.client.is_user_authorized():
            print("Your session is active")
            return True

        phone = input("Your Phone Number: ")
        await self.client.send_code_request(phone)

        code = input("Enter Login Code: ")
        try:
            await self.client.sign_in(phone=phone, code=code)
        except SessionPasswordNeededError:
            c2fa = input("Enter 2FA password: ")
            await self.client.sign_in(password=c2fa)

        print("Login successful")
        return True