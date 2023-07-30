from PyQt6.QtWidgets import QWidget, QGroupBox, QHBoxLayout, QVBoxLayout,QScrollArea
from PyQt6.QtCore import Qt
from resources import *
from Widgets.BountiesWidget import BountiesWidget
from Widgets.RewardsWidget import RewardsWidget
from Widgets.MonstersWidget import MonstersWidget
from Widgets.KillsWidget import KillsWidget
from Widgets.ScrollWidget import ScrollWidget
from MainWindow.Hunts.Timeline import Timeline
from DbHandler import *


class HuntDetails(ScrollWidget):
    def __init__(self, parent=None):
        if debug:
            print("HuntDetails.__init__")
        super().__init__(parent)
        self.setObjectName("HuntDetails")

        self.kills = KillsWidget()
        self.kills.setObjectName("KillsWidget")
        self.bounties = BountiesWidget()
        self.rewards = RewardsWidget()
        self.monsters = MonstersWidget()
        self.kills = KillsWidget()
        self.layout.addWidget(self.kills)
        self.layout.addWidget(self.bounties)
        self.layout.addWidget(self.rewards)
        self.layout.addWidget(self.monsters)
        self.addWidget(self.kills)
        self.addWidget(self.bounties)
        self.addWidget(self.rewards)
        self.addWidget(self.monsters)

        self.main.layout.addStretch()
        self.main.layout.setContentsMargins(0,0,0,0)
        self.main.setContentsMargins(0,0,0,0)

    def update(self, qp, bounties, accolades, monsters_killed, targets,ts,mmrChange):
        if debug:
            print("huntdetails.update")
        self.kills.update(qp,ts,mmrChange)
        self.bounties.update(qp,bounties,targets)
        self.rewards.update(accolades)
        self.monsters.update(monsters_killed)