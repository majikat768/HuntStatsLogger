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

    def show(self) -> None:
        p_pos = self.parent().window().pos()
        self.move(p_pos.x()+32,p_pos.y()+32)

        return super().show()

    def wheelEvent(self, a0) -> None:
        return 