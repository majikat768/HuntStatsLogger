from PyQt6 import QtGui
from PyQt6.QtCore import QEvent, Qt
from PyQt6.QtWidgets import (QGridLayout, QGroupBox, QHBoxLayout, QLabel, QFrame, QPushButton,
                             QSizePolicy, QSplitter, QSplitterHandle, QScrollArea,
                             QStackedWidget, QStyledItemDelegate,
                             QStyleOptionViewItem, QTreeWidget,
                             QTreeWidgetItem, QVBoxLayout, QWidget)

from DbHandler import execute_query, GetCurrentMmr
from MainWindow.Hunts.TeamDetails.TeamButton import TeamButton
from MainWindow.Hunts.TeamDetails.TeamButtons import TeamButtons
from Widgets.Popup import Popup
from resources import *

icon_size = 16

class TeamDetails(QWidget):
    def __init__(self, parent=None):
        if debug:
            print("TeamDetails.__init__")
        super().__init__(parent)
        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.setLayout(self.layout)

        self.teamStack = QStackedWidget()
        self.teamStack.setObjectName("TeamStack")
        self.teamStack.setSizePolicy(QSizePolicy.Policy.Expanding,QSizePolicy.Policy.Expanding)

        self.teamButtons = TeamButtons()

        self.layout.addWidget(self.teamButtons)
        self.layout.addWidget(self.teamStack)
        self.layout.addStretch()

        self.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

    def update(self, teams, hunters, hunt):
        if debug:
            print("teamdetails.update")
        maxIconWidth = 0
        isQp = hunt['MissionBagIsQuickPlay'].lower() == 'true'

        while self.teamStack.count() > 0:
            self.teamStack.removeWidget(self.teamStack.currentWidget())

        clearLayout(self.teamButtons.main.layout)
        teamItems = {}
        ownTeamButton = None
        ownTeamWidget = None
        ownTeamInserted = False
        for i in range(len(teams)):
            team = teams[i]

            teamhunters = HuntersOnTeam(hunters, team)
            hadbounty = 0
            hadKills = False
            bountyextracted = 0
            ownTeam = False
            hadWellspring = False
            soulSurvivor = False


            tab = QWidget()
            tab.layout = QGridLayout()
            tab.setLayout(tab.layout)
            tab.setSizePolicy(
                QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

            teamMmr = team['mmr']
            teamMmrLabel = QLabel("Team MMR: %d" % teamMmr)
            teamRandom = (team['isinvite'].lower() == "false" and team['numplayers'] > 1)
            teamRandomLabel = QLabel("Randoms" if teamRandom else "")
            nHunters = team['numplayers']
            if not isQp:
                nHuntersLabel = QLabel("%d hunters" % nHunters)
            else:
                nHuntersLabel = QLabel(teamhunters[0]['blood_line_name'])

            tab.layout.addWidget(nHuntersLabel, 0, 0)
            tab.layout.addWidget(teamMmrLabel, 1, 0)
            tab.layout.addWidget(teamRandomLabel,0,2)
            if not isQp:
                tab.layout.addWidget(QLabel(),2,0)

            title = "%s hunters" % len(teamhunters)
            for j in range(len(teamhunters)):
                hunterWidget = self.GetHunterWidget(teamhunters[j], isQp)
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
                if len(name) > 15:
                    name = name[:12] + '...'
                if isQp:
                    title = name
            if bountyextracted:
                tab.layout.addWidget(
                    QLabel("Extracted with the bounty."), 3, 0)
            if soulSurvivor:
                tab.layout.addWidget(
                    QLabel("Soul Survivor."), 3, 0)
            tab.layout.setRowStretch(tab.layout.rowCount(), 1)

            self.teamStack.addWidget(tab)
            icons = []
            if ownTeam:
                icons.append(livedIcon)
                ownTeamWidget = tab
            if hadKills:
                icons.append(deadIcon)
            if hadWellspring or hadbounty:
                icons.append(bountyIcon)
            teamItems[i] = {'title': title, 'widget': tab,'icons':icons, 'ownteam':ownTeam}

            button = TeamButton(teamMmr=teamMmr,text=title,parent=self.teamButtons)
            button.ownTeam = ownTeam
            button.icons = icons
            button.setObjectName("TeamButton")
            button.setWidget(tab,self.switchTeamWidget)
            button.setIcons(icons)
            button.ownTeam = ownTeam
            if not ownTeam:
                self.teamButtons.addButton(button)
            else:
                ownTeamButton = button
        self.teamButtons.addButton(ownTeamButton)
        ownTeamButton.select()

        self.teamButtons.main.layout.addStretch()

        self.teamStack.setCurrentWidget(ownTeamWidget)

    def switchTeamWidget(self, tab):
        self.teamStack.setCurrentWidget(tab)

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


    def GetHunterWidget(self,hunter, isQp):
        hunterWidget = QWidget()
        hunterWidget.layout = QVBoxLayout()
        hunterWidget.setLayout(hunterWidget.layout)
        hunterWidget.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        hunterWidget.setObjectName("HunterWidget")
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

        if not isQp:
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
        iconWidget.layout.addWidget(get_icon(blankIcon,border=False))
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

