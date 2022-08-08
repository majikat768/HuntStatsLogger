from PyQt6.QtWidgets import QMainWindow
from PyQt6.QtCore import Qt, QEvent
from PyQt6.QtGui import QFocusEvent

class Popup(QMainWindow):
    def __init__(self, widget,pos,parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint) 
        self.setObjectName("popup")
        print('popup.init')
        self.setCentralWidget(widget)

        self.setMaximumSize(self.sizeHint())
        self.move(pos.x()+self.size().width()/4,pos.y()-self.size().height()/4)

    def keepAlive(self,keep):
        if(keep):
            self.setWindowFlag(Qt.WindowType.Popup)