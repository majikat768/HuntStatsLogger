from PyQt6.QtWidgets import QWidget, QHBoxLayout, QSizePolicy, QComboBox
from PyQt6 import QtCore
from resources import settings, comboBoxStyle
from DbHandler import execute_query
from Widgets.Label import Label
import time

class KDA(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        self.layout = QHBoxLayout()
        self.setLayout(self.layout)
        self.layout.setContentsMargins(0,0,0,0)
        self.layout.setSpacing(0)
        self.kills = 0
        self.deaths = 1
        self.assists = 0
        self.kda = 0.0

        self.last_hunt = None

        self.kdaLabel = Label("KDA: %.3f" % self.kda)
        self.killsLabel = Label("Kills %d" % self.kills)
        self.deathsLabel = Label("Deaths %d" % self.deaths)
        self.assistsLabel = Label("Assists %d" % self.assists)

        self.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Minimum
        )
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_StyledBackground)      

        self.huntCountLabel = Label()
        self.huntCountLabel.setStyleSheet("Label{border:2px solid #888;}")
        self.huntCountLabel.setSizePolicy(
            QSizePolicy.Policy.Fixed,
            QSizePolicy.Policy.Fixed,
        )
        #self.layout.addWidget(self.huntCountLabel)
        self.layout.addWidget(self.kdaLabel)
        self.layout.addWidget(self.killsLabel)
        self.layout.addWidget(self.deathsLabel)
        self.layout.addWidget(self.assistsLabel)

        self.dropdowns = self.init_dropdowns()
        self.layout.addWidget(self.dropdowns)
        self.init()

        self.setFixedHeight(self.sizeHint().height())


    def init_dropdowns(self):
        dropdowns = QWidget()
        dropdowns.setObjectName("KdaDropdowns")
        dropdowns.layout = QHBoxLayout()
        dropdowns.layout.setSpacing(0)
        dropdowns.layout.setContentsMargins(0,0,0,0)
        dropdowns.setLayout(dropdowns.layout)

        gametype = QComboBox()
        gametype.setStyleSheet(comboBoxStyle)
        gametype.setSizePolicy(QSizePolicy.Policy.Minimum,QSizePolicy.Policy.Expanding)
        gametype.addItems([
            "All Games",
            "Bounty Hunt",
            "Soul Survivor",
        ])
        gametype.setCurrentText(settings.value("KdaGameType","All Games"))

        timeframe = QComboBox()
        timeframe.setStyleSheet(comboBoxStyle)
        timeframe.setSizePolicy(QSizePolicy.Policy.Minimum,QSizePolicy.Policy.Expanding)
        timeframe.addItem("Hour",60*60)
        timeframe.addItem("Day",60*60*24)
        timeframe.addItem("Week",60*60*24*7)
        timeframe.addItem("Month",60*60*24*4)
        timeframe.addItem("Year",60*60*24*365)
        timeframe.addItem("All Time",-1)

        timeframe.setCurrentText(settings.value("KdaTimeframe","All Time"))
        gametype.activated.connect(self.init)
        timeframe.activated.connect(self.init)

        self.gametype = gametype
        self.timeframe = timeframe
        dropdowns.layout.addWidget(Label("Game Type"))
        dropdowns.layout.addWidget(gametype)
        dropdowns.layout.addWidget(Label("Timeframe"))
        dropdowns.layout.addWidget(timeframe)
        return dropdowns

    def update(self):
        last_hunt = execute_query("select g.game_id from 'games' g order by timestamp desc limit 1")
        if len(last_hunt) == 0:
            return
        last_hunt = last_hunt[0][0]
        if last_hunt != self.last_hunt:
            self.last_hunt = last_hunt
            [kills,deaths] = execute_query("select sum(h.downedbyme+h.killedbyme) as kills,\
                                        sum(h.downedme+h.killedme) as deaths from\
                                            'hunters' h where h.game_id = ?",last_hunt)[0]
            self.kills += kills
            self.deaths += deaths
            assists = execute_query("select sum(e.amount) as assists\
                                     from 'entries' e\
                                     where e.category is 'accolade_players_killed_assist'\
                                     and e.game_id = ?",last_hunt)[0][0]
            assists = 0 if assists == None else assists
            self.assists += assists
            self.kda = self.calc(self.kills,self.deaths,self.assists)
            self.kdaLabel.setText("KDA: %.3f" % self.kda)
            self.kdaLabel.setToolTip("%d / %d / %d" % (self.kills,self.deaths,self.assists))
            self.killsLabel.setText("Kills %d" % (self.kills))
            self.deathsLabel.setText("Deaths %d" % self.deaths)
            self.assistsLabel.setText("Assists %d" % self.assists)


    def init(self):
        self.totalHunts = execute_query("select count(*) from 'games'")
        if len(self.totalHunts) == 0:
            self.totalHunts = 0
        else:
            self.totalHunts = self.totalHunts[0][0]
        self.huntCountLabel.setText("Hunts: %d" % self.totalHunts)
        settings.setValue("KdaGameType",self.gametype.currentText())
        settings.setValue("KdaTimeframe",self.timeframe.currentText())

        timespan = time.time() - self.timeframe.currentData()
        gametype = self.gametype.currentText()
        if(self.timeframe.currentData() == -1):
            timespan = 0

        gtCondition = "and g.MissionBagIsQuickPlay = %s" % ("'true'" if gametype == "Soul Survivor" else "'false'") if gametype != "All Games" else ""
        last_hunt = execute_query("select g.game_id from 'games' g order by timestamp desc limit 1")
        if len(last_hunt) == 0:
            return

        self.last_hunt = last_hunt[0][0]
        kills_data = execute_query("select sum(h.downedbyme + h.killedbyme) as kills,\
                                    sum(h.downedme + h.killedme) as deaths\
                                    from 'hunters' h\
                                    join 'games' g on g.game_id = h.game_id\
                                    where h.timestamp > ?\
                                    %s" % gtCondition, timespan)

        self.assists = execute_query("select sum(e.amount)\
                                    from 'entries' e\
                                    join 'games' g on g.game_id = e.game_id\
                                    where e.category is 'accolade_players_killed_assist'\
                                    %s\
                                    and e.timestamp > ?" % gtCondition,timespan)
        if len(kills_data) == 0:
            return
        if len(self.assists) == 0:
            self.assists = 0
        else:
            self.assists = self.assists[0][0]
        [self.kills,self.deaths] = kills_data[0]
        if self.kills is None:
            self.kills = 0
        if self.deaths is None:
            self.deaths = 0
        if self.assists is None:
            self.assists = 0
        self.kda = self.calc(self.kills,self.deaths,self.assists)
        self.kdaLabel.setText("KDA: %.3f" % self.kda)
        self.kdaLabel.setToolTip("%d / %d / %d" % (self.kills,self.deaths,self.assists))
        self.killsLabel.setText("Kills %d" % (self.kills))
        self.deathsLabel.setText("Deaths %d" % self.deaths)
        self.assistsLabel.setText("Assists %d" % self.assists)

    def calc(self,k,d,a):
        if d == 0 and k == 0 and a == 0:
            return 0
        return (k+a)/d