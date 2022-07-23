from PyQt5.QtWidgets import (
    QWidget,
    QGridLayout,
    QVBoxLayout,
    QHBoxLayout
)
from PyQt5.QtCore import QSettings
from HuntHistory import HuntHistory
from Settings import Settings
from Hunter import Hunter
from Connection import Connection


class MainFrame(QWidget):
    def __init__(self, parent) -> None:
        super().__init__(parent)
        self.parent = parent
        self.connection = Connection()
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.settings = QSettings('majikat','HuntStats')
        #self.setMinimumSize(500,500)
        self.huntDir = self.settings.value('huntDir','')

        self.initUI()


    def initUI(self):
        self.hunterTab = Hunter(self,QHBoxLayout(),'Hunter')
        self.layout.addWidget(self.hunterTab)

        self.huntHistoryTab = HuntHistory(self,QGridLayout(),'Hunt History')
        self.layout.addWidget(self.huntHistoryTab)

        self.settingsTab = Settings(self,QGridLayout(),'Settings')
        self.layout.addWidget(self.settingsTab)

    def StartLogger(self):
        self.parent.StartLogger()

    def update(self):
        self.hunterTab.update()
        self.huntHistoryTab.update()

