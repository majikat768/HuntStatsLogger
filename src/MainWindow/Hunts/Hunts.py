from PyQt6.QtWidgets import QWidget,QHBoxLayout,QGridLayout,QVBoxLayout,QGroupBox, QLabel, QSizePolicy, QScrollArea, QTabWidget,QPushButton,QDialog, QComboBox, QStackedWidget, QListWidget
from PyQt6.QtCore import Qt, QSize, QEvent
from PyQt6.QtGui import QIcon
from DbHandler import *
from MainWindow.Hunts.HuntDetails import HuntDetails
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
        self.layout = QGridLayout()
        self.setLayout(self.layout)

        self.SelectHuntBox = QGroupBox()
        self.SelectHuntBox.layout = QHBoxLayout()
        self.SelectHuntBox.setLayout(self.SelectHuntBox.layout)

        self.initDetails()
        self.initHuntSelection()
        self.layout.addWidget(self.HuntSelect,0,0,1,4)
        self.layout.addWidget(QLabel("Team details:"),1,1,1,1)
        self.layout.addWidget(self.teamScrollArea,2,1,5,3)
        self.layout.addWidget(QLabel("Teams:"),1,0,1,1)
        self.layout.addWidget(self.teamList,2,0,1,1)
        self.layout.addWidget(QLabel("Hunt details:"),3,0,1,1)
        self.layout.addWidget(self.huntDetails,4,0,3,1)
        #self.layout.addWidget(self.details,1,0,1,4)
        self.refreshButton = QPushButton(" reload ")
        self.refreshButton.clicked.connect(self.update)
        self.refreshButton.setSizePolicy(QSizePolicy.Policy.Fixed,QSizePolicy.Policy.Fixed)
        self.layout.addWidget(self.refreshButton,1,self.layout.columnCount()-1,1,1)
        self.layout.setRowStretch(self.layout.rowCount()-1,1)


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
        self.huntDetails.update(hunt,entries, accolades)
        self.updateTeamDetails(teams,hunters,hunt)

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
        self.huntDetails = HuntDetails()
        self.teamDetails = self.initTeamDetails()
        self.huntDetails.setFixedWidth(self.teamList.sizeHint().width())

    def initTeamDetails(self):
        self.teamScrollArea = QScrollArea()
        self.teamScrollArea.setWidgetResizable(True)
        self.teamStack = QStackedWidget()
        self.teamScrollArea.setObjectName("teamDetails")
        self.teamStack.setSizePolicy(QSizePolicy.Policy.Expanding,QSizePolicy.Policy.Expanding)
        #self.teamStack.setStyleSheet("QStackedWidget{border:0px;}")
        self.teamStack.setObjectName("TeamStack")
        self.teamScrollArea.setWidget(self.teamStack)
        self.teamList = QListWidget()
        self.teamList.currentRowChanged.connect(self.switchTeamWidget)
        self.teamScrollArea.setSizePolicy(QSizePolicy.Policy.Expanding,QSizePolicy.Policy.MinimumExpanding)
        self.teamList.setSizePolicy(QSizePolicy.Policy.Fixed,QSizePolicy.Policy.Maximum)
        self.teamList.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.teamList.setFixedWidth(self.teamList.sizeHint().width())
        #self.teamScrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

    def updateTeamDetails(self, teams, hunters, hunt):
        self.teamList.clear()
        while self.teamStack.count() > 0:
            self.teamStack.removeWidget(self.teamStack.currentWidget())

        isQp = hunt['MissionBagIsQuickPlay'].lower() == 'true'

        for i in range(len(teams)):
            hadKills = False
            team = teams[i]
            tabArea = QScrollArea()
            tabArea.setWidgetResizable(True)
            tabArea.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

            tab = QWidget()
            tab.layout = QGridLayout()
            tab.setLayout(tab.layout)

            teamLabel = QLabel("Team %d<br>" % i)
            teamMmr = team['mmr']
            teamMmrLabel = QLabel("Team MMR: %d" % teamMmr)
            nHunters = team['numplayers']
            nHuntersLabel = QLabel("Hunters: %d" % nHunters)

            tab.layout.addWidget(teamLabel,0,0)
            tab.layout.addWidget(teamMmrLabel,1,0)
            tab.layout.addWidget(nHuntersLabel,2,0)

            teamhunters = HuntersOnTeam(hunters,team)
            bountyextracted = 0

            hunterNames = []
            for j in range(len(teamhunters)):
                hunter = teamhunters[j]
                hunterWidget = QWidget()
                hunterWidget.layout = QVBoxLayout()
                hunterWidget.setLayout(hunterWidget.layout)
                name = hunter['blood_line_name']
                if isQp:
                    teamLabel.setText("%s<br>" % name)
                if name == settings.value("steam_name"):
                    ownTab = tabArea
                nameLabel = QLabel(hunter['blood_line_name'])
                mmr = hunter['mmr']
                hunterNames.append('  %s' % name)
                mmrLabel = QLabel("%d" % mmr)
                stars = "<img src='%s'>" % (star_path())*mmr_to_stars(mmr)
                starsLabel = QLabel("%s" % stars)
                bountypickedup = hunter['bountypickedup']
                hadWellspring = hunter['hadWellspring'].lower() == 'true'
                if hunter['bountyextracted']:
                    bountyextracted = 1

                kills = [
                    hunter['killedme'],
                    hunter['downedme'],
                    hunter['killedbyme'],
                    hunter['downedbyme'],
                    hunter['killedteammate'],
                    hunter['downedteammate'],
                    hunter['killedbyteammate'],
                    hunter['downedbyteammate']
                ]


                hunterWidget.layout.addWidget(nameLabel)
                hunterWidget.layout.addWidget(mmrLabel)
                hunterWidget.layout.addWidget(starsLabel)
                if hunter['killedme'] > 0 or hunter['downedme'] > 0:
                    icon = get_icon(killedByIcon)
                    icon.data = []
                    if hunter['killedme'] > 0:
                        icon.data.append('%s killed you %d times.' % (name,hunter['killedme'])),
                    if hunter['downedme'] > 0:
                        icon.data.append('%s downed you %d times.' % (name,hunter['downedme'])),
                    icon.installEventFilter(self)
                    hunterWidget.layout.addWidget(icon)
                if hunter['killedbyme'] > 0 or hunter['downedbyme'] > 0:
                    icon = get_icon(killedIcon)
                    icon.data = []
                    if hunter['killedbyme'] > 0:
                        icon.data.append('You killed %s %d times.' % (name,hunter['killedbyme'])),
                    if hunter['downedbyme'] > 0:
                        icon.data.append('You downed %s %d times.' % (name,hunter['downedbyme'])),
                    icon.installEventFilter(self)
                    hunterWidget.layout.addWidget(icon)
                if hunter['killedteammate'] > 0 or hunter['downedteammate'] > 0:
                    icon = get_icon(killedTeammateIcon)
                    icon.data = []
                    if hunter['killedteammate'] > 0:
                        icon.data.append('%s killed your teammates %d times.' % (name,hunter['killedteammate'])),
                    if hunter['downedteammate'] > 0:
                        icon.data.append('%s downed your teammates %d times.' % (name,hunter['downedteammate'])),
                    icon.installEventFilter(self)
                    hunterWidget.layout.addWidget(icon)
                if hunter['killedbyteammate'] > 0 or hunter['downedbyteammate'] > 0:
                    icon = get_icon(teammateKilledIcon)
                    icon.data = []
                    if hunter['killedbyteammate'] > 0:
                        icon.data.append('Your teammates killed %s %d times.' % (name,hunter['killedbyteammate'])),
                    if hunter['downedbyteammate'] > 0:
                        icon.data.append('Your teammates downed %s %d times.' % (name,hunter['downedbyteammate'])),
                    icon.installEventFilter(self)
                    hunterWidget.layout.addWidget(icon)
                if bountypickedup:
                    hunterWidget.layout.addWidget(QLabel("%s carried the bounty." % name))
                if hadWellspring:
                    hunterWidget.layout.addWidget(QLabel("%s activated the Wellspring." % name))


                tab.layout.addWidget(hunterWidget,3,j)
                if(sum(kills) > 0):
                    hadKills = True

                hunterWidget.layout.addStretch()
            if bountyextracted:
                tab.layout.addWidget(QLabel("Extracted with the bounty."),2,0)
            tab.layout.setRowStretch(tab.layout.rowCount(),1)
            tab.layout.setColumnStretch(tab.layout.columnCount(),1)
            tabArea.setMinimumHeight(int(tab.sizeHint().height()))

            tabArea.setWidget(tab)
            self.teamStack.addWidget(tab)

            if isQp:
                self.teamList.insertItem(i,'%s' % (name))
            else:
                self.teamList.insertItem(i,'Team %d - %s hunters' % (i,len(teamhunters)))
        self.teamList.setCurrentRow(0)
        self.teamList.setFixedHeight(self.teamList.sizeHint().height())
        self.teamScrollArea.setMinimumHeight(int(self.teamStack.sizeHint().height()*1.1))
        self.teamScrollArea.setMinimumWidth(int(self.teamStack.sizeHint().width()*1.1))

    def switchTeamWidget(self,idx):
        self.teamStack.setCurrentIndex(idx)

    def eventFilter(self, obj, event) -> bool:
        if event.type() == QEvent.Type.Enter:
            info = QWidget()
            info.layout = QVBoxLayout()
            info.setLayout(info.layout)
            x = event.globalPosition().x()
            y = event.globalPosition().y()
            for d in obj.data:
                info.layout.addWidget(QLabel(d))
            self.popup = Popup(info,x,y)
            #self.popup.keepAlive(True)
            self.popup.show()
            self.raise_()
            self.activateWindow()
        elif event.type() == QEvent.Type.Leave:
            try:
                self.popup.close()
            except:
                self.popup = None
        return super().eventFilter(obj, event)

def HuntersOnTeam(hunters, team):
    teamhunters = []
    for hunter in hunters:
        if hunter['team_num'] == team['team_num']:
            teamhunters.append(hunter)
    return teamhunters