from PyQt5.QtWidgets import (
    QWidget,
    QGridLayout,
    QVBoxLayout,
)
from PyQt5.QtCore import QSettings
from HuntHistory import HuntHistory
from Settings import Settings
from Hunter import Hunter
from Connection import Connection


class MainFrame(QWidget):
    def __init__(self, parent) -> None:
        super().__init__(parent)
        self.connection = Connection()
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.settings = QSettings('majikat','HuntStats')
        #self.setMinimumSize(500,500)
        self.huntDir = self.settings.value('huntDir','')

        self.initUI()


    def initUI(self):
        self.hunterTab = Hunter(self,QGridLayout(),'Hunter')
        self.layout.addWidget(self.hunterTab)
        #self.addTab(self.hunterTab,'Hunter Stats')
        #self.initLastHunt()
        self.huntHistoryTab = HuntHistory(self,QGridLayout(),'Hunt History')
        self.layout.addWidget(self.huntHistoryTab)
        #self.addTab(self.huntHistoryTab,'Hunt History')
        self.settingsTab = Settings(self,QGridLayout(),'Settings')
        self.layout.addWidget(self.settingsTab)
        #self.addTab(self.settingsTab,'Settings')

    def UpdateHunterTab(self):
        self.hunterTab.UpdateHunterBox()
    
    def UpdateLastMatchTab(self):
        self.huntHistory.update()
        pass

