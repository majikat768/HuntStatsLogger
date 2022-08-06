from PyQt6.QtWidgets import QMainWindow,QVBoxLayout
from PyQt6.QtCore import Qt
from util.TitleBar import TitleBar
from viewer.MainFrame import MainFrame
from resources import *
from viewer.DbHandler import *
from util.StatusBar import StatusBar

class ViewerWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setStatusBar(StatusBar())
        self.setObjectName("ViewerWindow")
        self.setWindowFlags(Qt.WindowType.CustomizeWindowHint | Qt.WindowType.FramelessWindowHint)

        self.setMinimumWidth(512)
        self.mainframe = MainFrame(self,QVBoxLayout())
        self.setCentralWidget(self.mainframe)
        self.titleBar = TitleBar(self)
        self.setMenuBar(self.titleBar)
        self.titleBar.setText("Hunt Stats Viewer")
        self.setWindowTitle("Hunt Data Viewer")

        #self.statusBar().setEnabled(True)
        #self.statusBar().setSizeGripEnabled(True)
        #self.statusBar().setStyleSheet("QSizeGrip{image: url(\"%s\")};" % resource_path("assets/icons/sizegrip.png").replace("\\","/"))


        self.show()

    def update(self):
        self.mainframe.update();
        self.adjustSize()

    def setStatus(self,text):
        self.statusBar().showMessage(text)

    def toggle(self):
        self.mainframe.toggle()
