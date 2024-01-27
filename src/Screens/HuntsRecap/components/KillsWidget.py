from PyQt6.QtWidgets import QWidget, QGridLayout, QHBoxLayout, QSizePolicy,QGroupBox
from PyQt6 import QtCore
from DbHandler import get_kills_data, get_assists_data, execute_query
from resources import resource_path, mmr_to_stars, stars_pixmap, get_icon, settings
from Widgets.Label import Label

class KillsWidget(QGroupBox):
    def __init__(self, game_id, parent: QWidget | None = None):
        super().__init__(parent)
        self.game_id = game_id

        self.data = {}
        self.setObjectName("KillsTable")
        self.setTitle("Kills")
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_StyledBackground)
        self.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )
        self.layout = QGridLayout()
        self.setLayout(self.layout)
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0,0,0,0)

    # todo:
        # on star labels, add ToolTip displaying hunter name, and their mmr.
    def init(self):
        if(len(self.data) == 0):
            self.data = get_kills_data(self.game_id)
            self.assists = get_assists_data(self.game_id)

            my_kills = {i+1: 0 for i in range(6)}
            my_deaths = {i+1: 0 for i in range(6)}
            team_kills = {i+1: 0 for i in range(6)}
            team_deaths = {i+1: 0 for i in range(6)}

            for hunter in self.data:
                stars = mmr_to_stars(hunter['mmr'])
                my_kills[stars] += hunter['mykill']
                my_deaths[stars] += hunter['mydeath']
                team_kills[stars] += hunter['teamkill']
                team_deaths[stars] += hunter['teamdeath']
                team_kills[stars] += hunter['mykill']
                team_deaths[stars] += hunter['mydeath']

            youHeader = Label()
            youHeader.setText("You")
            teamHeader = Label()
            teamHeader.setText("Team")
            self.layout.addWidget(youHeader,0,0,1,1)
            self.layout.addWidget(teamHeader,0,1,1,1)
            youKills = Label("Kills: %d" % sum(my_kills.values()))
            teamKills = Label("Kills: %d" % sum(team_kills.values()))
            youKills.setObjectName("KillsSubWidgetHeader")
            teamKills.setObjectName("KillsSubWidgetHeader")
            self.layout.addWidget(youKills,1,0,1,1)
            self.layout.addWidget(teamKills,1,1,1,1)

            youRow = 2
            teamRow = 2
            for i in range(1,7):
                if(my_kills[i] > 0):
                    w = QWidget()
                    w.layout = QHBoxLayout()
                    w.setLayout(w.layout)
                    w.layout.setContentsMargins(8,2,8,2)
                    starWidget = Label()
                    starWidget.setPixmap(stars_pixmap(i,h=12))
                    w.layout.addWidget(Label(str(my_kills[i])))
                    w.layout.addWidget(starWidget,alignment=QtCore.Qt.AlignmentFlag.AlignRight)
                    self.layout.addWidget(w,youRow,0)
                    youRow += 1
                if(team_kills[i] > 0):
                    w = QWidget()
                    w.layout = QHBoxLayout()
                    w.setLayout(w.layout)
                    w.layout.setContentsMargins(8,2,8,2)
                    w.layout.addWidget(Label(str(team_kills[i])))
                    starWidget = Label()
                    starWidget.setPixmap(stars_pixmap(i,h=12))
                    w.layout.addWidget(starWidget,alignment=QtCore.Qt.AlignmentFlag.AlignRight)
                    self.layout.addWidget(w,teamRow,1)
                    teamRow += 1
            while youRow < teamRow:
                self.layout.addWidget(Label(),youRow,0)
                youRow += 1
            while teamRow < youRow:
                self.layout.addWidget(Label(),teamRow,1)
                teamRow += 1

            youRow += 1
            teamRow += 1
            youDeaths = Label("Deaths: %d" % sum(my_deaths.values()))
            youDeaths.setObjectName("KillsSubWidgetHeader")
            teamDeaths = Label("Deaths: %d" % sum(team_deaths.values()))
            teamDeaths.setObjectName("KillsSubWidgetHeader")
            self.layout.addWidget(youDeaths,youRow,0)
            self.layout.addWidget(teamDeaths,teamRow,1)
            youRow += 1
            teamRow += 1
            for i in range(1,7):
                if(my_deaths[i] > 0):
                    w = QWidget()
                    w.layout = QHBoxLayout()
                    w.setLayout(w.layout)
                    w.layout.setContentsMargins(8,2,8,2)
                    w.layout.addWidget(Label(str(my_deaths[i])))
                    starWidget = Label()
                    starWidget.setPixmap(stars_pixmap(i,h=12))
                    w.layout.addWidget(starWidget,alignment=QtCore.Qt.AlignmentFlag.AlignRight)
                    self.layout.addWidget(w,youRow,0)
                    youRow += 1
                if(team_deaths[i] > 0):
                    w = QWidget()
                    w.layout = QHBoxLayout()
                    w.setLayout(w.layout)
                    w.layout.setContentsMargins(8,2,8,2)
                    w.layout.addWidget(Label(str(team_deaths[i])))
                    starWidget = Label()
                    starWidget.setPixmap(stars_pixmap(i,h=12))
                    w.layout.addWidget(starWidget,alignment=QtCore.Qt.AlignmentFlag.AlignRight)
                    self.layout.addWidget(w,teamRow,1)
                    teamRow += 1
            while youRow < teamRow:
                self.layout.addWidget(Label(),youRow,0)
                youRow += 1
            while teamRow < youRow:
                self.layout.addWidget(Label(),teamRow,1)
                teamRow += 1
            youRow += 1

            assistsWidget = Label("Assists: %d" % self.assists)
            assistsWidget.setObjectName("KillsSubWidgetHeader")
            self.layout.addWidget(assistsWidget,youRow,0,1,2)
            self.layout.addWidget(self.getMmrWidget(),youRow+1,0,2,2)
            self.layout.setRowStretch(self.layout.rowCount(),1)
        self.setMinimumHeight(self.sizeHint().height())

    def getMmrWidget(self):
        w = QWidget()
        w.layout = QHBoxLayout()
        w.setLayout(w.layout)
        w.layout.setContentsMargins(8,2,8,2)
        [mmrDiff,mmrIcon] = self.getMmrDiff()
        mmrIcon.setObjectName("mmrIcon")
        mmrDiff.setObjectName("mmrIcon")
        w.layout.addWidget(mmrDiff)
        w.layout.addWidget(mmrIcon)
        w.layout.setAlignment(mmrIcon,QtCore.Qt.AlignmentFlag.AlignRight)
        w.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )
        w.setMinimumHeight(w.sizeHint().height())
        return w

    def getMmrDiff(self):
        ts = execute_query("select timestamp from 'games' where game_id = ?", self.game_id)[0][0]
        mmrs = execute_query("select mmr,timestamp from 'hunters' h\
                                            where blood_line_name is ? and timestamp >= ?\
                                            order by timestamp asc limit 2", settings.value("steam_name",""),ts)
        mmrChangeText = "MMR Δ"
        if len(mmrs) == 0:
            return [Label(mmrChangeText+": 0"), get_icon("assets/icons/mmrEqIcon.png" , height=36)]
        current = mmrs[0][0]
        est = self.calculateMmrChange(current)
        if len(mmrs) > 1:
            diff = mmrs[1][0] - mmrs[0][0]
            mmrChangeText += ": %+d\n" % diff
            icon = "mmrDecIcon.png" if diff < 0 else "mmrIncIcon.png" if diff > 0 else "mmrEqIcon.png"
        else:
            icon = "mmrDecIcon.png" if est < 0 else "mmrIncIcon.png" if est > 0 else "mmrEqIcon.png"
        mmrChangeText += " Est: %+d" % est

        return [Label(mmrChangeText), get_icon("assets/icons/%s" % icon, height=36)]

    # thanks @Huakas
    def calculateMmrChange(self, currentMmr):
        predictedChange = 0
        for hunter in self.data:
            kills = hunter['mykill']
            deaths = hunter['mydeath']
            mmr = hunter['mmr']
            killValue = min(15,(currentMmr - mmr) / 25)
            predictedChange += (15 - killValue) * kills
            deathValue = max(-15, (currentMmr - mmr) / 25)
            predictedChange += (-15 - deathValue) * deaths
        return predictedChange