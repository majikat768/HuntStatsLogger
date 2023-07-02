from PyQt6.QtWidgets import QWidget, QGroupBox, QHBoxLayout, QVBoxLayout, QLabel,QScrollArea
from PyQt6.QtCore import Qt
from resources import *
from Widgets.BountiesWidget import BountiesWidget
from Widgets.RewardsWidget import RewardsWidget
from Widgets.MonstersWidget import MonstersWidget
from Widgets.KillsWidget import KillsWidget
from MainWindow.Hunts.Timeline import Timeline
from DbHandler import *


class HuntDetails(QScrollArea):
    def __init__(self, parent=None):
        if debug:
            print("HuntDetails.__init__")
        super().__init__(parent)
        self.main = QWidget()
        self.main.layout = QVBoxLayout()
        self.main.setLayout(self.main.layout)
        self.setWidgetResizable(True)
        self.setWidget(self.main)
        self.setObjectName("huntDetails")

        self.kills = KillsWidget()
        self.kills.setObjectName("KillsWidget")
        self.bounties = BountiesWidget()
        self.rewards = RewardsWidget()
        self.monsters = MonstersWidget()
        self.main.layout.addWidget(self.kills)
        self.main.layout.setAlignment(self.kills, Qt.AlignmentFlag.AlignTop)
        self.main.layout.addWidget(self.bounties)
        self.main.layout.setAlignment(self.bounties, Qt.AlignmentFlag.AlignTop)
        self.main.layout.addWidget(self.rewards)
        self.main.layout.setAlignment(self.rewards, Qt.AlignmentFlag.AlignTop)
        self.main.layout.addWidget(self.monsters)
        self.main.layout.setAlignment(self.monsters, Qt.AlignmentFlag.AlignTop)

    def update(self, qp, bounties, accolades, monsters_killed, targets,ts,mmrChange):
        if debug:
            print("huntdetails.update")
        self.kills.update(qp,ts,mmrChange)
        self.bounties.update(qp,bounties,targets)
        self.rewards.update(accolades)
        self.monsters.update(monsters_killed)