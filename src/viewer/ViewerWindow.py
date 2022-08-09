from PyQt6.QtWidgets import QVBoxLayout
from util.StatusBar import StatusBar
from viewer.MainFrame import MainFrame
from resources import *
from viewer.DbHandler import *
from util.MainWindow import MainWindow

class ViewerWindow(MainWindow):
    def __init__(self,parent=None):
        super().__init__(parent)

        self.setObjectName("ViewerWindow")

        self.setMinimumWidth(512)
        self.mainframe = MainFrame(self,QVBoxLayout())
        self.setCentralWidget(self.mainframe)
        self.titleBar.setText("Hunt Stats Viewer")
        self.setWindowTitle("Hunt Data Viewer")

        self.window().setMinimumHeight(self.mainframe.headerBar.sizeHint().height()//2)
        self.window().setMaximumHeight(self.mainframe.sizeHint().height())
        self.window().setBaseSize(self.mainframe.sizeHint())
        self.statusBar().keep.append(self.mainframe.headerBar)
        StatusBar.setStatus("Hunts are not being logged.", "#ff0000")

    def update(self):
        self.mainframe.update();
        self.adjustSize()

    def toggle(self):
        self.mainframe.toggle()

    def close(self) -> bool:
        self.mainframe.settingsWindow.close()
        return super().close()