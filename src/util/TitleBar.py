from PyQt6.QtWidgets import QHBoxLayout, QPushButton,QMenuBar,QSizePolicy,QLabel
from PyQt6.QtCore import Qt
from PyQt6 import QtGui


class TitleBar(QMenuBar):
    def __init__(self, parent) -> None:
        super().__init__(parent)
        self.layout = QHBoxLayout()
        self.setLayout(self.layout)
        self.setSizePolicy(QSizePolicy.Policy.Fixed,QSizePolicy.Policy.Fixed)
        self.setObjectName('TitleBar')

        self.setFixedHeight(48)
        self.title = QLabel("Hunt Stats Logger")
        self.title.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.ExitButton = QPushButton('X',parent)
        self.ExitButton.clicked.connect(killThreads)
        self.ExitButton.clicked.connect(parent.close)
        self.ExitButton.setObjectName('Exit')
        self.ExitButton.setFixedSize(32,24)
        self.layout.addWidget(self.title)
        self.layout.addStretch()
        self.layout.addWidget(self.ExitButton,Qt.AlignmentFlag.AlignRight)
        self.mouseHold = False

    def setText(self,text):
        self.title.setText(text)

    def mousePressEvent(self, event: QtGui.QMouseEvent) -> None:
        super().mousePressEvent(event)
        self.start = event.pos()
        self.mouseHold = True

    def mouseReleaseEvent(self, event: QtGui.QMouseEvent) -> None:
        super().mouseReleaseEvent(event)
        self.mouseHold = False

    def mouseMoveEvent(self, event: QtGui.QMouseEvent) -> None:
        super().mouseMoveEvent(event)
        if self.mouseHold:
            try:
                diff = event.globalPosition().toPoint() - self.start
                self.parent().move(diff)
            except Exception as msg:
                print(event.globalPosition())
                print(msg)
                self.window().setGeometry(60,60,self.window().size().width(),self.window().size().height())
                self.mouseHold = False

def killThreads():
    #DbHandler.running = False
    #Logger.running = False
    pass