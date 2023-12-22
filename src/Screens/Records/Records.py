from PyQt6.QtCore import Qt
from PyQt6.QtGui import QResizeEvent
from PyQt6.QtWidgets import QWidget, QGridLayout, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QSizePolicy
from resources import settings, stars_pixmap, mmr_to_stars
from Screens.Records.components.RecordWidget import RecordWidget
from DbHandler import execute_query, get_id_from_timestamp

class Records(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.body = parent

        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground)      
        self.setObjectName("RecordsWidget")

        self.setMouseTracking(True)

        self.nCols = 4

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.layout.setContentsMargins(0,0,0,0)

        self.main = QWidget()
        self.main.setAttribute(Qt.WidgetAttribute.WA_StyledBackground)      
        self.main.setObjectName("MyTeamsWidget")
        self.main.layout = QGridLayout()
        self.main.layout.setSpacing(0)
        self.main.setLayout(self.main.layout)
        self.layout.addWidget(self.main)
        self.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )
        self.main.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )

        self.update()
        #self.adjustLayout(self.size())

    def redirect(self,timestamp):
        self.body.menu.set_focus("Hunts Recap")
        self.body.setCurrentWidget("Hunts Recap")
        self.body.stack.currentWidget().show_hunt(get_id_from_timestamp(timestamp))

    def update(self):
        self.clearLayout()
        self.widgets = []
        # most kills
        mostKillsData = execute_query("select timestamp, sum(h.killedbyme+h.downedbyme) as kills\
                                      from 'hunters' h\
                                      group by game_id\
                                      order by kills desc\
                                      limit 1")
        if len(mostKillsData) == 0:
            return
        mostKillsData = mostKillsData[0]
        self.widgets.append(RecordWidget(mostKillsData[1],mostKillsData[0],"Kills"))
        
        # most deaths
        mostDeathsData = execute_query("select timestamp, sum(h.killedme+h.downedme) as kills\
                                      from 'hunters' h\
                                      group by game_id\
                                      order by kills desc\
                                      limit 1")
        if len(mostDeathsData) == 0:
            mostDeathsData = [(0,0)]
        else:
            mostDeathsData = mostDeathsData[0]
        self.widgets.append(RecordWidget(mostDeathsData[1],mostDeathsData[0],"Deaths"))

        # most assists

        assistsData = execute_query("select sum(e.amount) as assists, e.timestamp\
                                    from 'entries' e where e.category = 'accolade_players_killed_assist'\
                                    group by e.timestamp order by assists desc limit 1")
        if len(assistsData) == 0:
            assistsData = [(0,0)]
        else:
            assistsData = assistsData[0]
        self.widgets.append(RecordWidget(assistsData[0],assistsData[1],"Assists"))
        # most team kills
        mostTeamKillsData = execute_query("select timestamp, sum(h.killedbyme+h.downedbyme+h.killedbyteammate+h.downedbyteammate) as kills\
                                      from 'hunters' h\
                                      group by game_id\
                                      order by kills desc\
                                      limit 1")
        if len(mostTeamKillsData) == 0:
            mostTeamKillsData = [(0,0)]
        else:
            mostTeamKillsData = mostTeamKillsData [0]
        self.widgets.append(RecordWidget(mostTeamKillsData[1],mostTeamKillsData[0],"Team Kills"))

        # most team deaths 
        mostTeamDeathsData = execute_query("select timestamp, sum(h.killedme+h.downedme+h.killedteammate+h.downedteammate) as kills\
                                      from 'hunters' h\
                                      group by game_id\
                                      order by kills desc\
                                      limit 1")
        if len(mostTeamDeathsData) == 0:
            mostTeamDeathsData = [(0,0)]
        else:
            mostTeamDeathsData = mostTeamDeathsData [0]
        self.widgets.append(RecordWidget(mostTeamDeathsData[1],mostTeamDeathsData[0],"Team Deaths"))

        # mmr gain
        mmrGain = execute_query("select\
                                lag(h.mmr) over (order by g.timestamp desc) - h.mmr as mmr_gain,\
                                g.timestamp\
                                from 'hunters' h join 'games' g on h.game_id = g.game_id where h.profileid = ? order by mmr_gain desc limit 1", settings.value("profileid",0))
        if len(mmrGain) == 0:
            mmrGain =[(0,0)] 
        else:
            mmrGain = [ x if x is not None else 0 for x in mmrGain[0] ]
        self.widgets.append(RecordWidget("%+d"%mmrGain[0],mmrGain[1],"MMR Gain"))
        #mmr loss
        mmrLoss = execute_query("select\
                                lag(h.mmr) over (order by g.timestamp desc) - h.mmr as mmr_loss,\
                                g.timestamp\
                                from 'hunters' h join 'games' g on h.game_id = g.game_id where h.profileid = ? order by mmr_loss asc limit 1 offset 1", settings.value("profileid",0))
        if len(mmrLoss) == 0:
            mmrLoss =[(0,0)] 
        else:
            mmrLoss = [ x if x is not None else 0 for x in mmrLoss[0] ]
        self.widgets.append(RecordWidget("%+d"%mmrLoss[0],mmrLoss[1],"MMR Loss"))


        # shortest hunt
        shortestHuntData = execute_query("SELECT g.timestamp, max(t.timestamp) FROM 'timestamps' t\
                                         join 'games' g on t.game_id = g.game_id\
                                         group by t.game_id order by max(t.timestamp) asc LIMIT 1")
        if len(shortestHuntData) == 0:
            shortestHuntData = [(0,0)]
        else:
            shortestHuntData = shortestHuntData[0]
        self.widgets.append(RecordWidget(shortestHuntData[1],shortestHuntData[0],"Shortest Hunt"))
        
        #longest hunt
        longestHuntData = execute_query("SELECT g.timestamp, max(t.timestamp) FROM 'timestamps' t\
                                         join 'games' g on t.game_id = g.game_id\
                                         group by t.game_id order by max(t.timestamp) desc LIMIT 1")
        if len(longestHuntData) == 0:
            longestHuntData = [(0,0)]
        else:
            longestHuntData = longestHuntData[0]
        self.widgets.append(RecordWidget(longestHuntData[1],longestHuntData[0],"Longest Hunt"))
        
        #most mobs
        mobsData = execute_query("select e.timestamp, sum(e.amount) as kills from 'entries' e\
                                    where (category like 'accolade_monsters_killed' or descriptorName like 'kill horse')\
                                    group by e.game_id order by kills desc limit 1")
        if len(mobsData) == 0:
            mobsData = [(0,0)]
        else:
            mobsData = mobsData[0]
        self.widgets.append(RecordWidget(mobsData[1],mobsData[0],"Mobs Killed"))
        
        #most money
        moneyData = execute_query("select a.timestamp, sum(a.bounty) as bounty from 'accolades' a\
                                  group by game_id order by bounty desc limit 1")
        if len(moneyData) == 0:
            moneyData = [(0,0)]
        else:
            moneyData = moneyData[0]
        self.widgets.append(RecordWidget("$%d"%moneyData[1],moneyData[0],"Hunt Dollars"))

        #most xp 
        xpData = execute_query("select a.timestamp, sum(a.xp) as xp from 'accolades' a\
                                  group by game_id order by xp desc limit 1")
        if len(xpData) == 0:
            xpData = [(0,0)]
        else:
            xpData = xpData[0]
        self.widgets.append(RecordWidget(xpData[1],xpData[0],"XP"))

        for i in range(len(self.widgets)):
            widget = self.widgets[i]
            self.main.layout.addWidget(widget,i//self.nCols,i%self.nCols)
        self.main.layout.setRowStretch(self.main.layout.rowCount(),1)

    def clearLayout(self):
        for i in reversed(range(self.main.layout.count())): 
            w = self.main.layout.itemAt(i).widget()
            if w != None:
                w.setParent(None)

    def resizeEvent(self, a0: QResizeEvent) -> None:
        return super().resizeEvent(a0)