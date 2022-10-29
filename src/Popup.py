from PyQt6.QtWidgets import QMainWindow
from PyQt6.QtCore import Qt

class Popup(QMainWindow):
    def __init__(self, widget,x,y,parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint) 
        self.setObjectName("popup")
        self.setCentralWidget(widget)

        self.setMaximumSize(self.sizeHint())
        self.move(int(x+self.size().width()/4),int(y-self.size().height()/4))

    def keepAlive(self,keep):
        if(keep):
            self.setWindowFlag(Qt.WindowType.Popup)