from PyQt6.QtWidgets import QVBoxLayout
from PyQt6.QtCore import Qt
from settings.MainFrame import MainFrame
from resources import *
from util.MainWindow import MainWindow

class SettingsWindow(MainWindow):
    def __init__(self,parent=None):
        super().__init__(parent)

        self.setObjectName("LoggerWindow")
        self.mainframe = MainFrame(self,QVBoxLayout())
        self.setCentralWidget(self.mainframe)
        self.titleBar.setText("Settings")
        self.setWindowTitle("Hunt Data Logger")

        self.adjustSize()

        self.statusBar().setSizeGripEnabled(False)

    def update(self):
        self.mainframe.update();
        self.adjustSize()