from PyQt6.QtWidgets import QWidget, QGroupBox, QHBoxLayout, QVBoxLayout, QLabel,QScrollArea
from PyQt6.QtCore import Qt
from resources import *
from Widgets.BountiesWidget import BountiesWidget
from Widgets.RewardsWidget import RewardsWidget
from Widgets.MonstersWidget import MonstersWidget
from Widgets.KillsWidget import KillsWidget
from MainWindow.Hunts.Timeline import Timeline
from DbHandler import *


class HuntDetails(QGroupBox):
    def __init__(self, title=None):
        if debug:
            print("HuntDetails.__init__")
        super().__init__(title)
        self.setObjectName("huntDetails")
        self.layout = QHBoxLayout()
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.setLayout(self.layout)

        self.bounties = BountiesWidget()
        self.rewards = RewardsWidget()
        self.monsters = MonstersWidget()
        self.layout.addWidget(self.bounties)
        self.layout.setAlignment(self.bounties, Qt.AlignmentFlag.AlignTop)
        self.layout.addStretch()
        self.layout.addWidget(self.rewards)
        self.layout.setAlignment(self.rewards, Qt.AlignmentFlag.AlignTop)
        self.layout.addStretch()
        self.layout.addWidget(self.monsters)
        self.layout.setAlignment(self.monsters, Qt.AlignmentFlag.AlignTop)


    def update(self, qp, bounties, accolades, monsters_killed, targets,ts,mmrChange):
        if debug:
            print("huntdetails.update")
        self.bounties.update(qp,bounties,targets)
        self.rewards.update(accolades)
        self.monsters.update(monsters_killed)