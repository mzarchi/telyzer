from core.controller import TelyzerController
import messages as msg


def main():
    tc = TelyzerController()

    while True:
        tc.cls()
        menu = msg.msg_main
        if tc.cf.ta and tc.cf.ta.client:
            is_active = tc.is_session_active()
            if is_active:
                me = tc.get_me()
                if me:
                    username = me.username or me.first_name
                    menu = msg.msg_main.replace("1. Telegram Login", f"1. Session of @{username} is active - Logout")

        input_user_choose = input(menu)
        if input_user_choose == "e":
            tc.disconnect()
            break

        match input_user_choose:
            case "1":
                if tc.is_session_active():
                    tc.logout()
                else:
                    tc.connect()

            case "2":
                tc.contacts()


if __name__ == "__main__":
    main()
