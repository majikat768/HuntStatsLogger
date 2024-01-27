from PyQt6.QtGui import QEnterEvent
from PyQt6.QtWidgets import QLabel, QWidget, QVBoxLayout, QMainWindow
from PyQt6.QtCore import Qt

class Tooltip(QMainWindow):
    def __init__(self, text,parent: QWidget | None = None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.SubWindow)
        self.main = QWidget()
        self.main.layout = QVBoxLayout()
        self.main.setLayout(self.main.layout)
        #self.main.layout.addWidget(QLabel(text))
        self.setCentralWidget(QLabel(text))

    def show(self,point) -> None:
        self.setGeometry(
            point.x(),
            point.y(),
            self.sizeHint().width(),
            self.sizeHint().height()
        )
        return super().show()

    def enterEvent(self, event: QEnterEvent) -> None:
        self.hide()
        return super().enterEvent(event)