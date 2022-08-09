from PyQt6.QtWidgets import (
    QMainWindow
)
from PyQt6.QtCore import Qt

from util.StatusBar import StatusBar
from util.TitleBar import TitleBar

class MainWindow(QMainWindow):
    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)

        self.setStatusBar(StatusBar())

        self.titleBar = TitleBar(self)
        self.setMenuBar(self.titleBar)