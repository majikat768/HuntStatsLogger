import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFontDatabase,QIcon
from PyQt6.QtCore import QSettings
import Logger, App, Connection
from resources import *

def killall():
    Logger.killall = True
    Connection.killall = True


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

    ex2 = App.App()
    ex2.setWindowIcon(QIcon(App.resource_path('assets/icons/death2.png')))
    app.exec()

    Logger.killall = True
    Connection.killall = True