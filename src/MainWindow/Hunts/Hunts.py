from PyQt6.QtWidgets import QWidget,QHBoxLayout,QGridLayout,QVBoxLayout,QGroupBox, QLabel, QSizePolicy, QScrollArea, QTabWidget,QPushButton,QDialog, QComboBox
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon
from DbHandler import *
from MainWindow.Hunts.HuntDetails import HuntDetails
from MainWindow.Hunts.TeamDetails import TeamDetails


BountyNames = {
    'MissionBagBoss_-1': '-1',
    'MissionBagBoss_0': 'Butcher',
    'MissionBagBoss_1': 'Spider',
    'MissionBagBoss_2': 'Assassin',
    'MissionBagBoss_3': 'Scrapbeak',
}

class Hunts(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.SelectHuntBox = QGroupBox()
        self.SelectHuntBox.layout = QHBoxLayout()
        self.SelectHuntBox.setLayout(self.SelectHuntBox.layout)

        self.initDetails()
        self.initHuntSelection()
        self.layout.addWidget(self.HuntSelect)
        self.layout.addWidget(self.details)
        self.refreshButton = QPushButton(" reload ")
        self.refreshButton.clicked.connect(self.update)
        self.refreshButton.setSizePolicy(QSizePolicy.Policy.Fixed,QSizePolicy.Policy.Fixed)
        self.layout.addWidget(self.refreshButton)


    def updateDetails(self):
        ts = self.HuntSelect.currentData()
        hunt = GetHunt(ts)
        entries = GetHuntEntries(ts)
        teams = GetTeams(ts)
        hunters = GetHunters(ts)
        if hunt == {} or entries == {} or teams == {}:
            return
        self.huntDetails.update(hunt,entries)
        self.teamDetails.update(teams,hunters,hunt)

    def update(self):
        #print('hunts.update')
        self.updateHuntSelection()
        self.updateDetails()

    def initHuntSelection(self):
        self.HuntSelect = QComboBox()
        self.HuntSelect.setIconSize(QSize(24,24))
        self.HuntSelect.view().setSpacing(4)
        self.HuntSelect.setStyleSheet('QComboBox{padding:8px;}')

        self.HuntSelect.activated.connect(self.updateDetails)

        self.updateHuntSelection()

    def updateHuntSelection(self):
        self.HuntSelect.clear()
        hunts = GetHunts()
        for hunt in hunts:
            ts = hunt['timestamp']
            dt = unix_to_datetime(ts)
            dead = hunt['MissionBagIsHunterDead']
            gameType = "Quick Play" if hunt['MissionBagIsQuickPlay'].lower() == 'true' else "Bounty Hunt"
            nTeams = hunt['MissionBagNumTeams']
            ln = "%s - %s - %s %s" % (dt, gameType, nTeams, "teams" if gameType == "Bounty Hunt" else "hunters")
            self.HuntSelect.addItem(QIcon(deadIcon if dead else livedIcon),ln,ts)

    def initDetails(self):
        self.details = QWidget()
        self.details.layout = QHBoxLayout()
        self.details.setLayout(self.details.layout)
        self.huntDetails = HuntDetails()
        self.details.layout.addWidget(self.huntDetails)
        self.teamDetails = TeamDetails()
        self.details.layout.addWidget(self.teamDetails)

    def initTeamDetails(self):
        teamDetailsContainer = QTabWidget()

        teamDetails = QWidget()
        teamDetails.layout = QVBoxLayout()
        teamDetails.setLayout(teamDetails.layout)


        teamDetails.layout.addWidget(QLabel("Team Details"))
        teamDetails.layout.addStretch()

        teamDetailsContainer.setSizePolicy(QSizePolicy.Policy.Expanding,QSizePolicy.Policy.Expanding)
        teamDetailsContainer.addTab(teamDetails, "Team N")
        teamDetailsContainer.addTab(teamDetails, "Team M")
        teamDetailsContainer.setSizePolicy(QSizePolicy.Policy.Expanding,QSizePolicy.Policy.Expanding)
        self.teamDetails = teamDetailsContainer

