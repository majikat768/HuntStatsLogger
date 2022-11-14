from PyQt6 import QtGui
from PyQt6.QtCore import QEvent, Qt
from PyQt6.QtWidgets import (QGridLayout, QGroupBox, QHBoxLayout, QLabel,
                             QListWidget, QListWidgetItem, QSizePolicy,
                             QStackedWidget, QStyledItemDelegate,
                             QStyleOptionViewItem, QTreeWidget,
                             QTreeWidgetItem, QVBoxLayout, QWidget)

from DbHandler import execute_query
from Popup import Popup
from resources import *


class TeamDetails(QGroupBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QGridLayout()
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.setLayout(self.layout)

        self.teamsArea = QWidget()
        self.setObjectName("teamDetails")
        self.teamsArea.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        self.teamStack = QStackedWidget()
        self.teamStack.setObjectName("TeamStack")

        self.teamList = QTreeWidget()
        self.teamList.setHeaderHidden(True)
        self.teamList.setColumnCount(2)
        self.teamList.setItemDelegate(ItemDelegate())
        self.teamList.currentItemChanged.connect(self.switchTeamWidget)
        self.teamList.setDropIndicatorShown(False)

        self.killsData = QGroupBox()
        self.killsData.layout = QVBoxLayout()
        self.killsData.setLayout(self.killsData.layout)

        self.layout.addWidget(self.teamList, 0, 0, 1, 1)
        self.layout.addWidget(self.killsData, 1, 0, 1, 1)
        self.layout.addWidget(self.teamStack, 0, 1, 2, 2)
        self.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.layout.setColumnStretch(1, 1)

    def update(self, teams, hunters, hunt, kills):
        qp = hunt['MissionBagIsQuickPlay'].lower() == 'true'
        clearLayout(self.killsData.layout)
        team_kills = kills['team_kills']
        your_kills = kills['your_kills']
        your_deaths = kills['your_deaths']
        assists = kills['assists']
        if not qp:
            teamKills = QLabel(
                "Team kills: %d<br>%s" % (
                    sum(team_kills.values()),
                    '<br>'.join(["%sx %s" % (
                        team_kills[stars],
                        "<img src='%s'>" % (star_path())*stars
                    ) for stars in team_kills.keys() if team_kills[stars] > 0])
                )
            )
            self.killsData.layout.addWidget(teamKills)

        yourKills = QLabel(
            "Your kills: %d<br>%s" % (
                sum(your_kills.values()),
                '<br>'.join(["%sx %s" % (
                    your_kills[stars],
                    "<img src='%s'>" % (star_path())*stars
                ) for stars in your_kills.keys() if your_kills[stars] > 0])
            )
        )
        self.killsData.layout.addWidget(yourKills)

        yourAssists = QLabel("%d assists." % assists)
        self.killsData.layout.addWidget(yourAssists)

        yourDeaths = QLabel(
            "Your deaths: %d<br>%s" % (
                sum(your_deaths.values()),
                '<br>'.join(["%sx %s" % (
                    your_deaths[stars],
                    "<img src='%s'>" % (star_path())*stars
                ) for stars in your_deaths.keys() if your_deaths[stars] > 0])
            )
        )
        self.killsData.layout.addWidget(yourDeaths)

        self.teamList.clear()
        while self.teamStack.count() > 0:
            self.teamStack.removeWidget(self.teamStack.currentWidget())

        isQp = hunt['MissionBagIsQuickPlay'].lower() == 'true'
        teamItems = {}
        for i in range(len(teams)):
            team = teams[i]

            tab = QWidget()
            tab.layout = QGridLayout()
            tab.setLayout(tab.layout)
            tab.setSizePolicy(
                QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

            teamLabel = QLabel("Team %d<br>" % i)
            teamMmr = team['mmr']
            teamMmrLabel = QLabel("Team MMR: %d" % teamMmr)
            nHunters = team['numplayers']
            nHuntersLabel = QLabel("Hunters: %d" % nHunters)

            tab.layout.addWidget(teamLabel, 0, 0)
            tab.layout.addWidget(teamMmrLabel, 1, 0)
            tab.layout.addWidget(nHuntersLabel, 2, 0)

            teamhunters = HuntersOnTeam(hunters, team)
            hadbounty = 0
            hadKills = False
            bountyextracted = 0
            ownTeam = False
            hadWellspring = False
            soulSurvivor = False

            title = "%s hunters - %d" % (len(teamhunters), teamMmr)
            title = "%s hunters" % len(teamhunters)
            for j in range(len(teamhunters)):
                hunterWidget = self.GetHunterWidget(teamhunters[j])
                tab.layout.addWidget(hunterWidget, 4, j)

                hadKills = not hadKills and hunterWidget.hadKills
                hadbounty = not hadbounty and hunterWidget.hadbounty
                bountyextracted = not bountyextracted and hunterWidget.bountyextracted
                ownTeam = not ownTeam and hunterWidget.ownTeam
                hadWellspring = not hadWellspring and hunterWidget.hadWellspring
                soulSurvivor = not soulSurvivor and hunterWidget.soulSurvivor
                name = teamhunters[j]['blood_line_name']
                if isQp:
                    title = name
            if bountyextracted:
                tab.layout.addWidget(
                    QLabel("Extracted with the bounty."), 3, 0)
            tab.layout.setRowStretch(tab.layout.rowCount(), 1)
            tab.layout.setColumnStretch(tab.layout.columnCount(), 1)

            self.teamStack.addWidget(tab)
            icons = []
            if ownTeam:
                icons.append(livedIcon)
                print('own',title)
            if hadKills:
                icons.append(deadIcon)
            if hadWellspring or hadbounty:
                icons.append(bountyIcon)
            item = QTreeWidgetItem()
            item.setText(0,title)
            item.view = tab
            item.idx = i
            # self.teamList.insertItem(i,item)
            teamItems[i] = {'item': item, 'widget': tab,'icons':icons}

        for i in range(len(teamItems)):
            icons = teamItems[i]['icons']
            if livedIcon in icons:
                self.teamList.insertTopLevelItem(0,teamItems[i]['item'])
            else:
                if deadIcon in icons or bountyIcon in icons:
                    if self.teamList.topLevelItemCount() > 0:
                        self.teamList.insertTopLevelItem(1,teamItems[i]['item'])
                    else:
                        self.teamList.insertTopLevelItem(0,teamItems[i]['item'])
                else:
                    self.teamList.insertTopLevelItem(self.teamList.topLevelItemCount(),teamItems[i]['item'])
                
            icons = teamItems[i]['icons']
            icoLabel = QLabel()
            print('i',len(icons))
            pm = QPixmap(32*len(icons),32)
            pm.fill(QtGui.QColor(0,0,0,0))
            if len(icons) > 0:
                painter = QtGui.QPainter(pm)
                for j in range(len(icons)):
                    icon = icons[j]
                    painter.drawPixmap(j*32,0,32,32,QPixmap(icon).scaled(32,32))
                del painter
                icoLabel.setPixmap(pm)
                self.teamList.setItemWidget(teamItems[i]['item'],1,icoLabel)
                self.teamList.setColumnWidth(1,pm.width())
            self.teamStack.addWidget(teamItems[i]['widget'])
            print('pm',pm.width())
            self.teamList.setColumnWidth(
                0,
                min(self.teamList.columnWidth(0),self.teamList.width()-pm.width())
            )
        self.teamList.setCurrentItem(self.teamList.itemAt(0,0))

        # self.teamList.setFixedHeight(self.teamList.sizeHint().height())
        #self.teamList.setFixedWidth(int(self.teamList.sizeHint().width()*1.2))

    def switchTeamWidget(self, new,old):
        if new != None:
            self.teamStack.setCurrentWidget(new.view)
        else:
            self.teamStack.setCurrentWidget(old.view)

    def eventFilter(self, obj, event) -> bool:
        if event.type() == QEvent.Type.Enter:
            info = QWidget()
            info.layout = QVBoxLayout()
            info.setLayout(info.layout)
            x = event.globalPosition().x()
            y = event.globalPosition().y()
            for d in obj.data:
                info.layout.addWidget(QLabel(d))
            self.popup = Popup(info, x, y)
            # self.popup.keepAlive(True)
            self.popup.show()
            self.raise_()
            self.activateWindow()
        elif event.type() == QEvent.Type.Leave:
            try:
                self.popup.close()
            except:
                self.popup = None
        return super().eventFilter(obj, event)


    def GetHunterWidget(self,hunter):
        hunterWidget = QWidget()
        hunterWidget.layout = QVBoxLayout()
        hunterWidget.setLayout(hunterWidget.layout)
        hunterWidget.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        name = hunter['blood_line_name']
        pid = hunter['profileid']
        n_games = execute_query(
            "select count(*) from 'hunters' where profileid is %d" % pid)
        n_games = 0 if len(n_games) == 0 else n_games[0][0]
        if name.lower() == settings.value("steam_name", "").lower():
            hunterWidget.ownTeam = True
        else:
            hunterWidget.ownTeam = False
        #if isQp:
        #    teamLabel.setText("%s<br>" % name)
        nameLabel = QLabel(hunter['blood_line_name'])
        mmr = hunter['mmr']
        mmrLabel = QLabel("%d" % mmr)
        stars = "<img src='%s'>" % (star_path())*mmr_to_stars(mmr)
        starsLabel = QLabel("%s" % stars)
        n_gamesLabel = QLabel()
        if n_games > 1:
            n_gamesLabel.setText("seen in %d games" % n_games)
        bountypickedup = hunter['bountypickedup']
        if bountypickedup:
            hunterWidget.hadbounty = 1
        else:
            hunterWidget.hadbounty = 0
        hunterWidget.hadWellspring = hunter['hadWellspring'].lower() == 'true'
        hunterWidget.soulSurvivor = hunter['issoulsurvivor'].lower() == 'true'
        if hunter['bountyextracted']:
            hunterWidget.bountyextracted = 1
        else:
            hunterWidget.bountyextracted = 0

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
        hunterWidget.layout.addWidget(n_gamesLabel)
        iconWidget = QWidget()
        iconWidget.layout = QHBoxLayout()
        iconWidget.setLayout(iconWidget.layout)
        if hunter['killedme'] > 0 or hunter['downedme'] > 0:
            icon = get_icon(killedByIcon)
            icon.data = []
            if hunter['killedme'] > 0:
                icon.data.append('%s killed you %d times.' %
                                    (name, hunter['killedme'])),
            if hunter['downedme'] > 0:
                icon.data.append('%s downed you %d times.' %
                                    (name, hunter['downedme'])),
            icon.installEventFilter(self)
            iconWidget.layout.addWidget(icon)
        if hunter['killedbyme'] > 0 or hunter['downedbyme'] > 0:
            icon = get_icon(killedIcon)
            icon.data = []
            if hunter['killedbyme'] > 0:
                icon.data.append('You killed %s %d times.' %
                                    (name, hunter['killedbyme'])),
            if hunter['downedbyme'] > 0:
                icon.data.append('You downed %s %d times.' %
                                    (name, hunter['downedbyme'])),
            icon.installEventFilter(self)
            iconWidget.layout.addWidget(icon)
        if hunter['killedteammate'] > 0 or hunter['downedteammate'] > 0:
            icon = get_icon(killedTeammateIcon)
            icon.data = []
            if hunter['killedteammate'] > 0:
                icon.data.append('%s killed your teammates %d times.' % (
                    name, hunter['killedteammate'])),
            if hunter['downedteammate'] > 0:
                icon.data.append('%s downed your teammates %d times.' % (
                    name, hunter['downedteammate'])),
            icon.installEventFilter(self)
            iconWidget.layout.addWidget(icon)
        if hunter['killedbyteammate'] > 0 or hunter['downedbyteammate'] > 0:
            icon = get_icon(teammateKilledIcon)
            icon.data = []
            if hunter['killedbyteammate'] > 0:
                icon.data.append('Your teammates killed %s %d times.' % (
                    name, hunter['killedbyteammate'])),
            if hunter['downedbyteammate'] > 0:
                icon.data.append('Your teammates downed %s %d times.' % (
                    name, hunter['downedbyteammate'])),
            icon.installEventFilter(self)
            iconWidget.layout.addWidget(icon)
        if bountypickedup or hunterWidget.hadWellspring or hunterWidget.soulSurvivor:
            icon = get_icon(bountyIcon)
            icon.data = []
            if bountypickedup:
                icon.data.append("%s carried the bounty." % name)
            if hunterWidget.hadWellspring:
                icon.data.append("%s activated the Wellspring." % name)
            if hunterWidget.soulSurvivor:
                icon.data.append("%s was the soul survivor." % name)
            icon.installEventFilter(self)
            iconWidget.layout.addWidget(icon)
        iconWidget.layout.addStretch()
        hunterWidget.layout.addWidget(
            iconWidget, 0, Qt.AlignmentFlag.AlignLeft)
        hunterWidget.layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        hunterWidget.layout.addStretch()

        if (sum(kills) > 0):
            hunterWidget.hadKills = True
        else:
            hunterWidget.hadKills = False
        return hunterWidget


def HuntersOnTeam(hunters, team):
    teamhunters = []
    for hunter in hunters:
        if hunter['team_num'] == team['team_num']:
            teamhunters.append(hunter)
    return teamhunters


class ItemDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index):
        option.decorationPosition = QStyleOptionViewItem.Position.Right
        super(ItemDelegate, self).paint(painter, option, index)


