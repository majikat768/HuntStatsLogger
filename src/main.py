import sys
import ctypes
import platform
from resources import *

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFontDatabase
from PyQt6.QtCore import Qt, QCoreApplication

from MainWindow.MainWindow import MainWindow

if __name__ == '__main__':
    if int(platform.release()) >= 8:
        ctypes.windll.shcore.SetProcessDpiAwareness(True)
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    app = QApplication(sys.argv)
    QFontDatabase.addApplicationFont(resource_path('./assets/fonts/LibreBaskerville/LibreBaskerville-Regular.ttf'))
    QFontDatabase.addApplicationFont(resource_path('./assets/fonts/Ubuntu/Ubuntu-R.ttf'))

    stylesheet = open(resource_path('./assets/MaterialDark.qss'),'r').read()
    app.setStyleSheet(stylesheet)

    window = MainWindow()
    window.show()

    app.exec()