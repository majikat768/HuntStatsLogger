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


class MainFrame(QWidget):
    def __init__(self, parent) -> None:
        super().__init__(parent)
        self.parent = parent
        self.connection = Connection()
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.settings = QSettings('majikat','HuntStats')
        self.huntDir = self.settings.value('huntDir','')

        self.initUI()

        self.setSizePolicy(QSizePolicy.MinimumExpanding,QSizePolicy.MinimumExpanding)
        self.mouseXY = QPoint()

    def initUI(self):
        self.hunterTab = Hunter(self,QHBoxLayout(),'Hunter')
        self.layout.addWidget(self.hunterTab)

        self.huntHistoryTab = HuntHistory(self,QGridLayout(),'Hunt History')
        self.layout.addWidget(self.huntHistoryTab)

        self.settingsButton = QPushButton('Settings')
        self.settingsButton.clicked.connect(self.OpenSettings)
        #self.settingsTab = Settings(self,QGridLayout(),'Settings')
        #self.layout.addWidget(self.settingsTab)
        self.layout.addWidget(self.settingsButton)
        self.settingsWindow = Settings(self,QGridLayout(),'Settings')

    def StartLogger(self):
        self.parent.StartLogger()

    def OpenSettings(self):
        window = QMainWindow()
        window.setCentralWidget(self.settingsWindow)
        window.setMenuBar(TitleBar(window))
        window.menuBar().setFixedHeight(48)
        window.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Expanding)
        window.setWindowFlags(Qt.FramelessWindowHint)
        window.setFixedSize(window.sizeHint())
        window.show()

    def update(self):
        print('mainframe: updating')
        self.hunterTab.update()
        self.huntHistoryTab.update()