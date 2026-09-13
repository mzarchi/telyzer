from config import Config
import matplotlib
matplotlib.use('TkAgg')
matplotlib.rcParams['font.family'] = ['Tahoma', 'Segoe UI Emoji', 'Segoe UI Symbol', 'sans-serif']
import matplotlib.pyplot as plt
from telethon.tl.types import UserStatusOnline, UserStatusOffline, UserStatusRecently, UserStatusLastWeek, UserStatusLastMonth
from telethon.tl.functions.contacts import GetContactsRequest
from telethon.tl.functions.users import GetFullUserRequest
from matplotlib.ticker import MultipleLocator, FixedLocator
from telegram.auth import TelegramAuth
from collections import Counter
from datetime import datetime
from math import ceil

import messages as msg
import mplcursors
import pandas as pd
import requests
import asyncio
import shutil
import pytz
import glob
import csv
import sys
import os


class TelyzerController:
    cf = None

    def __init__(self):
        self.cf = Config()
        if self.cf.ta is None:
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

    def log(self, text):
        dt = self.get_datetime()
        file_path = f"{self.cf.system_logs}log_{dt['log_name']}.txt"
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(f"[{dt['file_name']}] {text}")

    def get_datetime(self):
        result = {}
        now = datetime.now()
        result.update({"file_name": now.strftime("%Y-%m-%d_%H-%M-%S")})
        result.update({"log_name": now.strftime("%Y-%m-%d")})
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
                async def _cleanup():
                    await self.cf.ta.client.disconnect()
                    await asyncio.sleep(0.3)

                self.loop.run_until_complete(_cleanup())

                pending = asyncio.all_tasks(self.loop)
                for task in pending:
                    task.cancel()

                if pending:
                    self.loop.run_until_complete(
                        asyncio.gather(*pending, return_exceptions=True)
                    )

                self.loop.close()
            except:
                pass

    def contacts(self):
        self.cls()
        while True:
            user_choose = input(msg.msg_contacts)
            match user_choose:
                case "1":
                    target = input("Enter username: ")
                    self.user_lookup(target)
                    self.cls()

                case "2":
                    self.contacts_list()
                    self.cls()

                case "3":
                    target = input("Enter target username: ")
                    self.chat_stream(target)
                    selected_file = self.chat_visualization()
                    if selected_file:
                        self.plot_chat(selected_file)
                    self.cls()

                case "4":
                    try:
                        selected_file = self.chat_visualization()
                        if selected_file:
                            self.plot_chat(selected_file)
                        self.cls()
                    except Exception as e:
                        self.log(f"Error in chat visualization: {str(e)}")
                        print(f"Error: {str(e)}")
                        input("Press Enter to continue...")

                case "b":
                    break

    def contacts_list(self):
        self.cls()
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

        file_path = f"{self.cf.contact_lists}Contacts_{dt['file_name']}.csv"

        fieldnames = [
            "row_number",
            "id",
            "access_hash",
            "first_name",
            "last_name",
            "username",
            "phone",
            "lang_code",
            "status",
            "bot",
            "verified",
            "premium",
            "scam",
            "fake",
            "restricted",
            "restriction_reason",
            "contact",
            "mutual",
            "deleted",
            "support",
            "stories_hidden",
            "stories_unavailable",
            "photo_id"
        ]

        with open(file_path, "w", encoding="utf-8", newline="") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

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

                contact_data = {
                    "row_number": i,
                    "id": contact.id,
                    "access_hash": contact.access_hash,
                    "first_name": contact.first_name or "",
                    "last_name": contact.last_name or "",
                    "username": contact.username or "",
                    "phone": phone,
                    "lang_code": contact.lang_code or "",
                    "status": status,
                    "bot": contact.bot,
                    "verified": contact.verified,
                    "premium": contact.premium,
                    "scam": contact.scam,
                    "fake": contact.fake,
                    "restricted": contact.restricted,
                    "restriction_reason": restriction_reason,
                    "contact": contact.contact,
                    "mutual": contact.mutual_contact,
                    "deleted": contact.deleted,
                    "support": contact.support,
                    "stories_hidden": contact.stories_hidden,
                    "stories_unavailable": contact.stories_unavailable,
                    "photo_id": contact.photo.photo_id if contact.photo else ""
                }

                writer.writerow(contact_data)
                
                print(f"{i:<6}  {contact.id:<14}  +{phone:<15}  {name}")

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
        self.cls()
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
                shutil.copy2(old_file_path, output_csv)
                os.remove(old_file_path)
                print(f"Copied previous file to: {os.path.basename(output_csv)}")
                print(f"Removed old file: {os.path.basename(old_file_path)}")

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
        input("Press Enter to show plot ...")
        
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
        
        return selected_file



    def plot_chat(self, csv_path):
        self.cls()
        csv_name = os.path.basename(csv_path)
        df = pd.read_csv(csv_path)
        df = df.dropna(subset=["sender_id"])
        df["sender_id"] = df["sender_id"].astype("Int64")
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
        plt.ylim(0, 25)
        
        plt.gca().yaxis.set_major_locator(FixedLocator([0, 5, 10, 15, 20]))
        plt.gca().yaxis.set_minor_locator(MultipleLocator(1))

        plt.grid(which='major', axis='y', linestyle='--', alpha=0.9) # every 5 hours
        plt.grid(which='minor', axis='y', linestyle='--', alpha=0.5) # every 1 hour
        plt.legend()
        
        today_dt = datetime.now().strftime("%Y%m%d-%H%M%S")
        plt.title("Chat Activity Distribution Over Time")
        
        output_image = f"{images_folder}{my_user_id}-{target_user_id}-{today_dt}.jpg"
        plt.savefig(output_image, dpi=600)
        plt.show()
        
        print(f"\nPlot saved to: {output_image}")
        
    def groups(self):
        self.cls()
        while True:
            user_choose = input(msg.msg_groups)
            match user_choose:
                case "1":
                    target = input("Enter group username: ")
                    self.group_stream(target)

                case "2":
                    selected_file = self.explore_group_files()
                    if selected_file:
                        self.plot_group(selected_file)
                    self.cls()

                case "b":
                    break


    def group_stream(self, target_group):
        me = self.get_me()
        target_group = target_group.replace("@", "")
        if target_group.lstrip("-").isdigit():
            target_group = int(target_group)
            
        dt = self.get_datetime()

        async def _stream():
            if isinstance(target_group, int):
                entity = None
                async for dialog in self.cf.ta.client.iter_dialogs():
                    if dialog.entity.id == abs(target_group):
                        entity = dialog.entity
                        break
                if entity is None:
                    print("Group not found in your dialogs!")
                    return
            else:
                entity = await self.cf.ta.client.get_entity(target_group)

            if not (hasattr(entity, 'megagroup') or hasattr(entity, 'title')):
                print("This is not a group!")
                return

            group_id = entity.id
            group_folder = f"{self.cf.group_csv}{group_id}/"
            os.makedirs(group_folder, exist_ok=True)

            output_csv = f"{group_folder}{group_id}-{dt['file_name']}.csv"

            pattern = f"{group_folder}{group_id}-*.csv"
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
                shutil.copy2(old_file_path, output_csv)
                os.remove(old_file_path)
                print(f"Copied previous file to: {os.path.basename(output_csv)}")
                print(f"Removed old file: {os.path.basename(old_file_path)}")

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

            print(f"\nGroup stream saved to: {output_csv}")

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


    def explore_group_files(self):
        self.cls()

        if not os.path.exists(self.cf.group_csv):
            print("No group CSV folder found!")
            input("Press Enter to continue...")
            return None

        group_folders = [f for f in os.listdir(self.cf.group_csv) if os.path.isdir(os.path.join(self.cf.group_csv, f))]

        if not group_folders:
            print("No group folders found!")
            input("Press Enter to continue...")
            return None

        print("Group folders:")
        for i, folder in enumerate(group_folders, 1):
            folder_path = os.path.join(self.cf.group_csv, folder)
            csv_files = glob.glob(os.path.join(folder_path, "*.csv"))
            print(f"{i}. {folder} ({len(csv_files)} CSV files)")

        folder_choice = input("\nSelect folder number (or 'b' to back): ")
        if folder_choice.lower() == "b":
            return None

        try:
            folder_idx = int(folder_choice) - 1
            selected_folder = group_folders[folder_idx]
        except:
            print("Invalid choice!")
            input("Press Enter to continue...")
            return None

        folder_path = os.path.join(self.cf.group_csv, selected_folder)
        csv_files = glob.glob(os.path.join(folder_path, "*.csv"))

        if not csv_files:
            print("No CSV files in this folder!")
            input("Press Enter to continue...")
            return None

        csv_files.sort(key=os.path.getsize, reverse=True)

        print(f"\nCSV files in {selected_folder}:")
        for i, file in enumerate(csv_files, 1):
            file_name = os.path.basename(file)
            file_size = os.path.getsize(file) / 1024
            print(f"{i}. {file_name} ({file_size:.1f} KB)")

        file_choice = input("\nSelect file number (or 'b' to back): ")
        if file_choice.lower() == "b":
            return None

        try:
            file_idx = int(file_choice) - 1
            selected_file = csv_files[file_idx]
        except:
            print("Invalid choice!")
            input("Press Enter to continue...")
            return None

        return selected_file


    def plot_group(self, csv_path):
        self.cls()
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
        group_id = names[0]
        group_id_val = group_id
        if str(group_id).lstrip("-").isdigit():
            group_id_val = int(group_id)

        sender_counts = Counter(df["sender_id"])
        top_senders = [sender for sender, _ in sender_counts.most_common(10)]

        print(f"Group ID: {group_id_val}")
        print(f"Total messages: {len(df)}")
        print(f"Total senders: {len(sender_counts)}")
        
        print(f"\nTop 10 active members:")
        for sender_id, count in sender_counts.most_common(10):
            print(f"  {sender_id}: {count} messages")

        images_folder = f"{self.cf.group_csv}../images/"
        os.makedirs(images_folder, exist_ok=True)

        plt.figure(figsize=(10, 5))

        colors = ["#d62728", "#1f77b4", "#2ca02c", "#ff7f0e", "#9467bd",
          "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf"]

        other_df = df[~df["sender_id"].isin(top_senders)]
        if not other_df.empty:
            plt.scatter(
                other_df["days_from_start"],
                other_df["hour"],
                s=2,
                alpha=0.3,
                color="gray",
                label=f"Others ({len(other_df)})"
            )

        for idx, sender_id in enumerate(top_senders):
            sender_df = df[df["sender_id"] == sender_id]
            plt.scatter(
                sender_df["days_from_start"],
                sender_df["hour"],
                s=2,
                alpha=0.7,
                color=colors[idx % len(colors)],
                label=f"{sender_id} ({len(sender_df)})"
            )

        plt.xlabel("Days from First Message")
        plt.ylabel("Hour of Day")
        plt.ylim(0, 25)

        plt.grid(axis='y', linestyle='--', alpha=0.9)
        plt.legend(loc='best', fontsize=8)

        today_dt = datetime.now().strftime("%Y%m%d-%H%M%S")
        async def _get_group_name():
            try:
                entity = await self.cf.ta.client.get_entity(group_id_val)
                return entity.title
            except:
                return group_id

        group_name = self.loop.run_until_complete(_get_group_name())
        plt.title(f"Group Activity Distribution - {group_name}")
        
        output_image = f"{images_folder}group-{group_id}-{today_dt}.jpg"
        plt.savefig(output_image, dpi=300)
        plt.show()

        print(f"\nPlot saved to: {output_image}")

    def user_lookup(self, target_user):
        self.cls()
        target_user = target_user.replace("@", "")
        
        async def _lookup():
            try:
                entity = await self.cf.ta.client.get_entity(target_user)
                
                name = f"{entity.first_name or ''} {entity.last_name or ''}".strip()
                username = f"@{entity.username}" if entity.username else "None"
                phone = entity.phone or "Hidden"
                user_id = entity.id
                lang_code = entity.lang_code or "None"
                
                status = "No status"
                if entity.status:
                    if isinstance(entity.status, UserStatusOnline):
                        status = "Online"
                    elif isinstance(entity.status, UserStatusOffline):
                        status = f"Offline (last seen: {entity.status.was_online})"
                    elif isinstance(entity.status, UserStatusRecently):
                        status = "Recently"
                    elif isinstance(entity.status, UserStatusLastWeek):
                        status = "Last week"
                    elif isinstance(entity.status, UserStatusLastMonth):
                        status = "Last month"
                    else:
                        status = str(entity.status)
                
                full = await self.cf.ta.client(GetFullUserRequest(entity.id))
                bio = ""
                if hasattr(full, 'full_user') and full.full_user.about:
                    bio = full.full_user.about
                
                print("User Lookup Result:")
                print("-" * 50)
                print(f"Name:          {name}")
                print(f"Username:      {username}")
                print(f"ID:            {user_id}")
                print(f"Phone:         {phone}")
                print(f"Lang Code:     {lang_code}")
                print(f"Status:        {status}")
                print(f"Bio:           {bio}")
                print(f"Bot:           {'Yes' if entity.bot else 'No'}")
                print(f"Verified:      {'Yes' if entity.verified else 'No'}")
                print(f"Premium:       {'Yes' if entity.premium else 'No'}")
                print(f"Scam:          {'Yes' if entity.scam else 'No'}")
                print(f"Fake:          {'Yes' if entity.fake else 'No'}")
                print(f"Restricted:    {'Yes' if entity.restricted else 'No'}")
                print(f"Deleted:       {'Yes' if entity.deleted else 'No'}")
                print(f"Contact:       {'Yes' if entity.contact else 'No'}")
                print(f"Mutual:        {'Yes' if entity.mutual_contact else 'No'}")
                print(f"Photo ID:      {entity.photo.photo_id if entity.photo else 'No photo'}")
                print("-" * 50)
                
            except Exception as e:
                print(f"Error: {e}")
        
        self.loop.run_until_complete(_lookup())
        input("Press Enter to continue...")

    def developers(self):
        self.cls()
        url = "https://api.github.com/repos/mzarchi/telyzer/stats/contributors"

        try:
            response = requests.get(url)

            if response.status_code == 202:
                print("Stats are being computed. Please try again in a few seconds.")
                input("Press Enter to continue...")
                return

            if response.status_code != 200:
                print(f"Error: {response.status_code}")
                input("Press Enter to continue...")
                return

            contributors = response.json()

            if not contributors:
                print("No contributors found.")
                input("Press Enter to continue...")
                return

            total_commits = sum(c["total"] for c in contributors)

            contributors.sort(key=lambda c: c["total"], reverse=True)

            print("Telyzer Developers", end="")
            print("-" * 42)
            print(f"{'Rank':<6} {'Username':<20} {'Commits':<10} {'Share':<10}")
            print("-" * 60)

            for i, c in enumerate(contributors, 1):
                login = c["author"]["login"] if c["author"] else "Unknown"
                commits = c["total"]
                percentage = (commits / total_commits) * 100
                print(f"{i:<6} {login:<20} {commits:<10} {percentage:.1f}%")

        except Exception as e:
            print(f"Error: {e}")

        input("\nPress Enter to continue...")

    def check_for_update(self):
        update_url = "https://api.github.com/repos/mzarchi/telyzer/releases/latest"

        try:
            print("Checking for updates...")
            response = requests.get(update_url, timeout=10)

            if response.status_code == 404:
                print("No releases found on GitHub!")
                input("Press Enter to continue...")
                return

            if response.status_code != 200:
                print(f"Error: Cannot connect to GitHub (Status: {response.status_code})")
                input("Press Enter to continue...")
                return

            data = response.json()

            if "tag_name" not in data:
                print("Invalid release data!")
                input("Press Enter to continue...")
                return

            latest_version = data["tag_name"]
            release_name = data.get("name", latest_version)
            release_notes = data.get("body", "No release notes")

            assets = data.get("assets", [])
            if not assets:
                print("No downloadable file found in this release!")
                input("Press Enter to continue...")
                return

            download_url = None
            file_name = None
            for asset in assets:
                if asset["name"].endswith(".exe"):
                    download_url = asset["browser_download_url"]
                    file_name = asset["name"]
                    break

            if not download_url:
                print("No .exe file found in this release!")
                input("Press Enter to continue...")
                return

            current_version = self.cf.app_version

            print(f"\nCurrent version: {current_version}")
            print(f"Latest version:  {release_name}")

            if not self.compare_versions(current_version, latest_version):
                print("\nYou are using the latest version!")
                input("Press Enter to continue...")
                return

            print(f"\nNew version available: {latest_version}")
            print(f"\nRelease notes:\n{release_notes}")

            choice = input("\nDownload and install? (y/n): ")

            if choice.lower() != "y":
                print("Update cancelled.")
                input("Press Enter to continue...")
                return

            current_exe = sys.executable
            exe_dir = os.path.dirname(current_exe)
            new_exe_path = os.path.join(exe_dir, "telyzer_update.exe")
            bat_path = os.path.join(exe_dir, "update.bat")
            backup_path = os.path.join(exe_dir, "telyzer_backup.exe")

            print(f"\nDownloading {file_name}...")
            try:
                with requests.get(download_url, stream=True, timeout=30) as r:
                    r.raise_for_status()
                    total = int(r.headers.get("content-length", 0))
                    downloaded = 0
                    last_percent = -1

                    with open(new_exe_path, "wb") as f:
                        for chunk in r.iter_content(chunk_size=8192):
                            if chunk:
                                f.write(chunk)
                                downloaded += len(chunk)
                                if total > 0:
                                    percent = int(downloaded / total * 100)
                                    if percent != last_percent and percent % 5 == 0:
                                        print(f"\rDownloading: {percent}% ({downloaded // 1024} KB / {total // 1024} KB)", end="")
                                        last_percent = percent

                print("\nDownload complete!")

                if os.path.getsize(new_exe_path) < 1024:
                    print("Downloaded file is too small. Download failed.")
                    os.remove(new_exe_path)
                    input("Press Enter to continue...")
                    return

                with open(bat_path, "w") as f:
                    f.write(f"""@echo off
    title Telyzer Updater
    echo Updating Telyzer...

    timeout /t 3 /nobreak > nul

    echo Backing up current version...
    move "{current_exe}" "{backup_path}"

    echo Installing new version...
    move "{new_exe_path}" "{current_exe}"

    echo Starting new version...
    start "" "{current_exe}"

    echo Cleaning up...
    timeout /t 5 /nobreak > nul
    del "{backup_path}"

    del "%~f0"
    """)

                print("\nRestarting to apply update...")
                input("Press Enter to restart...")

                os.startfile(bat_path)
                os._exit(0)

            except requests.exceptions.Timeout:
                print("Download timeout! Please try again.")
                if os.path.exists(new_exe_path):
                    os.remove(new_exe_path)
                input("Press Enter to continue...")

            except requests.exceptions.RequestException as e:
                print(f"Download failed: {e}")
                if os.path.exists(new_exe_path):
                    os.remove(new_exe_path)
                input("Press Enter to continue...")

        except requests.exceptions.Timeout:
            print("Connection timeout! Check your internet.")
            input("Press Enter to continue...")

        except requests.exceptions.ConnectionError:
            print("Cannot connect to GitHub! Check your internet.")
            input("Press Enter to continue...")

        except Exception as e:
            print(f"Error: {e}")
            input("Press Enter to continue...")


    def compare_versions(self, current, latest):
        current_num = int(current.split("vC")[1].split("-")[0])
        latest_num = int(latest.split("vC")[1].split("-")[0])
        return latest_num > current_num

    def channels(self):
        self.cls()
        while True:
            user_choose = input(msg.msg_channels)
            match user_choose:
                case "1":
                    target = input("Enter channel username: ")
                    self.channel_stream(target)

                case "2":
                    selected_file = self.explore_channel_files()
                    if selected_file:
                        self.plot_channel(selected_file)
                    self.cls()

                case "3":
                    selected_file = self.explore_channel_files()
                    if selected_file:
                        self.plot_channel_views(selected_file)
                    self.cls()

                case "4":
                    selected_file = self.explore_channel_files()
                    if selected_file:
                        self.plot_channel_forwards(selected_file)
                    self.cls()

                case "5":
                    selected_file = self.explore_channel_files()
                    if selected_file:
                        self.plot_channel_comments(selected_file)
                    self.cls()

                case "b":
                    break


    def channel_stream(self, target_channel):
        target_channel = target_channel.replace("@", "")
        if target_channel.lstrip("-").isdigit():
            target_channel = int(target_channel)

        dt = self.get_datetime()

        async def _stream():
            if isinstance(target_channel, int):
                entity = None
                async for dialog in self.cf.ta.client.iter_dialogs():
                    if dialog.entity.id == abs(target_channel):
                        entity = dialog.entity
                        break
                if entity is None:
                    print("Channel not found in your dialogs!")
                    return
            else:
                entity = await self.cf.ta.client.get_entity(target_channel)

            if not (hasattr(entity, 'broadcast') or hasattr(entity, 'title')):
                print("This is not a channel!")
                return

            channel_id = entity.id
            channel_folder = f"{self.cf.channel_csv}{channel_id}/"
            os.makedirs(channel_folder, exist_ok=True)

            output_csv = f"{channel_folder}{channel_id}-{dt['file_name']}.csv"

            pattern = f"{channel_folder}{channel_id}-*.csv"
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
                shutil.copy2(old_file_path, output_csv)
                os.remove(old_file_path)
                print(f"Copied previous file to: {os.path.basename(output_csv)}")
                print(f"Removed old file: {os.path.basename(old_file_path)}")

            mode = "a" if append_mode else "w"

            with open(output_csv, mode=mode, encoding="utf-8", newline="") as csvfile:
                fieldnames = [
                    "row_number", "message_id", "publish_timestamp", "publish_datetime",
                    "edit_datetime", "sender_id", "is_outgoing", "message_type",
                    "message_text", "message_edited", "from_schedule", "via_bot_id",
                    "reply_to_msg_id", "reply_to_top_id", "forward_from_id", "forward_from_name",
                    "forward_date", "views", "forwards", "reactions_count", "replies_count",
                    "has_media", "media_type", "grouped_id", "post_author",
                    "post", "pinned", "silent", "mentioned", "noforwards",
                    "out", "sender_username", "sender_first_name", "sender_last_name",
                    "media_caption", "has_reactions", "reactions_detail", "ttl_period",
                    "action_type", "to_id", "from_id", "is_reply", "is_forward",
                    "media_duration", "media_size", "media_mime", "media_name",
                    "document_attributes"
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
                        "edit_datetime": msg.edit_date.isoformat() if msg.edit_date else "",
                        "sender_id": msg.sender_id,
                        "is_outgoing": msg.out,
                        "message_type": self.detect_message_type(msg),
                        "message_text": msg.raw_text,
                        "message_edited": msg.edit_date is not None,
                        "from_schedule": getattr(msg, "from_schedule", False),
                        "via_bot_id": msg.via_bot_id if msg.via_bot_id else "",
                        "reply_to_msg_id": msg.reply_to.reply_to_msg_id if msg.reply_to else "",
                        "reply_to_top_id": msg.reply_to.reply_to_top_id if msg.reply_to and hasattr(msg.reply_to, "reply_to_top_id") else "",
                        "forward_from_id": msg.forward.from_id if msg.forward else "",
                        "forward_from_name": msg.forward.from_name if msg.forward else "",
                        "forward_date": msg.forward.date.isoformat() if msg.forward and msg.forward.date else "",
                        "views": msg.views if hasattr(msg, "views") and msg.views is not None else "",
                        "forwards": msg.forwards if hasattr(msg, "forwards") and msg.forwards is not None else "",
                        "reactions_count": sum(r.count for r in msg.reactions.results) if msg.reactions else 0,
                        "replies_count": msg.replies.replies if msg.replies else 0,
                        "has_media": bool(msg.media),
                        "media_type": type(msg.media).__name__ if msg.media else "",
                        "grouped_id": msg.grouped_id if msg.grouped_id else "",
                        "post_author": msg.post_author if hasattr(msg, "post_author") and msg.post_author else "",
                        "post": msg.post if hasattr(msg, "post") else False,
                        "pinned": msg.pinned if hasattr(msg, "pinned") else False,
                        "silent": msg.silent if hasattr(msg, "silent") else False,
                        "mentioned": msg.mentioned if hasattr(msg, "mentioned") else False,
                        "noforwards": getattr(msg, "noforwards", False),
                        "out": msg.out,
                        "sender_username": "",
                        "sender_first_name": "",
                        "sender_last_name": "",
                        "media_caption": msg.text if msg.media else "",
                        "has_reactions": bool(msg.reactions),
                        "reactions_detail": str([(r.reaction, r.count) for r in msg.reactions.results]) if msg.reactions else "",
                        "ttl_period": getattr(msg, "ttl_period", ""),
                        "action_type": type(msg.action).__name__ if msg.action else "",
                        "to_id": msg.to_id.channel_id if msg.to_id and hasattr(msg.to_id, "channel_id") else "",
                        "from_id": msg.from_id.user_id if msg.from_id and hasattr(msg.from_id, "user_id") else (msg.from_id.channel_id if msg.from_id and hasattr(msg.from_id, "channel_id") else ""),
                        "is_reply": bool(msg.reply_to),
                        "is_forward": bool(msg.forward),
                        "media_duration": getattr(msg.media, "duration", "") if msg.media and hasattr(msg.media, "duration") else "",
                        "media_size": getattr(msg.file, "size", "") if msg.file else "",
                        "media_mime": getattr(msg.file, "mime_type", "") if msg.file else "",
                        "media_name": getattr(msg.file, "name", "") if msg.file else "",
                        "document_attributes": str(msg.document.attributes) if msg.document and hasattr(msg.document, "attributes") else "",
                    }

                    # گرفتن اطلاعات فرستنده
                    if msg.sender_id:
                        try:
                            sender = await msg.get_sender()
                            if sender:
                                message_data["sender_username"] = getattr(sender, "username", "") or ""
                                message_data["sender_first_name"] = getattr(sender, "first_name", "") or ""
                                message_data["sender_last_name"] = getattr(sender, "last_name", "") or ""
                        except:
                            pass

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

            print(f"\nChannel stream saved to: {output_csv}")

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


    def explore_channel_files(self):
        self.cls()

        if not os.path.exists(self.cf.channel_csv):
            print("No channel CSV folder found!")
            input("Press Enter to continue...")
            return None

        channel_folders = [f for f in os.listdir(self.cf.channel_csv) if os.path.isdir(os.path.join(self.cf.channel_csv, f))]

        if not channel_folders:
            print("No channel folders found!")
            input("Press Enter to continue...")
            return None

        folder_info = []
        for folder in channel_folders:
            folder_path = os.path.join(self.cf.channel_csv, folder)
            csv_files = glob.glob(os.path.join(folder_path, "*.csv"))
            if csv_files:
                latest_mtime = max(os.path.getmtime(f) for f in csv_files)
            else:
                latest_mtime = 0
            folder_info.append((folder, len(csv_files), latest_mtime))

        folder_info.sort(key=lambda x: x[2], reverse=True)

        print("Channel folders:")
        for i, (folder, count, mtime) in enumerate(folder_info, 1):
            if mtime > 0:
                mod_date = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M:%S")
            else:
                mod_date = "N/A"
            print(f"{i}. {folder} ({count} CSV files), {mod_date}")

        channel_folders = [info[0] for info in folder_info]

        folder_choice = input("\nSelect folder number (or 'b' to back): ")
        if folder_choice.lower() == "b":
            return None

        try:
            folder_idx = int(folder_choice) - 1
            selected_folder = channel_folders[folder_idx]
        except:
            print("Invalid choice!")
            input("Press Enter to continue...")
            return None

        folder_path = os.path.join(self.cf.channel_csv, selected_folder)
        csv_files = glob.glob(os.path.join(folder_path, "*.csv"))

        if not csv_files:
            print("No CSV files in this folder!")
            input("Press Enter to continue...")
            return None

        csv_files.sort(key=os.path.getmtime, reverse=True)

        print(f"\nCSV files in {selected_folder}:")
        for i, file in enumerate(csv_files, 1):
            file_name = os.path.basename(file)
            file_size = os.path.getsize(file) / 1024
            mod_date = datetime.fromtimestamp(os.path.getmtime(file)).strftime("%Y-%m-%d %H:%M:%S")
            print(f"{i}. {file_name} ({file_size:.1f} KB) - {mod_date}")

        file_choice = input("\nSelect file number (or 'b' to back): ")
        if file_choice.lower() == "b":
            return None

        try:
            file_idx = int(file_choice) - 1
            selected_file = csv_files[file_idx]
        except:
            print("Invalid choice!")
            input("Press Enter to continue...")
            return None

        return selected_file


    def plot_channel(self, csv_path):
        self.cls()
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

        df_sorted = df.sort_values("message_id").reset_index(drop=True)

        deleted_points = []
        for i in range(len(df_sorted) - 1):
            curr_id = int(df_sorted.loc[i, "message_id"])
            next_id = int(df_sorted.loc[i + 1, "message_id"])
            gap = next_id - curr_id - 1

            if gap > 0:
                curr_time = df_sorted.loc[i, "days_from_start"]
                next_time = df_sorted.loc[i + 1, "days_from_start"]
                curr_hour = df_sorted.loc[i, "hour"]
                next_hour = df_sorted.loc[i + 1, "hour"]

                for j in range(1, gap + 1):
                    ratio = j / (gap + 1)
                    fake_time = curr_time + (next_time - curr_time) * ratio
                    fake_hour = curr_hour + (next_hour - curr_hour) * ratio
                    deleted_points.append((fake_time, fake_hour))

        names = csv_name.split("-")
        channel_id = names[0]
        channel_id_val = channel_id
        if str(channel_id).lstrip("-").isdigit():
            channel_id_val = int(channel_id)

        print(f"Channel ID: {channel_id_val}")
        print(f"Total messages: {len(df)}")
        print(f"Estimated deleted messages: {len(deleted_points)}")

        images_folder = f"{self.cf.chat_images}"
        os.makedirs(images_folder, exist_ok=True)

        fig, ax = plt.subplots(figsize=(10, 5))

        scatter = ax.scatter(
            df["days_from_start"],
            df["hour"],
            s=2,
            alpha=0.6,
            color="#1f77b4",
            label=f"Alive ({len(df)})"
        )

        msg_ids = df["message_id"].values
        msg_dates = df["publish_datetime"].values

        cursor = mplcursors.cursor(scatter, multiple=True)

        @cursor.connect("add")
        def on_add(sel):
            idx = sel.index
            msg_id = msg_ids[idx]
            full_date = str(msg_dates[idx])[:19]

            date_part = full_date[:10]
            time_part = full_date[11:19]

            sel.annotation.set_text(
                f"Post ID: {msg_id}\n"
                f"Time: {time_part}\n"
                f"Date: {date_part}\n"
                f"Status: Alive"
            )
            sel.annotation.get_bbox_patch().set(
                facecolor="white",
                edgecolor="black",
                linewidth=1,
                alpha=1.0
            )
            sel.annotation.set_fontsize(9)

        cursor_del = None
        if deleted_points:
            del_x = [p[0] for p in deleted_points]
            del_y = [p[1] for p in deleted_points]
            scatter_del = ax.scatter(
                del_x,
                del_y,
                s=2,
                alpha=0.4,
                color="#ff0e0e",
                label=f"Deleted ({len(deleted_points)})"
            )

        cursor_del = mplcursors.cursor(scatter_del, multiple=True)

        @cursor_del.connect("add")
        def on_add_del(sel):
            idx = sel.index
            del_x_val = del_x[idx]
            del_y_val = del_y[idx]
            
            prev_msg = df_sorted[df_sorted["days_from_start"] <= del_x_val].iloc[-1] if len(df_sorted[df_sorted["days_from_start"] <= del_x_val]) > 0 else None
            next_msg = df_sorted[df_sorted["days_from_start"] >= del_x_val].iloc[0] if len(df_sorted[df_sorted["days_from_start"] >= del_x_val]) > 0 else None
            
            if prev_msg is not None and next_msg is not None:
                prev_time = pd.to_datetime(prev_msg["publish_datetime"])
                next_time = pd.to_datetime(next_msg["publish_datetime"])
                avg_time = prev_time + (next_time - prev_time) / 2
                date_part = avg_time.strftime("%Y-%m-%d")
                time_part = avg_time.strftime("%H:%M:%S")
            else:
                date_part = "Unknown"
                time_part = "Unknown"
            
            if prev_msg is not None and next_msg is not None:
                prev_id = int(prev_msg["message_id"])
                next_id = int(next_msg["message_id"])
                gap = next_id - prev_id - 1
                if gap > 0:
                    ratio = (del_x_val - prev_msg["days_from_start"]) / (next_msg["days_from_start"] - prev_msg["days_from_start"]) if next_msg["days_from_start"] != prev_msg["days_from_start"] else 0
                    est_id = int(prev_id + ratio * (next_id - prev_id))
                else:
                    est_id = prev_id
            else:
                est_id = "Unknown"
            
            sel.annotation.set_text(
                f"Post ID: {est_id}\n"
                f"Time: {time_part}\n"
                f"Date: {date_part}\n"
                f"Status: Deleted"
            )
            sel.annotation.get_bbox_patch().set(
                facecolor="white",
                edgecolor="black",
                linewidth=1,
                alpha=1.0
            )
            sel.annotation.set_fontsize(9)

        from matplotlib.backend_bases import MouseButton

        def on_click(event):
            if event.button == MouseButton.RIGHT:
                for sel in list(cursor.selections):
                    cursor.remove_selection(sel)
                if cursor_del:
                    for sel in list(cursor_del.selections):
                        cursor_del.remove_selection(sel)
                fig.canvas.draw_idle()

        fig.canvas.mpl_connect("button_press_event", on_click)

        ax.set_xlabel("Days elapsed since the first message")
        ax.set_ylabel("Hour of the day")
        ax.set_ylim(0, 25)

        ax.yaxis.set_major_locator(FixedLocator([0, 4, 8, 12, 16, 20, 24]))
        ax.yaxis.set_minor_locator(MultipleLocator(1))

        ax.grid(which='major', axis='y', linestyle='--', alpha=1.0, linewidth=0.8)
        ax.grid(which='minor', axis='y', linestyle='--', alpha=0.4, linewidth=0.5)

        ax.grid(which='major', axis='x', linestyle='--', alpha=1.0, linewidth=0.8)
        ax.xaxis.set_major_locator(plt.MaxNLocator(nbins=10))

        ax.legend(loc='best', fontsize=8)

        today_dt = datetime.now().strftime("%Y%m%d-%H%M%S")

        async def _get_channel_name():
            try:
                entity = await self.cf.ta.client.get_entity(channel_id_val)
                return entity.title, entity.username
            except:
                return "", ""

        channel_name, channel_username = self.loop.run_until_complete(_get_channel_name())

        plt.title("Channel Activity Timeline", fontsize=16, fontweight='bold')

        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if channel_username:
            footer = f"Created by Telyzer at {now_str}  |  @{channel_username}"
        elif channel_name:
            footer = f"Created by Telyzer at {now_str}  |  {channel_name}"
        else:
            footer = f"Created by Telyzer at {now_str}  |  Channel ID: {channel_id_val}"

        plt.figtext(0.5, 0.01, footer, ha='center', fontsize=11, color='gray')

        plt.tight_layout(rect=[0, 0.05, 1, 1])

        output_image = f"{images_folder}channel-{channel_id}-{today_dt}.jpg"
        plt.savefig(output_image, dpi=300)
        plt.show()

        print(f"\nPlot saved to: {output_image}")

    def plot_channel_views(self, csv_path):
        self._plot_channel_metric(csv_path, "views", "Views", "#1f77b4")


    def plot_channel_forwards(self, csv_path):
        self._plot_channel_metric(csv_path, "forwards", "Forwards", "#9467bd")


    def plot_channel_comments(self, csv_path):
        self._plot_channel_metric(csv_path, "replies_count", "Comments", "#2ca02c")


    def _plot_channel_metric(self, csv_path, metric_column, metric_label, line_color):
        self.cls()
        csv_name = os.path.basename(csv_path)
        df = pd.read_csv(csv_path)
        df["publish_datetime"] = pd.to_datetime(df["publish_datetime"])

        iran_tz = pytz.timezone("Asia/Tehran")
        df["publish_datetime"] = df["publish_datetime"].dt.tz_convert(iran_tz)

        df = df.sort_values("message_id").reset_index(drop=True)

        df[metric_column] = pd.to_numeric(df[metric_column], errors="coerce").fillna(0)

        names = csv_name.split("-")
        channel_id = names[0]
        channel_id_val = channel_id
        if str(channel_id).lstrip("-").isdigit():
            channel_id_val = int(channel_id)

        print(f"Channel ID: {channel_id_val}")
        print(f"Total messages: {len(df)}")

        images_folder = f"{self.cf.chat_images}"
        os.makedirs(images_folder, exist_ok=True)

        fig, ax = plt.subplots(figsize=(12, 5))

        x = df["message_id"].values
        y = df[metric_column].values

        line, = ax.plot(x, y, color=line_color, linewidth=1.2)
        ax.fill_between(x, y, alpha=0.15, color=line_color)

        points = ax.scatter(x, y, s=15, color=line_color, alpha=0.01, picker=True)

        ax.set_xlabel("Post ID")
        ax.set_ylabel(metric_label)
        ax.grid(True, linestyle='--', alpha=0.5)

        msg_ids = df["message_id"].values
        msg_dates = df["publish_datetime"].values
        msg_values = df[metric_column].values

        cursor = mplcursors.cursor(points, multiple=True)

        @cursor.connect("add")
        def on_add(sel):
            idx = sel.index
            msg_id = msg_ids[idx]
            full_date = str(msg_dates[idx])[:19]
            value = msg_values[idx]

            date_part = full_date[:10]
            time_part = full_date[11:19]

            sel.annotation.set_text(
                f"Post ID: {msg_id}\n"
                f"{metric_label}: {value}\n"
                f"Time: {time_part}\n"
                f"Date: {date_part}"
            )
            sel.annotation.get_bbox_patch().set(
                facecolor="white",
                edgecolor="black",
                linewidth=1,
                alpha=1.0
            )
            sel.annotation.set_fontsize(9)

        from matplotlib.backend_bases import MouseButton

        def on_click(event):
            if event.button == MouseButton.RIGHT:
                for sel in list(cursor.selections):
                    cursor.remove_selection(sel)
                fig.canvas.draw_idle()

        fig.canvas.mpl_connect("button_press_event", on_click)

        today_dt = datetime.now().strftime("%Y%m%d-%H%M%S")

        async def _get_channel_name():
            try:
                entity = await self.cf.ta.client.get_entity(channel_id_val)
                return entity.title, entity.username
            except:
                return "", ""

        channel_name, channel_username = self.loop.run_until_complete(_get_channel_name())

        plt.title(f"Channel {metric_label} Timeline", fontsize=16, fontweight='bold')

        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if channel_username:
            footer = f"Created by Telyzer at {now_str}  |  @{channel_username}"
        elif channel_name:
            footer = f"Created by Telyzer at {now_str}  |  {channel_name}"
        else:
            footer = f"Created by Telyzer at {now_str}  |  Channel ID: {channel_id_val}"

        plt.figtext(0.5, 0.01, footer, ha='center', fontsize=11, color='gray')

        plt.tight_layout(rect=[0, 0.05, 1, 1])

        output_image = f"{images_folder}channel-{channel_id}-{metric_column}-{today_dt}.jpg"
        plt.savefig(output_image, dpi=300)
        plt.show()

        print(f"\nPlot saved to: {output_image}")