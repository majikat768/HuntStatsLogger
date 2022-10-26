from PyQt6.QtWidgets import QScrollArea, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QTabWidget, QStackedWidget, QListWidget, QSizePolicy
from PyQt6.QtCore import Qt
from resources import *
from DbHandler import *

class TeamDetails(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QHBoxLayout()
        self.setLayout(self.layout)

        self.stack = QStackedWidget()
        self.teamList = QListWidget()
        #self.teamList.setMaximumHeight(self.teamList.sizeHint().height()//4)
        #self.teamList.setSizePolicy(QSizePolicy.Policy.Fixed,QSizePolicy.Policy.Fixed)
        self.teamList.currentRowChanged.connect(self.switch)
        self.layout.addWidget(self.teamList)
        self.layout.addWidget(self.stack)
        #self.setSizePolicy(QSizePolicy.Policy.Fixed,QSizePolicy.Policy.Fixed)
        self.setObjectName("teamDetails")
        

    def switch(self,i):
        self.stack.setCurrentIndex(i)

    def update(self,teams, hunters, hunt):
        self.layout.removeWidget(self.stack)
        self.layout.removeWidget(self.teamList)
        self.stack = QStackedWidget()
        self.teamList = QListWidget()
        self.teamList.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.teamList.setMaximumHeight(self.teamList.sizeHint().height())
        self.teamList.currentRowChanged.connect(self.switch)
        self.layout.addWidget(self.teamList)
        self.layout.addWidget(self.stack)
        self.stack.setSizePolicy(QSizePolicy.Policy.MinimumExpanding,QSizePolicy.Policy.Fixed)
        self.teamList.setSizePolicy(QSizePolicy.Policy.Fixed,QSizePolicy.Policy.Expanding)
        self.layout.setAlignment(self.teamList,Qt.AlignmentFlag.AlignTop)
        self.layout.setAlignment(self.stack,Qt.AlignmentFlag.AlignTop)
        #self.clear()
        #print('teamdetails.update')

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

            teamMmr = QLabel("Team MMR: %d" % team['mmr'])
            nHunters = QLabel("Hunters: %d" % team['numplayers'])

            tab.layout.addWidget(teamMmr,0,0)
            tab.layout.addWidget(nHunters,1,0)

            teamhunters = HuntersOnTeam(hunters,team)
            bountyextracted = 0

            for j in range(len(teamhunters)):
                hunter = teamhunters[j]
                hunterWidget = QWidget()
                hunterWidget.layout = QVBoxLayout()
                hunterWidget.setLayout(hunterWidget.layout)
                name = hunter['blood_line_name']
                if name == settings.value("steam_name"):
                    ownTab = tabArea
                nameLabel = QLabel(hunter['blood_line_name'])
                mmr = hunter['mmr']
                mmrLabel = QLabel("%d" % mmr)
                stars = QLabel("<img src='%s'>" % (star_path()) * mmr_to_stars(mmr))
                bountypickedup = hunter['bountypickedup']
                hadWellspring = hunter['hadWellspring'].lower() == 'true'
                if hunter['bountyextracted']:
                    bountyextracted = 1

                kills = {
                    '%s killed you': hunter['killedme'],
                    '%s downed you': hunter['downedme'],
                    'you killed %s': hunter['killedbyme'],
                    'you downed %s': hunter['downedbyme'],
                    '%s killed your teammate': hunter['killedteammate'],
                    '%s downed your teammate': hunter['downedteammate'],
                    'your teammate killed %s': hunter['killedbyteammate'],
                    'your teammate downed %s': hunter['downedbyteammate']
                }

                killsLabel = QLabel(
                    "%s" % (
                        "<br>".join([
                            "%s %d times." % (
                                k % (name), kills[k]
                            )
                        for k in kills.keys() if kills[k] > 0])
                    )
                )
                killsLabel.setWordWrap(True)

                hunterWidget.layout.addWidget(nameLabel)
                hunterWidget.layout.addWidget(mmrLabel)
                hunterWidget.layout.addWidget(stars)
                hunterWidget.layout.addWidget(killsLabel)
                if bountypickedup:
                    hunterWidget.layout.addWidget(QLabel("%s carried the bounty." % name))
                if hadWellspring:
                    hunterWidget.layout.addWidget(QLabel("%s activated the Wellspring." % name))


                tab.layout.addWidget(hunterWidget,3,j)
                if(sum(kills.values()) > 0):
                    hadKills = True

                hunterWidget.layout.addStretch()
            if bountyextracted:
                tab.layout.addWidget(QLabel("Extracted with the bounty."),2,0)
            tab.layout.setRowStretch(tab.layout.rowCount(),1)
            tab.layout.setColumnStretch(tab.layout.columnCount(),1)
            tabArea.setMinimumHeight(int(tab.sizeHint().height()))

            tabArea.setWidget(tab)
            self.stack.addWidget(tab)
            if isQp:
                self.teamList.insertItem(i,'%s' % name)
            else:
                self.teamList.insertItem(i,'Team %d' % i)

def HuntersOnTeam(hunters, team):
    teamhunters = []
    for hunter in hunters:
        if hunter['team_num'] == team['team_num']:
            teamhunters.append(hunter)
    return teamhunters
