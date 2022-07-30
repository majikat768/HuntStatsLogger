import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFontDatabase
from PyQt6.QtCore import QSettings
import Logger, App, Connection

def killall():
    Logger.killall = True
    Connection.killall = True

def resource_path(relative_path):
    try:
    # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

if __name__ == '__main__':
    app = QApplication(sys.argv)

    QFontDatabase.addApplicationFont(resource_path('assets/fonts/LibreBaskerville/LibreBaskerville-Regular.ttf'))
    stylesheet = open(resource_path('./assets/MaterialDark.qss'),'r').read()

    app.setStyleSheet(stylesheet)
    app.aboutToQuit.connect(killall)

    if len(sys.argv) > 1:
        if sys.argv[1] == '-nogui':
            logger = Logger.Logger()
            logger.run()
        elif sys.argv[1] == '-nolog':
            ex2 = App.App(log=False)

            app.exec()

    else:

        ex2 = App.App()
        app.exec()

        Logger.killall = True
        Connection.killall = True