from PyQt5.QtWidgets import (
    QWidget,
    QGridLayout,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QMainWindow,
    QSizePolicy
)
from PyQt5.QtCore import QSettings, QPoint, Qt
from PyQt5 import QtGui
from HuntHistory import HuntHistory
from Settings import Settings
from Hunter import Hunter
from Connection import Connection
from TitleBar import TitleBar

killall = False

class MainFrame(QWidget):
    def __init__(self, parent) -> None:
        super().__init__(parent)
        self.parent = parent
        self.connection = Connection()
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.settings = QSettings('./settings.ini',QSettings.Format.IniFormat)
        self.huntDir = self.settings.value('huntDir','')

        self.initUI()

        self.setSizePolicy(QSizePolicy.MinimumExpanding,QSizePolicy.MinimumExpanding)
        self.mouseXY = QPoint()

    def initUI(self):
        self.settingsBox = Settings(self,QVBoxLayout())
        self.settingsWindow = QMainWindow()
        self.settingsWindow.setWindowFlags(Qt.FramelessWindowHint)
        self.settingsWindow.setCentralWidget(self.settingsBox)
        self.settingsWindow.setMenuBar(TitleBar(self.settingsWindow))
        self.settingsWindow.menuBar().setFixedHeight(48)
        self.settingsWindow.setFixedSize(self.settingsWindow.sizeHint())
        self.hunterTab = Hunter(self,QHBoxLayout(),'Hunter')
        self.layout.addWidget(self.hunterTab)

        self.huntHistoryTab = HuntHistory(self,QGridLayout(),'Hunt History')
        self.layout.addWidget(self.huntHistoryTab)

        self.settingsButton = QPushButton('Settings')
        self.settingsButton.clicked.connect(self.settingsWindow.show)
        #self.settingsTab = Settings(self,QGridLayout(),'Settings')
        #self.layout.addWidget(self.settingsTab)
        self.layout.addWidget(self.settingsButton)

    def StartLogger(self):
        self.parent.StartLogger()

    def update(self):
        print('mainframe: updating')
        self.hunterTab.update()
        self.huntHistoryTab.update()