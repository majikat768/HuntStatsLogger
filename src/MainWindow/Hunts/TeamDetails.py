from PyQt6.QtWidgets import QScrollArea, QWidget, QVBoxLayout, QGridLayout, QLabel, QTabWidget
from PyQt6.QtCore import Qt
from resources import *
from DbHandler import *

class TeamDetails(QTabWidget):
    def __init__(self):
        super().__init__()
        self.tabs = QTabWidget()

    def update(self,teams, hunters, hunt):
        self.clear()
        #print('teamdetails.update')

        isQp = hunt['MissionBagIsQuickPlay'].lower() == 'true'

        ownTab = None
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
            if bountyextracted:
                tab.layout.addWidget(QLabel("Extracted with the bounty."),2,0)
            tab.layout.setRowStretch(tab.layout.rowCount(),1)
            tab.layout.setColumnStretch(tab.layout.columnCount(),1)
            tabArea.setMinimumHeight(int(tab.sizeHint().height()))

            tabArea.setWidget(tab)
            if isQp:
                self.addTab(tabArea,"%s" % name)
            else:
                self.addTab(tabArea,"Team %d" % i)
            if hadKills:
                self.tabBar().moveTab(self.indexOf(tabArea),0)
        ownIdx = self.indexOf(ownTab)
        self.tabBar().moveTab(ownIdx,0)
        self.tabBar().setCurrentIndex(0)


def HuntersOnTeam(hunters, team):
    teamhunters = []
    for hunter in hunters:
        if hunter['team_num'] == team['team_num']:
            teamhunters.append(hunter)
    return teamhunters
