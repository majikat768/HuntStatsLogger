from PyQt6.QtWidgets import QWidget,QHBoxLayout,QGridLayout,QVBoxLayout,QGroupBox, QLabel, QSizePolicy, QScrollArea, QTabWidget,QPushButton,QDialog, QComboBox, QStackedWidget, QListWidget
from PyQt6.QtCore import Qt, QSize, QEvent
from PyQt6.QtGui import QIcon
from DbHandler import *
from MainWindow.Hunts.HuntDetails import HuntDetails
from MainWindow.Hunts.TeamDetails import TeamDetails
from Popup import Popup


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
        self.layout.addWidget(self.huntDetails)
        self.layout.addWidget(self.teamDetails)
        self.refreshButton = QPushButton(" reload ")
        self.refreshButton.clicked.connect(self.update)
        self.refreshButton.setSizePolicy(QSizePolicy.Policy.Fixed,QSizePolicy.Policy.Fixed)
        #self.layout.addWidget(self.refreshButton,1,self.layout.columnCount()-1,1,1)
        #self.layout.setRowStretch(self.layout.rowCount()-1,1)


    def updateDetails(self):
        ts = self.HuntSelect.currentData()
        if(ts == None):
            return
        hunt = GetHunt(ts)
        entries = GetHuntEntries(ts)
        accolades = GetHuntAccolades(ts)
        teams = GetTeams(ts)
        hunters = GetHunters(ts)
        if hunt == {} or entries == {} or teams == {}:
            return
        qp = hunt['MissionBagIsQuickPlay'].lower() == 'true'
        monsters_killed = {}
        team_kills = {i+1 : 0 for i in range(6)}
        your_kills = {i+1 : 0 for i in range(6)}
        your_deaths = {i+1 : 0 for i in range(6)}
        assists = 0

        your_total_kills = execute_query("select downedbyme+killedbyme,mmr from 'hunters' where timestamp is %d and (downedbyme > 0 or killedbyme > 0)" % hunt['timestamp'])
        your_total_deaths = execute_query("select downedme+killedme,mmr from 'hunters' where timestamp is %d and (downedme > 0 or killedme > 0)" % hunt['timestamp'])
        for k in your_total_kills:
            mmr = mmr_to_stars(k[1])
            your_kills[mmr] += k[0]
        for d in your_total_deaths:
            mmr = mmr_to_stars(d[1])
            your_deaths[mmr] += d[0]
        if qp:
            bounties = {'rifts_closed':0}
        else:
            bounties = {
                'assassin': {
                    "clues": 0,
                    "killed": 0,
                    "banished": 0
                },
                'spider': {
                    "clues": 0,
                    "killed": 0,
                    "banished": 0
                },
                'butcher': {
                    "clues": 0,
                    "killed": 0,
                    "banished": 0
                },
                'scrapbeak': {
                    "clues": 0,
                    "killed": 0,
                    "banished": 0
                },
            }
        
        for accolade in accolades:
            cat = accolade['category']
            if "killed_" in cat:
                boss = cat.split("_")[2]
                if boss in bounties:
                    bounties[boss]["killed"] = 1
            if "banished" in cat:
                boss = cat.split("_")[2]
                if boss in bounties:
                    bounties[boss]["banished"] = 1
        for entry in entries:
            cat = entry['category']
            if 'wellsprings_found' in cat:
                bounties['rifts_closed'] += 1
            if 'clues_found' in cat:
                boss = entry['descriptorName'].split(' ')[1]
                bounties[boss]['clues'] += 1
            if 'monsters_killed' in cat:
                monster = entry['descriptorName'].split(' ')[1]
                if monster not in monsters_killed.keys():
                    monsters_killed[monster] = 0
                monsters_killed[monster] += entry['amount']
            if 'players_killed' in cat:
                if 'assist' in cat:
                    assists += entry['amount']
                elif 'mm rating' in entry['descriptorName']:
                    stars = int(entry['descriptorName'].split(' ')[4])
                    team_kills[stars] += entry['amount']

        killData = {
            "your_kills": your_kills,
            "team_kills": team_kills,
            "your_deaths": your_deaths,
            "assists": assists,
        }
        rewards = calculateRewards(accolades,entries)
        targets = GetBounties(hunt)
        self.huntDetails.update(qp,bounties,rewards,monsters_killed, targets)
        self.teamDetails.update(teams,hunters,hunt,killData)

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
            dead = hunt['MissionBagIsHunterDead'] == 'true'
            gameType = "Quick Play" if hunt['MissionBagIsQuickPlay'].lower() == 'true' else "Bounty Hunt"
            nTeams = hunt['MissionBagNumTeams']
            ln = "%s - %s - %s %s" % (dt, gameType, nTeams, "teams" if gameType == "Bounty Hunt" else "hunters")
            self.HuntSelect.addItem(QIcon(deadIcon if dead else livedIcon),ln,ts)

    def initDetails(self):
        self.huntDetails = HuntDetails()
        self.huntDetails.setSizePolicy(QSizePolicy.Policy.MinimumExpanding,QSizePolicy.Policy.Fixed)
        self.teamDetails = TeamDetails()

def calculateRewards(accolades, entries):
    bounty = 0
    gold = 0
    bb = 0
    xp = 0
    eventPoints = 0

    for acc in accolades:
        bounty += acc['bounty']
        xp += acc['xp']
        bb += acc['generatedGems']
        eventPoints += acc['eventPoints']

    xp += 4*bounty
    gold += bounty
    return {
        'Hunt Dollars':gold,
        'Blood Bonds':bb,
        'XP':xp,
        'Event Points':eventPoints
    }