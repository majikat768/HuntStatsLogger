from PyQt6.QtWidgets import QGroupBox, QHBoxLayout, QVBoxLayout, QLabel, QWidget, QSizePolicy, QPushButton
from PyQt6.QtCore import Qt

from resources import settings
from DbHandler import *
from Widgets.MmrWidget import MmrWidget
from Widgets.KdaWidget import KdaWidget
from Widgets.HunterWidget import HunterWidget

gameTypes = ["All Hunts","Bounty Hunt","Quick Play"]

class Header(QGroupBox):
    def __init__(self,parent=None, layout=QHBoxLayout()):
        super().__init__(parent)
        self.layout = QHBoxLayout()
        self.setLayout(self.layout)

        self.setObjectName("Header")
        self.main = QWidget()
        self.main.layout = layout
        self.main.setLayout(self.main.layout)

        self.initUI()
        self.layout.addWidget(self.main)
        self.setSizePolicy(QSizePolicy.Policy.Minimum,QSizePolicy.Policy.Maximum)
        self.update()

    def initUI(self):
        self.kda = KdaWidget()
        self.main.layout.addWidget(self.kda)
        self.main.layout.addStretch()

        self.hunter = HunterWidget()
        for i in range(self.hunter.layout.count()):
            self.hunter.layout.itemAt(i).setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.main.layout.addWidget(self.hunter)
        self.main.layout.addStretch()

        self.mmr = MmrWidget()
        for i in range(self.mmr.layout.count()):
            self.mmr.layout.itemAt(i).setAlignment(Qt.AlignmentFlag.AlignRight)
        self.main.layout.addWidget(self.mmr)


    def update(self):
        #print('header.update')
        self.hunter.update()
        self.mmr.update()
        self.kda.update()