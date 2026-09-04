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
        self.loop.run_until_complete(config.ta._create_client())
        
    def cls(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def connect(self):
        is_valid = self.loop.run_until_complete(config.ta.connect())
        if not is_valid:
            self.loop.run_until_complete(config.ta.login())

    def is_session_active(self):
        if config.ta is None or config.ta.client is None:
            return False
        return self.loop.run_until_complete(config.ta.connect())

    def get_me(self):
        if config.ta is None or config.ta.client is None:
            return None
        return self.loop.run_until_complete(config.ta.client.get_me())

    def logout(self):
        submit = input("Are you sure you want to logout? (y/n): ")
        if submit.lower() != "n":
            async def _logout():
                await config.ta.client.log_out()
                print("Logged out!")
                input("Press Enter to continue...")
            self.loop.run_until_complete(_logout())
        else:
            print("Logout cancelled.")
            input("Press Enter to continue...")


    def disconnect(self):
        if config.ta and config.ta.client:
            try:
                self.loop.run_until_complete(config.ta.client.disconnect())
            except:
                pass
