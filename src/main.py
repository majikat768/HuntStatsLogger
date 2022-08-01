import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFontDatabase,QIcon
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

class nonApp():
    def __init__(self):
        self.app_data_path = os.path.join(os.getcwd(),'hsl_files')
        self.settings = QSettings(
            os.path.join(self.app_data_path,'settings.ini'),
            QSettings.Format.IniFormat
        )

if __name__ == '__main__':
    app = QApplication(sys.argv)

    QFontDatabase.addApplicationFont(resource_path('assets/fonts/LibreBaskerville/LibreBaskerville-Regular.ttf'))
    stylesheet = open(resource_path('./assets/MaterialDark.qss'),'r').read()

    app.setStyleSheet(stylesheet)
    app.aboutToQuit.connect(killall)

    if len(sys.argv) > 1:
        if sys.argv[1] == '-nogui':
            logger = Logger.Logger(nonApp())
            logger.run()
        elif sys.argv[1] == '-nolog':
            ex2 = App.App(log=False)

            app.exec()

    else:

        ex2 = App.App()
        ex2.setWindowIcon(QIcon(App.resource_path('assets/icons/death2.png')))
        app.exec()

        Logger.killall = True
        Connection.killall = True