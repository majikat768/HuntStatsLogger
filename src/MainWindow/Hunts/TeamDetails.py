from PyQt6 import QtGui
from PyQt6.QtCore import QEvent, Qt
from PyQt6.QtWidgets import (QGridLayout, QGroupBox, QHBoxLayout, QLabel, QFrame,
                             QSizePolicy, QSplitter, QSplitterHandle, QScrollArea,
                             QStackedWidget, QStyledItemDelegate,
                             QStyleOptionViewItem, QTreeWidget,
                             QTreeWidgetItem, QVBoxLayout, QWidget)

from DbHandler import execute_query
from Widgets.Popup import Popup
from resources import *

icon_size = 16

class TeamDetails(QGroupBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.setLayout(self.layout)

        self.teamStack = QStackedWidget()
        self.teamStack.setObjectName("TeamStack")

        self.teamList = QTreeWidget()
        self.teamList.setIndentation(0)
        self.teamList.setItemsExpandable(False)
        #self.teamList.setHeaderHidden(True)
        self.teamList.setColumnCount(2)
        #self.teamList.setItemDelegate(ItemDelegate())
        self.teamList.currentItemChanged.connect(self.switchTeamWidget)
        self.teamList.setSizePolicy(QSizePolicy.Policy.Expanding,QSizePolicy.Policy.MinimumExpanding)
        self.teamList.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.leftColumn = QWidget()
        self.leftColumn.layout = QVBoxLayout()
        self.leftColumn.setLayout(self.leftColumn.layout)

        self.body = QSplitter(Qt.Orientation.Horizontal)
        self.body.setChildrenCollapsible(False)
        handleStyle = "QSplitter::handle:horizontal{image: url(\"%s\");}" % (resource_path("assets/icons/h_handle.png").replace("\\","/"));
        self.body.setStyleSheet(handleStyle);

        self.killsData = QGroupBox()
        self.killsData.setStyleSheet("QGroupBox{border:1px solid #44ffffff;}")
        self.killsData.layout = QVBoxLayout()
        self.killsData.setLayout(self.killsData.layout)
        self.killsData.setSizePolicy(QSizePolicy.Policy.Expanding,QSizePolicy.Policy.MinimumExpanding)

        self.leftColumn.layout.addWidget(self.teamList)
        self.leftColumn.layout.addWidget(self.killsData)
        self.body.addWidget(self.leftColumn)
        self.body.addWidget(self.teamStack)
        self.layout.addWidget(self.body)
        self.body.setStretchFactor(0,1)
        self.body.setStretchFactor(1,3)
        self.teamList.setHeaderLabels(["",""])
        self.teamList.header().setFixedHeight(4)
        self.teamList.header().setObjectName("teamsHeader")

        self.setStyleSheet("QGroupBox{border:0px;}")

        self.body.setSizePolicy(QSizePolicy.Policy.Expanding,QSizePolicy.Policy.Expanding)

        self.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

    def update(self, teams, hunters, hunt, kills,mmrChange):
        if debug:
            print("teamdetails.update")
        maxIconWidth = 0
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
        self.killsData.layout.addWidget(QLabel(mmrChange))
        self.killsData.layout.addStretch()

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

            teamLabel = QLabel("Team %d" % i)
            teamMmr = team['mmr']
            teamMmrLabel = QLabel("Team MMR: %d" % teamMmr)
            teamRandom = (team['isinvite'].lower() == "false" and team['numplayers'] > 1)
            teamRandomLabel = QLabel("Randoms" if teamRandom else "")
            nHunters = team['numplayers']
            nHuntersLabel = QLabel("%d hunters" % nHunters)

            tab.layout.addWidget(teamLabel, 0, 0)
            tab.layout.addWidget(teamMmrLabel, 1, 0)
            tab.layout.addWidget(teamRandomLabel,0,2)
            tab.layout.addWidget(nHuntersLabel, 1, 2)
            tab.layout.addWidget(QLabel(),2,0)
            tab.layout.addWidget(QLabel(),4,0)

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
                tab.layout.addWidget(hunterWidget, 5, j)
                tab.layout.setAlignment(hunterWidget,Qt.AlignmentFlag.AlignTop)

                if not hadKills:
                    hadKills = hunterWidget.hadKills
                if not hadbounty:
                    hadbounty = hunterWidget.hadbounty
                if not bountyextracted:
                    bountyextracted = hunterWidget.bountyextracted
                if not ownTeam:
                    ownTeam = hunterWidget.ownTeam
                if not hadWellspring:
                    hadWellspring = hunterWidget.hadWellspring
                if not soulSurvivor:
                    soulSurvivor = hunterWidget.soulSurvivor
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
            if hadKills:
                icons.append(deadIcon)
            if hadWellspring or hadbounty:
                icons.append(bountyIcon)
            item = QTreeWidgetItem()
            item.setText(0,title)
            item.view = tab
            # self.teamList.insertItem(i,item)
            teamItems[i] = {'title': title, 'widget': tab,'icons':icons, 'ownteam':ownTeam}

        ownTeamInserted = False
        maxIconWidth = 0
        for i in range(len(teamItems)):
            icons = teamItems[i]['icons']
            widget = teamItems[i]['widget']
            title = teamItems[i]['title']
            item = QTreeWidgetItem()
            item.view = widget
            if teamItems[i]['ownteam']:
                self.teamList.insertTopLevelItem(0,item)
                ownTeamInserted = True
            elif len(icons) > 0:
                if not ownTeamInserted:
                    self.teamList.insertTopLevelItem(0,item)
                else:
                    self.teamList.insertTopLevelItem(1,item)
            else:
                self.teamList.insertTopLevelItem(self.teamList.topLevelItemCount(),item)
             
            iconLabel = QLabel()
            pm = QPixmap(icon_size*(len(icons)+1),icon_size)
            pm.fill(QtGui.QColor(0,0,0,0))
            if len(icons) > 0:
                painter = QtGui.QPainter(pm)
                for j in range(len(icons)):
                    icon = icons[j]
                    painter.drawPixmap(j*icon_size,0,icon_size,icon_size,QPixmap(icon).scaled(icon_size,icon_size))
                del painter
                iconLabel.setPixmap(pm)
            maxIconWidth = max(maxIconWidth,icon_size*len(icons)+icon_size)
            #self.teamList.setItemWidget(item,0,label)
            item.setText(0,title)
            self.teamList.setItemWidget(item,1,iconLabel)
            iconLabel.setAlignment(Qt.AlignmentFlag.AlignRight)
            self.teamStack.addWidget(widget)
        self.teamList.setCurrentItem(self.teamList.itemAt(0,0))
        self.teamList.setColumnWidth(1,maxIconWidth)

    def switchTeamWidget(self, new,old):
        if new != None:
            self.teamStack.setCurrentWidget(new.view)
        else:
            self.teamStack.setCurrentWidget(old.view)

    def eventFilter(self, obj, event) -> bool:
        if obj.objectName() == "icon":
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
                    self.popup.hide()
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
        if int(pid) == int(settings.value("profileid","-1")):
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
