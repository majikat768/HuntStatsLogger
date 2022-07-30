from PyQt6.QtWidgets import QHBoxLayout, QPushButton,QMenuBar,QSizePolicy
from PyQt6.QtCore import Qt
from PyQt6 import QtGui
import Logger,Connection

class TitleBar(QMenuBar):
    def __init__(self, parent) -> None:
        super().__init__(parent)
        self.parent = parent
        self.layout = QHBoxLayout()
        self.setLayout(self.layout)
        self.layout.setAlignment(Qt.AlignRight)
        self.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed)
        self.setFixedHeight(256)
        print(self.size())
        self.setObjectName('TitleBar')

        self.setFixedHeight(33)
        self.ExitButton = QPushButton('X',parent)
        #self.ExitButton.clicked.connect(self.killall)
        self.ExitButton.clicked.connect(parent.close)
        self.ExitButton.setObjectName('Exit')
        self.ExitButton.setFixedSize(32,32)
        self.layout.addStretch(0)
        self.layout.addWidget(self.ExitButton)
        self.mouseHold = False

    def killall(self):
        Logger.killall = True
        Connection.killall = True

    def mousePressEvent(self, event: QtGui.QMouseEvent) -> None:
        print(self.size())
        super().mousePressEvent(event)
        self.start = event.pos()
        self.mouseHold = True

    def mouseReleaseEvent(self, event: QtGui.QMouseEvent) -> None:
        super().mouseReleaseEvent(event)
        self.mouseHold = False

    def mouseMoveEvent(self, event: QtGui.QMouseEvent) -> None:
        super().mouseMoveEvent(event)
        if self.mouseHold:
            diff = event.pos() - self.start
            self.parent.move(self.parent.pos() + diff)