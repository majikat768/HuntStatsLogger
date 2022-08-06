from PyQt6.QtWidgets import (
    QPushButton,
    QMainWindow,
    QVBoxLayout,
    QToolBar
)
from PyQt6.QtGui import QAction
from PyQt6.QtCore import Qt
from util.StatusBar import StatusBar
from settings.MainFrame import MainFrame
from resources import *
from util.TitleBar import TitleBar

class SettingsWindow(QMainWindow):
    def __init__(self,viewerWindow):
        super().__init__()

        self.setStatusBar(StatusBar())
        self.viewerWindow = viewerWindow
        self.setObjectName("LoggerWindow")
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.mainframe = MainFrame(self,QVBoxLayout())
        self.setCentralWidget(self.mainframe)
        self.titleBar = TitleBar(self)
        self.titleBar.setText("Settings")
        self.setMenuBar(self.titleBar)
        self.setWindowTitle("Hunt Data Logger")

        self.setMinimumSize(self.sizeHint().width(),10)
        self.show()

        print('parent',self.parent())

        self.statusBar().setSizeGripEnabled(False)

    def update(self):
        self.mainframe.update();
        self.adjustSize()

    def setStatus(self,text):
        self.viewerWindow.setStatus(text)
        self.statusBar().showMessage(text)
        pass

    def initToolBar(self):
        toolbar = QToolBar(self)
        toolbar.setMovable(False)

        InfoAction = QAction("Information",self)
        toolbar.addAction(InfoAction)

        self.addToolBar(toolbar)
