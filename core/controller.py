import os
import platform


class TelyzerController:
    def __init__(self):
        pass

    def cls(self):
        if platform.system() == "Windows":
            os.system("cls")
        else:
            os.system("clear")
