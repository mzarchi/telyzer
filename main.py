import threading
import time
import os
import sys

loading_done = False
tc = None


def load_app():
    global loading_done, tc
    from core.controller import TelyzerController
    tc = TelyzerController()
    loading_done = True


def main():
    global loading_done, tc
    os.system('cls' if os.name == 'nt' else 'clear')
    
    load_thread = threading.Thread(target=load_app, daemon=True)
    load_thread.start()
    
    dots = 0
    while not loading_done:
        dots = (dots + 1) % 4
        sys.stdout.write(f"\rPlease wait, loading Telyzer {'.' * dots}   ")
        sys.stdout.flush()
        time.sleep(0.3)
    
    sys.stdout.write("\rPlease wait, loading Telyzer ... Done!   \n")
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

                case "u":
                    tc.check_for_update()

                case "d":
                    tc.developers()

    except Exception as e:
        tc.log(f"Error: {str(e)}")
        pass


if __name__ == "__main__":
    main()