import messages as msg
from core.controller import TelyzerController

tc = TelyzerController()


def main():
    while True:
        tc.cls()
        input_user_choose = input(msg.msg_main)
        if input_user_choose == "e":
            break
        else:
            match input_user_choose:
                case "1":
                    pass


if __name__ == "__main__":
    main()
