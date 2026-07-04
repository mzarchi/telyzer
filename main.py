import sys
from PySide6.QtWidgets import QApplication
from app.ui.login import LoginWindow, STYLESHEET

def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(STYLESHEET)
    
    win = LoginWindow()
    
    screen = app.primaryScreen().geometry()
    x = (screen.width() - win.width()) // 2
    y = (screen.height() - win.height()) // 2
    win.move(x, y)
    
    win.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()

'''
pyinstaller --onefile --icon=icon/cisco-app.ico --name=Telyzer_vC36-2607 main.py
pyinstaller --onefile --name=Telyzer_vC38-2607 --noconsole --add-data "config.ini;." main.py
git rev-list --count HEAD
'''