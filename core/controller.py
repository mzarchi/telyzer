from telethon.tl.functions.contacts import GetContactsRequest
import matplotlib.pyplot as plt
from datetime import datetime
from config import Config
from math import ceil
import messages as msg
import pandas as pd
import asyncio
import pytz
import glob
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
                    self.chat_visualization()
                    self.cls()

                case "4":
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
        my_user_id = me.id
        target_user = target_user.replace("@", "")
        dt = self.get_datetime()

        async def _stream():
            entity = await self.cf.ta.client.get_entity(target_user)
            target_user_id = entity.id

            user_folder = f"{self.cf.chat_csv}{target_user_id}/"
            os.makedirs(user_folder, exist_ok=True)

            output_csv = f"{user_folder}{target_user_id}-{my_user_id}-{dt['file_name']}.csv"

            pattern = f"{user_folder}{target_user_id}-{my_user_id}-*.csv"
            existing_files = glob.glob(pattern)

            start_from_id = 0
            old_file_path = None
            append_mode = False

            if existing_files:
                old_file_path = max(existing_files, key=os.path.getsize)

                max_msg_id = 0
                with open(old_file_path, "r", encoding="utf-8") as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        try:
                            msg_id = int(row["message_id"])
                            if msg_id > max_msg_id:
                                max_msg_id = msg_id
                        except:
                            pass

                if max_msg_id > 0:
                    print(f"Previous file found: {os.path.basename(old_file_path)}")
                    print(f"File size: {os.path.getsize(old_file_path)} bytes")
                    print(f"Last message ID: {max_msg_id}")
                    user_choice = input("Get only newer messages? (y/n): ")

                    if user_choice.lower() == "y":
                        start_from_id = max_msg_id
                        append_mode = True
                        print(f"Continuing from message ID: {start_from_id}")
                    else:
                        print("Starting from beginning...")

            # محاسبه تعداد پیام‌های جدید
            total_new = 0
            if start_from_id > 0:
                all_messages = await self.cf.ta.client.get_messages(
                    entity,
                    min_id=start_from_id,
                    limit=0
                )
                total_new = all_messages.total
            else:
                all_messages = await self.cf.ta.client.get_messages(entity, limit=0)
                total_new = all_messages.total

            if append_mode and old_file_path:
                import shutil
                shutil.copy2(old_file_path, output_csv)
                print(f"Copied previous file to: {os.path.basename(output_csv)}")

            mode = "a" if append_mode else "w"

            with open(output_csv, mode=mode, encoding="utf-8", newline="") as csvfile:
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

                if append_mode:
                    count = 0
                    with open(output_csv, "r", encoding="utf-8") as f:
                        reader = csv.DictReader(f)
                        for row in reader:
                            count += 1
                    count += 1
                    print(f"Previous messages: {count - 1}")
                else:
                    writer.writeheader()
                    count = 1

                last_rows = []
                new_count = 0

                async for msg in self.cf.ta.client.iter_messages(
                    entity,
                    min_id=start_from_id if start_from_id else 0,
                    limit=None,
                    reverse=True
                ):
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
                    new_count += 1

                    if total_new > 0:
                        percent = ceil(new_count / total_new * 100)
                        print(f"\rReading new messages: {new_count}/{total_new} ({percent}%)", end="")
                    else:
                        print(f"\rReading new messages: {new_count}", end="")

            print(f"\nChat stream saved to: {output_csv}")

            if new_count == 0:
                print("No new messages found!")
            else:
                print("\nLast 5 messages:")
                print("-" * 80)
                print(f"{'Row':<6} {'Msg ID':<12} {'Timestamp':<15} {'Datetime':<25} {'Sender ID':<15} {'Outgoing':<10}")
                print("-" * 80)

                for row in last_rows[-5:]:
                    row_num, msg_id, ts, dt_str, sender_id, is_out = row
                    print(f"{row_num:<6}{msg_id:<12} {ts:<15} {dt_str:<25} {sender_id:<15} {'Yes' if is_out else 'No':<10}")

        self.loop.run_until_complete(_stream())
        input("Press Enter to continue...")
        
    def chat_visualization(self):
        self.cls()
        
        if not os.path.exists(self.cf.chat_csv):
            print("No chat CSV folder found!")
            input("Press Enter to continue...")
            return
        
        user_folders = [f for f in os.listdir(self.cf.chat_csv) if os.path.isdir(os.path.join(self.cf.chat_csv, f))]
        
        if not user_folders:
            print("No user folders found!")
            input("Press Enter to continue...")
            return
        
        print("User folders:")
        for i, folder in enumerate(user_folders, 1):
            folder_path = os.path.join(self.cf.chat_csv, folder)
            csv_files = glob.glob(os.path.join(folder_path, "*.csv"))
            print(f"{i}. {folder} ({len(csv_files)} CSV files)")
        
        folder_choice = input("\nSelect folder number: ")
        try:
            folder_idx = int(folder_choice) - 1
            selected_folder = user_folders[folder_idx]
        except:
            print("Invalid choice!")
            input("Press Enter to continue...")
            return
        
        folder_path = os.path.join(self.cf.chat_csv, selected_folder)
        csv_files = glob.glob(os.path.join(folder_path, "*.csv"))
        
        if not csv_files:
            print("No CSV files in this folder!")
            input("Press Enter to continue...")
            return
        
        csv_files.sort(key=os.path.getsize, reverse=True)
        
        print(f"\nCSV files in {selected_folder}:")
        for i, file in enumerate(csv_files, 1):
            file_name = os.path.basename(file)
            file_size = os.path.getsize(file) / 1024  # KB
            print(f"{i}. {file_name} ({file_size:.1f} KB)")
        
        file_choice = input("\nSelect file number: ")
        try:
            file_idx = int(file_choice) - 1
            selected_file = csv_files[file_idx]
        except:
            print("Invalid choice!")
            input("Press Enter to continue...")
            return
        
        self.plot_chat(selected_file)


    def plot_chat(self, csv_path):
        csv_name = os.path.basename(csv_path)
        df = pd.read_csv(csv_path)
        df["publish_datetime"] = pd.to_datetime(df["publish_datetime"])
        
        iran_tz = pytz.timezone("Asia/Tehran")
        df["publish_datetime"] = df["publish_datetime"].dt.tz_convert(iran_tz)
        
        df = df.sort_values("publish_datetime")
        df["hour"] = (df["publish_datetime"].dt.hour +
                    df["publish_datetime"].dt.minute / 60)
        start_date = df["publish_datetime"].min()
        df["days_from_start"] = (
            (df["publish_datetime"] - start_date).dt.total_seconds() / 86400)
        
        names = csv_name.split("-")
        my_user_id = names[0]
        target_user_id = names[1].split("_")[0]
        my_msgs = df[df["is_outgoing"] == True]
        other_msgs = df[df["is_outgoing"] == False]
        
        print(f"User {my_user_id}: {len(my_msgs)} messages")
        print(f"User {target_user_id}: {len(other_msgs)} messages")
        
        images_folder = f"{self.cf.chat_images}"
        os.makedirs(images_folder, exist_ok=True)
        
        plt.figure(figsize=(8, 4))
        
        plt.scatter(
            my_msgs["days_from_start"],
            my_msgs["hour"],
            s=1,
            alpha=0.6,
            color="#d62728",
            label=f"{my_user_id} ({len(my_msgs)})"
        )
        
        plt.scatter(
            other_msgs["days_from_start"],
            other_msgs["hour"],
            s=1,
            alpha=0.6,
            color="#1f77b4",
            label=f"{target_user_id} ({len(other_msgs)})"
        )
        
        plt.xlabel("Days from First Message")
        plt.ylabel("Hour of Day")
        plt.ylim(0, 24)
        
        plt.grid(axis='y', linestyle='--', alpha=0.9)
        plt.legend()
        
        today_dt = datetime.now().strftime("%Y%m%d-%H%M%S")
        plt.title("Chat Activity Distribution Over Time")
        
        output_image = f"{images_folder}{my_user_id}-{target_user_id}-{today_dt}.jpg"
        plt.savefig(output_image, dpi=600)
        plt.show()
        
        print(f"\nPlot saved to: {output_image}")