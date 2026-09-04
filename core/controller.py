import messages as msg
from config import Config
import asyncio
import os


class TelyzerController:
    cf = None
    def __init__(self):
        self.cf = Config()
        if self.cf.ta is None:
            from telegram.auth import TelegramAuth
            self.cf.ta = TelegramAuth(
                self.cf.session_path,
                self.cf.api_id,
                self.cf.api_hash,
                self.cf.app_version
            )
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self.cf.ta._create_client())

    def cls(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def connect(self):
        is_valid = self.loop.run_until_complete(self.cf.ta.connect())
        if not is_valid:
            self.loop.run_until_complete(self.cf.ta.login())

    def is_session_active(self):
        if self.cf.ta is None or self.cf.ta.client is None:
            return False
        return self.loop.run_until_complete(self.cf.ta.connect())

    def get_me(self):
        if self.cf.ta is None or self.cf.ta.client is None:
            return None
        return self.loop.run_until_complete(self.cf.ta.client.get_me())

    def logout(self):
        submit = input("Are you sure you want to logout? (y/n): ")
        if submit.lower() != "n":
            async def _logout():
                await self.cf.ta.client.log_out()
                await self.cf.ta.client.disconnect()
                self.cf.ta.client = None
                print("Logged out!")
                input("Press Enter to continue...")
            self.loop.run_until_complete(_logout())
        else:
            print("Logout cancelled.")
            input("Press Enter to continue...")

    def disconnect(self):
        if self.cf.ta and self.cf.ta.client:
            try:
                self.loop.run_until_complete(self.cf.ta.client.disconnect())
            except:
                pass

    def contacts(self):
        self.cls()
        while True:
            user_choose = input(msg.msg_contacts)
            match user_choose:
                case "1":
                    self.contacts_list()
                    self.cls()

                case "3":
                    break

    def contacts_list(self):
        from telethon.tl.functions.contacts import GetContactsRequest

        async def _get_contacts():
            result = await self.cf.ta.client(GetContactsRequest(hash=0))
            return result.users

        contacts = self.loop.run_until_complete(_get_contacts())

        if not contacts:
            print("No contacts found!")
            input("Press Enter to continue...")
            return

        contacts.sort(key=lambda c: (c.first_name or '').lower())

        for i, contact in enumerate(contacts, 1):
            name = f"{contact.first_name or ''} {contact.last_name or ''}".strip()
            username = f"@{contact.username}" if contact.username else "No username"
            phone = contact.phone or "No phone"

            restriction_reason = ""
            if contact.restriction_reason:
                reasons = []
                for r in contact.restriction_reason:
                    reasons.append(f"{r.platform}: {r.reason}")
                restriction_reason = ", ".join(reasons)
            else:
                restriction_reason = "None"

            status = "No status"
            if contact.status:
                from telethon.tl.types import UserStatusOnline, UserStatusOffline, UserStatusRecently, UserStatusLastWeek, UserStatusLastMonth
                if isinstance(contact.status, UserStatusOnline):
                    status = "Online"
                elif isinstance(contact.status, UserStatusOffline):
                    status = f"Offline (last seen: {contact.status.was_online})"
                elif isinstance(contact.status, UserStatusRecently):
                    status = "Recently"
                elif isinstance(contact.status, UserStatusLastWeek):
                    status = "Last week"
                elif isinstance(contact.status, UserStatusLastMonth):
                    status = "Last month"
                else:
                    status = str(contact.status)

            print(f"{i}. {name}")
            print(f"   ├─ ID: {contact.id}")
            print(f"   ├─ Access Hash: {contact.access_hash}")
            print(f"   ├─ Username: {username}")
            print(f"   ├─ Phone: {phone}")
            print(f"   ├─ Lang Code: {contact.lang_code or 'None'}")
            print(f"   ├─ Status: {status}")
            print(f"   ├─ Bot: {'Yes' if contact.bot else 'No'}")
            print(f"   ├─ Verified: {'Yes' if contact.verified else 'No'}")
            print(f"   ├─ Premium: {'Yes' if contact.premium else 'No'}")
            print(f"   ├─ Scam: {'Yes' if contact.scam else 'No'}")
            print(f"   ├─ Fake: {'Yes' if contact.fake else 'No'}")
            print(f"   ├─ Restricted: {'Yes' if contact.restricted else 'No'}")
            print(f"   ├─ Restriction Reason: {restriction_reason}")
            print(f"   ├─ Contact: {'Yes' if contact.contact else 'No'}")
            print(f"   ├─ Mutual: {'Yes' if contact.mutual_contact else 'No'}")
            print(f"   ├─ Deleted: {'Yes' if contact.deleted else 'No'}")
            print(f"   ├─ Support: {'Yes' if contact.support else 'No'}")
            print(f"   ├─ Stories Hidden: {'Yes' if contact.stories_hidden else 'No'}")
            print(f"   ├─ Stories Unavailable: {'Yes' if contact.stories_unavailable else 'No'}")
            print(f"   └─ Photo ID: {contact.photo.photo_id if contact.photo else 'No photo'}")
            print()

        input("Press Enter to continue...")