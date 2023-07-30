from PyQt6.QtWidgets import QGroupBox, QHBoxLayout, QGridLayout, QVBoxLayout, QWidget, QSizePolicy, QPushButton
from PyQt6.QtCore import Qt

from resources import settings
from DbHandler import *
from Widgets.MmrWidget import MmrWidget
from Widgets.KdaWidget import KdaWidget
from Widgets.HunterWidget import HunterWidget

gameTypes = ["All Hunts","Bounty Hunt","Quick Play"]

class Header(QGroupBox):
    def __init__(self,parent=None, layout=QGridLayout()):
        super().__init__(parent)
        self.layout = layout
        self.setLayout(self.layout)
        self.setContentsMargins(0,0,0,0)
        self.layout.setSpacing(0)

        self.setObjectName("Header")

        self.initUI()
        self.update()
        self.setSizePolicy(QSizePolicy.Policy.MinimumExpanding,QSizePolicy.Policy.Fixed)

    def initUI(self):
        self.kda = KdaWidget()
        self.layout.addWidget(self.kda.kdaLabel,0,0,1,1,Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
        self.layout.addWidget(self.kda.values,1,0,Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self.layout.addWidget(self.kda.button,2,0,Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)

        self.hunter = HunterWidget()
        self.layout.addWidget(self.hunter.name,0,1,1,1,Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        self.layout.addWidget(self.hunter.huntsCount,1,1,Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        self.layout.addWidget(self.hunter.level,2,1,Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)

        self.mmr = MmrWidget()
        self.layout.addWidget(self.mmr.starsLabel, 0,2,Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight)
        self.layout.addWidget(self.mmr.mmrLabel, 1,2,Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight)
        self.layout.addWidget(self.mmr.bestLabel, 2,2,Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight)

        self.layout.setColumnStretch(1,1)
        self.layout.setRowStretch(self.layout.rowCount(),1)

    def update(self):
        #print('header.update')
        self.hunter.update()
        self.mmr.update()
        self.kda.update()
