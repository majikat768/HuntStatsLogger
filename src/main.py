import sys
import typing
from resources import *
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFontDatabase
from MainWindow import MainWindow

class App(QApplication):
    def __init__(self, argv: list[str]) -> None:
        super().__init__(argv)


if __name__ == '__main__':
    app = QApplication(sys.argv)

    QFontDatabase.addApplicationFont(resource_path(
        './assets/fonts/LibreBaskerville/LibreBaskerville-Regular.ttf'))
    QFontDatabase.addApplicationFont(resource_path(
        './assets/fonts/Unfair_Style2Rough.ttf'))

    stylesheet = open(resource_path("assets/style.qss")).read()
    app.setStyleSheet(stylesheet)

    window = MainWindow()
    window.show()

    app.exec()