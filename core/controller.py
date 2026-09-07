from telethon.tl.functions.contacts import GetContactsRequest
from datetime import datetime
from config import Config
from math import ceil
import messages as msg
import asyncio
import csv
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

    def get_datetime(self):
        result = {}
        now = datetime.now()
        result.update({"file_name": now.strftime("%Y-%m-%d_%H-%M-%S")})
        result.update({"unix": str(int(now.timestamp()))})
        return result

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

                case "2":
                    target = input("Enter target username: ")
                    self.chat_stream(target)
                    self.cls()

                case "3":
                    break

    def contacts_list(self):
        dt = self.get_datetime()

        async def _get_contacts():
            result = await self.cf.ta.client(GetContactsRequest(hash=0))
            return result.users

        contacts = self.loop.run_until_complete(_get_contacts())

        if not contacts:
            print("No contacts found!")
            input("Press Enter to continue...")
            return

        contacts.sort(key=lambda c: (c.first_name or '').lower())

        file_path = f"{self.cf.contacts_lists}Contacts_{dt['file_name']}.txt"

        with open(file_path, "a", encoding="utf-8") as f:
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

                txt_fl = f"{i}. {name}\n"
                txt_fl += f"   ├─ ID: {contact.id}\n"
                txt_fl += f"   ├─ Access Hash: {contact.access_hash}\n"
                txt_fl += f"   ├─ Username: {username}\n"
                txt_fl += f"   ├─ Phone: +{phone}\n"
                txt_fl += f"   ├─ Lang Code: {contact.lang_code or 'None'}\n"
                txt_fl += f"   ├─ Status: {status}\n"
                txt_fl += f"   ├─ Bot: {'Yes' if contact.bot else 'No'}\n"
                txt_fl += f"   ├─ Verified: {'Yes' if contact.verified else 'No'}\n"
                txt_fl += f"   ├─ Premium: {'Yes' if contact.premium else 'No'}\n"
                txt_fl += f"   ├─ Scam: {'Yes' if contact.scam else 'No'}\n"
                txt_fl += f"   ├─ Fake: {'Yes' if contact.fake else 'No'}\n"
                txt_fl += f"   ├─ Restricted: {'Yes' if contact.restricted else 'No'}\n"
                txt_fl += f"   ├─ Restriction Reason: {restriction_reason}\n"
                txt_fl += f"   ├─ Contact: {'Yes' if contact.contact else 'No'}\n"
                txt_fl += f"   ├─ Mutual: {'Yes' if contact.mutual_contact else 'No'}\n"
                txt_fl += f"   ├─ Deleted: {'Yes' if contact.deleted else 'No'}\n"
                txt_fl += f"   ├─ Support: {'Yes' if contact.support else 'No'}\n"
                txt_fl += f"   ├─ Stories Hidden: {'Yes' if contact.stories_hidden else 'No'}\n"
                txt_fl += f"   ├─ Stories Unavailable: {'Yes' if contact.stories_unavailable else 'No'}\n"
                txt_fl += f"   └─ Photo ID: {contact.photo.photo_id if contact.photo else 'No photo'}\n\n"

                f.write(txt_fl)
                print(f"{i:<4}. ID: {contact.id:<12} Phone: +{phone:<12}")

        print(f"\nContacts saved to: {file_path}")
        input("Press Enter to continue...")

    def detect_message_type(self, msg):
        if msg.raw_text and not msg.media:
            return "text"

        if getattr(msg, "photo", None):
            return "photo"

        if getattr(msg, "video", None):
            return "video"

        if getattr(msg, "voice", None):
            return "voice"

        if getattr(msg, "video_note", None):
            return "video_note"

        if getattr(msg, "sticker", None):
            return "sticker"

        if getattr(msg, "document", None):
            return "document"

        if msg.media:
            return "media"

        return "unknown"

    def chat_stream(self, target_user):
        me = self.get_me()
        my_username = me.username or str(me.id)
        target_user = target_user.replace("@", "")
        dt = self.get_datetime()
        output_csv = f"{self.cf.chat_csv}{my_username}-{target_user}-{dt['file_name']}.csv"

        async def _stream():
            entity = await self.cf.ta.client.get_entity(target_user)

            total = await self.cf.ta.client.get_messages(entity, limit=0)
            total_messages = total.total

            with open(output_csv, mode="w", encoding="utf-8", newline="") as csvfile:
                fieldnames = [
                    "row_number",
                    "message_id",
                    "publish_timestamp",
                    "publish_datetime",
                    "sender_id",
                    "is_outgoing",
                    "message_type",
                    "message_text",
                    "message_edited"
                ]

                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()

                count = 1
                last_rows = []

                async for msg in self.cf.ta.client.iter_messages(entity, limit=None, reverse=True):
                    message_data = {
                        "row_number": count,
                        "message_id": msg.id,
                        "publish_timestamp": int(msg.date.timestamp()),
                        "publish_datetime": msg.date.isoformat(),
                        "sender_id": msg.sender_id,
                        "is_outgoing": msg.out,
                        "message_type": self.detect_message_type(msg),
                        "message_text": msg.raw_text,
                        "message_edited": hasattr(msg, "edit_date") and msg.edit_date is not None
                    }

                    writer.writerow(message_data)

                    last_rows.append([
                        count,
                        message_data["message_id"],
                        message_data["publish_timestamp"],
                        message_data["publish_datetime"],
                        message_data["sender_id"],
                        message_data["is_outgoing"]
                    ])

                    count += 1

                    if total_messages > 0:
                        percent = ceil(count / total_messages * 100)
                        print(f"\rReading messages: {count}/{total_messages} ({percent}%)", end="")
                    else:
                        print(f"\rReading messages: {count}", end="")

            print(f"\nChat stream saved to: {output_csv}")

            print("Last 5 messages:")
            print("-" * 80)
            print(f"{'Row':<6} {'Msg ID':<12} {'Timestamp':<15} {'Datetime':<25} {'Sender ID':<15} {'Outgoing':<10}")
            print("-" * 80)

            for row in last_rows[-5:]:
                row_num, msg_id, ts, dt_str, sender_id, is_out = row
                print(f"{row_num:<6}{msg_id:<12} {ts:<15} {dt_str:<25} {sender_id:<15} {'Yes' if is_out else 'No':<10}")

        self.loop.run_until_complete(_stream())
        input("Press Enter to continue...")