from PyQt6.QtWidgets import QMainWindow, QStatusBar
from MapWindow.MainFrame import MainFrame

class MapWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("MapWindow")
        self.setWindowTitle("Hunt Showdown Maps")

        self.main = MainFrame(self)

        self.setCentralWidget(self.main)
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)

    def wheelEvent(self, a0) -> None:
        return 