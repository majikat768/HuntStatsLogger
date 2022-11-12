import sys
import ctypes
import platform
from resources import *

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFontDatabase, QIcon
from PyQt6.QtCore import Qt
from resources import *

from MainWindow.MainWindow import MainWindow


if __name__ == '__main__':
    if platform.system() == "Windows" and int(platform.release()) >= 8:
        ctypes.windll.shcore.SetProcessDpiAwareness(True)
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)

    app = QApplication(sys.argv)
    stylesheet = open(resource_path('./assets/MaterialDark.qss'), 'r').read()
    app.setStyleSheet(stylesheet)

    QFontDatabase.addApplicationFont(resource_path(
        './assets/fonts/LibreBaskerville/LibreBaskerville-Regular.ttf'))
    QFontDatabase.addApplicationFont(
        resource_path('./assets/fonts/Ubuntu/Ubuntu-R.ttf'))

    window = MainWindow()
    window.setBaseSize(1024, 768)
    window.show()

    app.setWindowIcon(QIcon(resource_path('assets/icons/app.png')))
    if settings.value("xml_path", "") == "":
        window.mainframe.settingsWindow.show()

    app.exec()
