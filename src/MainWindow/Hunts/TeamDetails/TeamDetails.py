from PyQt6.QtCore import QEvent, Qt
from PyQt6.QtWidgets import (QGridLayout, QGroupBox, QHBoxLayout, QLabel, QPushButton,
                             QSizePolicy, QScrollArea,QVBoxLayout, QWidget)

from DbHandler import execute_query, GetCurrentMmr
from MainWindow.Hunts.TeamDetails.TeamButton import TeamButton
from Widgets.Popup import Popup
from Widgets.ScrollWidget import ScrollWidget
from resources import *

icon_size = 16

class TeamDetails(ScrollWidget):
    def __init__(self, parent=None):
        if debug:
            print("TeamDetails.__init__")
        super().__init__(parent)

        self.titleWidget = QWidget()
        self.titleWidget.layout = QHBoxLayout()
        self.titleWidget.setLayout(self.titleWidget.layout)
        titleLabel = QLabel("Teams")
        titleLabel.setStyleSheet("QLabel{font-size:16px;color:#cccc67;}")
        self.titleWidget.layout.addWidget(titleLabel)

        expandBtn = QPushButton("Expand All")
        expandBtn.setSizePolicy(QSizePolicy.Policy.Fixed,QSizePolicy.Policy.Fixed)
        expandBtn.clicked.connect(self.expandAll)

        collapseBtn = QPushButton("Collapse All")
        collapseBtn.setSizePolicy(QSizePolicy.Policy.Fixed,QSizePolicy.Policy.Fixed)
        collapseBtn.clicked.connect(self.collapseAll)

        self.titleWidget.layout.addWidget(expandBtn)
        self.titleWidget.layout.addWidget(collapseBtn)

        self.main.setObjectName("TeamDetails")

    def update(self, teams, hunters, hunt):
        if debug:
            print("teamdetails.update")
        isQp = hunt['MissionBagIsQuickPlay'].lower() == 'true'

        clearLayout(self.main.layout)

        self.addWidget(self.titleWidget)
        ownTeamWidget = None
        self.buttons = []

        for i in range(len(teams)):
            team = teams[i]
            teamhunters = HuntersOnTeam(hunters, team)
            teamhadbounty = 0
            hadKills = False
            kills = 0
            teambountyextracted = 0
            ownTeam = False
            hadWellspring = False
            soulSurvivor = False
            teamButton = TeamButton()
            self.buttons.append(teamButton)
            teamWidget = QGroupBox()
            teamWidget.layout = QVBoxLayout()
            teamWidget.setLayout(teamWidget.layout)
            teamWidget.setSizePolicy(QSizePolicy.Policy.Expanding,QSizePolicy.Policy.Minimum)
            teamWidget.setObjectName("TeamWidget")

            teamMmr = team['mmr']
            teamMmrLabel = QLabel("Match MMR: %d" % teamMmr)
            stars = "<img src='%s'>" % (star_path())*mmr_to_stars(teamMmr)
            starsLabel = QLabel("%s" % stars)
            teamRandom = (team['isinvite'].lower() == "false" and team['numplayers'] > 1)
            teamRandomStr = "Randoms" if teamRandom else "Invite" if team['numplayers'] > 1 else ""
            teamSizeStr = "Trio" if len(teamhunters) == 3 else "Duo" if len(teamhunters) == 2 else "Solo"
            teamFlavorLabel = QLabel(teamSizeStr)
            if len(teamRandomStr) > 0:
                teamFlavorLabel.setText(teamFlavorLabel.text() + " / " + teamRandomStr)
            nHunters = team['numplayers']
            if not isQp:
                nHuntersLabel = QLabel("%d hunters" % nHunters)
            else:
                nHuntersLabel = QLabel(teamhunters[0]['blood_line_name'])
            nHuntersLabel.setStyleSheet("QLabel{font-size:14px;}")
            nHuntersLabel.setText(', '.join([t['blood_line_name'] for t in teamhunters]))

            teamWidget.layout.addWidget(teamButton)

            huntersWidget = QWidget()
            huntersWidget.layout = QVBoxLayout()
            huntersWidget.setLayout(huntersWidget.layout)

            selfHunterWidget = None
            title = "%s hunters" % len(teamhunters)
            for j in range(len(teamhunters)):
                hunterWidget = self.GetHunterWidget(teamhunters[j],isQp)
                if not teambountyextracted and hunterWidget.bountyextracted:
                    teambountyextracted = True
                if not teamhadbounty and hunterWidget.hadbounty:
                    teamhadbounty = True
                if not ownTeam and hunterWidget.ownTeam:
                    ownTeam = True
                if not hadKills and hunterWidget.hadKills:
                    hadKills = True
                    kills += sum(hunterWidget.kills)
                huntersWidget.layout.addWidget(hunterWidget)

            iconStr = ""
            if hadKills:
                iconStr += "<img src='%s' height=24 width=24>" % killedIcon
            huntersWidget.layout.addStretch()
            if teambountyextracted:
                iconStr += "<img src='%s' height=24 width=24>" % bountyIcon 
            elif teamhadbounty:
                iconStr += "<img src='%s' height=24 width=24>" % bountyIcon 
 
            teamWidget.layout.addWidget(huntersWidget)
            huntersWidget.setVisible(False)

            teamWidget.setSizePolicy(QSizePolicy.Policy.Expanding,QSizePolicy.Policy.Minimum)

            huntersWidget.layout.addWidget(teamFlavorLabel)
            teamButton.layout.addWidget(nHuntersLabel,0,1,1,2)
            teamButton.layout.addWidget(teamFlavorLabel,1,1)
            teamButton.layout.addWidget(teamMmrLabel,2,1)
            teamButton.layout.addWidget(starsLabel,2,2)
            teamButton.layout.addWidget(QLabel(iconStr),0,3,2,1,Qt.AlignmentFlag.AlignRight)
            teamButton.layout.setColumnStretch(3,1)
            teamButton.setFixedHeight(teamButton.layout.sizeHint().height())

            teamButton.widget = huntersWidget

            if ownTeam:
                ownTeamWidget = teamWidget
                nHuntersLabel.setStyleSheet("QLabel{color:#cccc67;font-size:14px;}")
            elif hadKills:
                self.main.layout.insertWidget(1,teamWidget)
            else:
                self.addWidget(teamWidget)

        if ownTeamWidget:
            self.main.layout.insertWidget(1,ownTeamWidget)
        self.main.layout.addStretch()
            
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
        hunterWidget.layout = QGridLayout()
        hunterWidget.setLayout(hunterWidget.layout)
        hunterWidget.setObjectName("HunterWidget")

        hunterWidget.bountyextracted = False
        hunterWidget.hadbounty = False
        hunterWidget.hadKills = False
        hunterWidget.ownTeam = False

        name = hunter['blood_line_name']
        pid = hunter['profileid']
        n_games = execute_query(
            "select count(*) from 'hunters' where profileid is %d" % pid)
        n_games = 0 if len(n_games) == 0 else n_games[0][0]
        hunterWidget.ownTeam = int(pid) == int(settings.value("profileid","-1"))

        nameLabel = QLabel(hunter['blood_line_name'])
        mmrLabel = QLabel("MMR: %d" % hunter['mmr'])
        starsLabel = QLabel("<img src='%s'>" % (star_path())*mmr_to_stars(hunter['mmr']))

        n_gamesLabel = QLabel()
        if n_games > 1 and int(pid) != int(settings.value("profileid","-1")):
            n_gamesLabel.setText("seen in %d games" % n_games)
        
        hunterWidget.kills = [
            hunter['killedme'],
            hunter['downedme'],
            hunter['killedbyme'],
            hunter['downedbyme'],
            hunter['killedteammate'],
            hunter['downedteammate'],
            hunter['killedbyteammate'],
            hunter['downedbyteammate']
        ]
        wins = {
            'bountypickedup': int(hunter['bountypickedup']) > 0,
            'hadWellspring':hunter['hadWellspring'].lower() == 'true',
            'bountyextracted': int(hunter['bountyextracted']) > 0,
            'issoulsurvivor': hunter['issoulsurvivor'].lower() == 'true'
        }
        hunterWidget.bountyextracted = wins['bountyextracted']
        hunterWidget.hadbounty = wins['bountypickedup']

        hunterWidget.hadKills = sum(hunterWidget.kills) > 0 
        iconWidget = QWidget()
        iconWidget.layout = QHBoxLayout()
        iconWidget.setLayout(iconWidget.layout)
        iconWidget.layout.addWidget(get_icon(blankIcon,border=False))
        if hunter['killedme'] or hunter['downedme']:
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
        if hunter['killedteammate'] or hunter['downedteammate']:
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
        if hunter['killedbyme'] or hunter['downedbyme']:
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
        if hunter['killedbyteammate'] or hunter['downedbyteammate']:
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
        if wins['bountypickedup'] or wins['hadWellspring'] or wins['bountyextracted'] or wins['issoulsurvivor']:
            icon = get_icon(bountyIcon)
            icon.data = []
            if wins['bountypickedup']:
                icon.data.append("%s carried the bounty." % name)
            if wins['bountyextracted']:
                icon.data.append("%s extracted with the bounty." % name)
            if wins['hadWellspring']:
                icon.data.append("%s activated the Wellspring." % name)
            if wins['issoulsurvivor']:
                icon.data.append("%s was the soul survivor." % name)
            icon.installEventFilter(self)
            iconWidget.layout.addWidget(icon)

        iconWidget.setSizePolicy(QSizePolicy.Policy.Fixed,QSizePolicy.Policy.Fixed)

        hunterWidget.layout.addWidget(nameLabel,0,0,1,2,Qt.AlignmentFlag.AlignLeft)
        hunterWidget.layout.addWidget(mmrLabel,1,0,Qt.AlignmentFlag.AlignLeft)
        hunterWidget.layout.addWidget(starsLabel,1,1,Qt.AlignmentFlag.AlignLeft)
        if n_games > 1:
            hunterWidget.layout.addWidget(n_gamesLabel,2,0,1,2)
        hunterWidget.layout.addWidget(iconWidget,0,3,2,1,Qt.AlignmentFlag.AlignRight)

        hunterWidget.setSizePolicy(QSizePolicy.Policy.Minimum,QSizePolicy.Policy.Minimum)
        hunterWidget.layout.setColumnStretch(3,1)

        return hunterWidget
    
    def collapseAll(self):
        for button in self.buttons:
            button.widget.setVisible(False)
            button.unselect()
    def expandAll(self):
        for button in self.buttons:
            button.widget.setVisible(True)
            button.select()

def HuntersOnTeam(hunters, team):
    teamhunters = []
    for hunter in hunters:
        if hunter['team_num'] == team['team_num']:
            teamhunters.append(hunter)
    return teamhunters
