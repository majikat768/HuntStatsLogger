from PyQt6.QtWidgets import QWidget, QVBoxLayout, QScrollArea, QComboBox
from PyQt6.QtCore import QSize
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


class Hunts(QScrollArea):
    def __init__(self, parent):
        super().__init__(parent)
        self.setWidgetResizable(True)
        self.initUI()

    def initUI(self):
        #self.main = QSplitter(Qt.Orientation.Vertical)
        self.main = QWidget()
        self.main.layout = QVBoxLayout()
        self.main.setLayout(self.main.layout)

        self.initDetails()
        self.initHuntSelection()
        self.main.layout.addWidget(self.HuntSelect)
        self.main.layout.addWidget(self.huntDetails)
        self.main.layout.addWidget(self.teamDetails)
        self.setWidget(self.main)
        #self.main.setCollapsible(0,False)

    def calculateMmrChange(self):
        '''
        trying to reverse engineer how MMR is calculated, so that I can make an estimate.
        '''
        currentIndex = self.HuntSelect.currentIndex()
        if currentIndex < 0:
            return
        currentTs = self.HuntSelect.currentData()
        currentMmr = execute_query("select mmr from 'hunters' where profileid is '%s' and timestamp is %d" % (
            settings.value("profileid"), currentTs))
        currentMmr = 0 if len(currentMmr) == 0 else currentMmr[0][0]
        if currentIndex == 0:
            predictedMmr = predictNextMmr(currentMmr, currentTs)
            mmrOutput = 'predicted MMR change:<br>%d -> %d<br>%+d' % (currentMmr, predictedMmr, predictedMmr-currentMmr)
            return mmrOutput
        else:
            predictedMmr = predictNextMmr(currentMmr, currentTs)
            self.HuntSelect.setCurrentIndex(currentIndex-1)
            nextTs = self.HuntSelect.currentData()
            self.HuntSelect.setCurrentIndex(currentIndex)

            nextMmr = execute_query("select mmr from 'hunters' where profileid is '%s' and timestamp is %d" % (
                settings.value("profileid"), nextTs))
            nextMmr = 0 if len(nextMmr) == 0 else nextMmr[0][0]
            predictChange = predictedMmr - currentMmr
            mmrChange = nextMmr - currentMmr
            mmrOutput = "Your MMR change:<br>%d -> %d<br>%+d" % (
                currentMmr, nextMmr, mmrChange)
            return mmrOutput

    def updateDetails(self, ts=None):
        if not ts:
            ts = self.HuntSelect.currentData()
        if (ts == None):
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

        if qp:
            bounties = {'rifts_closed': 0}
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

        killData = getKillData(ts)
        targets = GetBounties(hunt)
        self.huntDetails.update(qp, bounties, accolades,
                                monsters_killed, targets)
        self.teamDetails.update(teams, hunters, hunt, killData,self.calculateMmrChange())

    def update(self):
        if debug:
            print('hunts.update')
        self.updateHuntSelection()
        self.updateDetails()

    def initHuntSelection(self):
        self.HuntSelect = QComboBox()
        self.HuntSelect.setIconSize(QSize(24, 24))
        self.HuntSelect.view().setSpacing(4)
        self.HuntSelect.setStyleSheet('QComboBox{padding:8px;}')

        self.HuntSelect.activated.connect(lambda : self.updateDetails())

    def updateHuntSelection(self):
        self.HuntSelect.clear()
        timeRange = int(settings.value("dropdown_range", str(7*24*60*60)))
        earliest = 0
        if timeRange > -1:
            earliest = time.time() - timeRange
        hunts = GetHunts(earliest)
        for hunt in hunts:
            ts = hunt['timestamp']
            dt = unix_to_datetime(ts)
            dead = hunt['MissionBagIsHunterDead'] == 'true'
            gameType = "Quick Play" if hunt['MissionBagIsQuickPlay'].lower(
            ) == 'true' else "Bounty Hunt"
            nTeams = hunt['MissionBagNumTeams']
            nKills = "%d kills" % sum(getKillData(ts)['team_kills'].values())
            ln = "%s - %s - %s %s - %s" % (dt, gameType, nTeams,
                                           "teams" if gameType == "Bounty Hunt" else "hunters", nKills)
            icon = QIcon(deadIcon if dead else livedIcon)

            self.HuntSelect.addItem(
                QIcon(deadIcon if dead else livedIcon), ln, ts)

    def initDetails(self):
        self.huntDetails = HuntDetails()
        self.teamDetails = TeamDetails()
