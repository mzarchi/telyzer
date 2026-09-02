from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError


class TelegramAuth:
    def __init__(self, api_id, api_hash, session_path):
        self.client = TelegramClient(
            session_path,
            api_id,
            api_hash
        )

    async def login(self):
        await self.client.connect()
        if await self.client.is_user_authorized():
            print("Your session is active")
            return True
        
        phone = input("Your Phone Number: ")
        await self.client.send_code_request(phone)
        
        code = input("Enter Login Code: ")
        try:
            await self.client.sign_in(phone=phone, code=code)
            
        except SessionPasswordNeededError as spne:
            c2fa = input("Enter 2FA password: ")
            await self.client.sign_in(password=c2fa)
        print("Login seccessful")
        return True
