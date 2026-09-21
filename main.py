import logging
import time
import os
import sys
import threading

logging.getLogger('telethon').setLevel(logging.ERROR)


def _spinner(stop_event):
    dots_states = ["", ".", "..", "..."]
    i = 0
    while not stop_event.is_set():
        sys.stdout.write(f"\rPlease wait, loading Telyzer{dots_states[i % len(dots_states)]}")
        sys.stdout.flush()
        time.sleep(0.4)
        i += 1


def main():
    os.system('cls' if os.name == 'nt' else 'clear')

    stop_event = threading.Event()
    spinner_thread = threading.Thread(target=_spinner, args=(stop_event,), daemon=True)
    spinner_thread.start()

    from core.controller import TelyzerController
    tc = TelyzerController()

    stop_event.set()
    spinner_thread.join()

    sys.stdout.write("\rPlease wait, loading Telyzer ... Done!\n")
    sys.stdout.flush()
    time.sleep(0.3)

    os.system('cls' if os.name == 'nt' else 'clear')

    import messages as msg

    try:
        while True:
            tc.cls()
            menu = msg.msg_main.replace("{version}", tc.cf.app_version)
            if tc.cf.ta and tc.cf.ta.client:
                is_active = tc.is_session_active()
                if is_active:
                    me = tc.get_me()
                    if me:
                        username = me.username or me.first_name
                        menu = msg.msg_main.replace("{version}", tc.cf.app_version)
                        menu = menu.replace("1. Telegram Login", f"1. Session of @{username} is active - Logout")

            input_user_choose = input(menu)
            if input_user_choose == "e":
                tc.disconnect()
                sys.exit(0)

            match input_user_choose:
                case "1":
                    if tc.is_session_active():
                        tc.logout()
                    else:
                        tc.connect()

                case "2":
                    tc.contacts()

                case "3":
                    tc.groups()

                case "4":
                    tc.channels()

                case "u":
                    tc.check_for_update()

                case "d":
                    tc.developers()

    except Exception as e:
        tc.log(f"Error: {str(e)}")
        pass


if __name__ == "__main__":
    main()