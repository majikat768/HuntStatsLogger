from PyQt6.QtWidgets import QWidget, QStackedWidget, QListWidget, QGroupBox, QSizePolicy, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QListWidgetItem,QStyledItemDelegate,QStyleOptionViewItem
from PyQt6.QtCore import Qt, QEvent
from PyQt6 import QtGui
from resources import *
from DbHandler import execute_query
from Popup import Popup

class TeamDetails(QGroupBox):
    def __init__(self,parent=None):
        super().__init__(parent)
        self.layout = QGridLayout()
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.setLayout(self.layout)

        self.teamsArea = QWidget()
        self.setObjectName("teamDetails")
        self.teamsArea.setSizePolicy(QSizePolicy.Policy.Expanding,QSizePolicy.Policy.MinimumExpanding)

        self.teamStack = QStackedWidget()
        self.teamStack.setSizePolicy(QSizePolicy.Policy.Expanding,QSizePolicy.Policy.Expanding)
        self.teamStack.setObjectName("TeamStack")

        self.teamList = QListWidget()
        self.teamList.setItemDelegate(ItemDelegate())
        self.teamList.currentRowChanged.connect(self.switchTeamWidget)
        self.teamList.setSizePolicy(QSizePolicy.Policy.Fixed,QSizePolicy.Policy.Minimum)

        self.killsData = QGroupBox()
        self.killsData.layout = QVBoxLayout()
        self.killsData.setLayout(self.killsData.layout)
        self.teamKills = QLabel()
        self.yourKills = QLabel()
        self.yourAssists = QLabel()
        self.yourDeaths = QLabel()
        self.killsData.layout.addWidget(self.teamKills)
        self.killsData.layout.addWidget(self.yourKills)
        self.killsData.layout.addWidget(self.yourDeaths)
        self.killsData.layout.addWidget(self.yourAssists)

        self.layout.addWidget(self.teamList,0,0,1,1)
        self.layout.addWidget(self.killsData,1,0,1,1)
        self.layout.addWidget(self.teamStack,0,1,2,3)

    def update(self, teams, hunters, hunt, kills):
        qp = hunt['MissionBagIsQuickPlay'].lower() == 'true'
        team_kills = kills['team_kills']
        your_kills = kills['your_kills']
        your_deaths = kills['your_deaths']
        assists = kills['assists']
        if not qp:
            self.teamKills.setText(
                "Team kills: %d<br>%s" % (
                    sum(team_kills.values()),
                    '<br>'.join(["%sx %s" % (
                            team_kills[stars],
                            "<img src='%s'>"%(star_path())*stars
                        ) for stars in team_kills.keys() if team_kills[stars] > 0])
                )
            )
        else:
            self.teamKills.setText('')
        self.yourKills.setText(
            "Your kills: %d<br>%s" % (
                sum(your_kills.values()),
                '<br>'.join(["%sx %s" % (
                        your_kills[stars],
                        "<img src='%s'>"%(star_path())*stars
                    ) for stars in your_kills.keys() if your_kills[stars] > 0])
            )
        )

        self.yourAssists.setText("%d assists." % assists)
        self.yourDeaths.setText(
            "Your deaths: %d<br>%s" % (
                sum(your_deaths.values()),
                '<br>'.join(["%sx %s" % (
                        your_deaths[stars],
                        "<img src='%s'>"%(star_path())*stars
                    ) for stars in your_deaths.keys() if your_deaths[stars] > 0])
            )
        )

        self.teamList.clear()
        while self.teamStack.count() > 0:
            self.teamStack.removeWidget(self.teamStack.currentWidget())

        isQp = hunt['MissionBagIsQuickPlay'].lower() == 'true'

        for i in range(len(teams)):
            hadKills = False
            team = teams[i]

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
            hadbounty = 0
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
                nameLabel = QLabel(hunter['blood_line_name'])
                mmr = hunter['mmr']
                hunterNames.append('  %s' % name)
                mmrLabel = QLabel("%d" % mmr)
                stars = "<img src='%s'>" % (star_path())*mmr_to_stars(mmr)
                starsLabel = QLabel("%s" % stars)
                bountypickedup = hunter['bountypickedup']
                if bountypickedup:
                    hadbounty = 1
                hadWellspring = hunter['hadWellspring'].lower() == 'true'
                soulSurvivor = hunter['issoulsurvivor'].lower() == 'true'
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
                iconWidget = QWidget()
                iconWidget.layout = QHBoxLayout()
                iconWidget.setLayout(iconWidget.layout)
                if hunter['killedme'] > 0 or hunter['downedme'] > 0:
                    icon = get_icon(killedByIcon)
                    icon.data = []
                    if hunter['killedme'] > 0:
                        icon.data.append('%s killed you %d times.' % (name,hunter['killedme'])),
                    if hunter['downedme'] > 0:
                        icon.data.append('%s downed you %d times.' % (name,hunter['downedme'])),
                    icon.installEventFilter(self)
                    iconWidget.layout.addWidget(icon)
                if hunter['killedbyme'] > 0 or hunter['downedbyme'] > 0:
                    icon = get_icon(killedIcon)
                    icon.data = []
                    if hunter['killedbyme'] > 0:
                        icon.data.append('You killed %s %d times.' % (name,hunter['killedbyme'])),
                    if hunter['downedbyme'] > 0:
                        icon.data.append('You downed %s %d times.' % (name,hunter['downedbyme'])),
                    icon.installEventFilter(self)
                    iconWidget.layout.addWidget(icon)
                if hunter['killedteammate'] > 0 or hunter['downedteammate'] > 0:
                    icon = get_icon(killedTeammateIcon)
                    icon.data = []
                    if hunter['killedteammate'] > 0:
                        icon.data.append('%s killed your teammates %d times.' % (name,hunter['killedteammate'])),
                    if hunter['downedteammate'] > 0:
                        icon.data.append('%s downed your teammates %d times.' % (name,hunter['downedteammate'])),
                    icon.installEventFilter(self)
                    iconWidget.layout.addWidget(icon)
                if hunter['killedbyteammate'] > 0 or hunter['downedbyteammate'] > 0:
                    icon = get_icon(teammateKilledIcon)
                    icon.data = []
                    if hunter['killedbyteammate'] > 0:
                        icon.data.append('Your teammates killed %s %d times.' % (name,hunter['killedbyteammate'])),
                    if hunter['downedbyteammate'] > 0:
                        icon.data.append('Your teammates downed %s %d times.' % (name,hunter['downedbyteammate'])),
                    icon.installEventFilter(self)
                    iconWidget.layout.addWidget(icon)
                if bountypickedup or hadWellspring or soulSurvivor:
                    icon = get_icon(bountyIcon)
                    icon.data = []
                    if bountypickedup:
                        icon.data.append("%s carried the bounty." % name)
                    if hadWellspring:
                        icon.data.append("%s activated the Wellspring." % name)
                    if soulSurvivor:
                        icon.data.append("%s was the soul survivor." % name)
                    icon.installEventFilter(self)
                    iconWidget.layout.addWidget(icon)
                iconWidget.layout.addStretch()
                hunterWidget.layout.addWidget(iconWidget,0,Qt.AlignmentFlag.AlignLeft)
                hunterWidget.layout.setAlignment(Qt.AlignmentFlag.AlignLeft)


                tab.layout.addWidget(hunterWidget,4,j)
                if(sum(kills) > 0):
                    hadKills = True

                hunterWidget.layout.addStretch()
            if bountyextracted:
                tab.layout.addWidget(QLabel("Extracted with the bounty."),3,0)
            tab.layout.setRowStretch(tab.layout.rowCount(),1)
            tab.layout.setColumnStretch(tab.layout.columnCount(),1)

            self.teamStack.addWidget(tab)

            if hadKills:
                icon = QtGui.QIcon(deadIcon)
            elif hadWellspring or hadbounty:
                icon = QtGui.QIcon(bountyIcon)
            else:
                icon = QtGui.QIcon(blankIcon)
            if isQp:
                if len(name) > 10:
                    name = name[0:7] + '...'
                title = "%s - %d" % (name,teamMmr)
            else:
                title = "%s hunters - %d" % (len(teamhunters),teamMmr)
            item = QListWidgetItem(QtGui.QIcon(icon),title)
            self.teamList.insertItem(i,item)
        self.teamList.setCurrentRow(0)
        #self.teamList.setFixedHeight(self.teamList.sizeHint().height())
        self.teamsArea.setMinimumHeight(int(self.teamStack.sizeHint().height()*1.1))
        self.teamsArea.setMinimumWidth(int(self.teamStack.sizeHint().width()*1.1))

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


class ItemDelegate(QStyledItemDelegate):
    def paint(self,painter,option,index):
        option.decorationPosition = QStyleOptionViewItem.Position.Right
        super(ItemDelegate,self).paint(painter,option,index)