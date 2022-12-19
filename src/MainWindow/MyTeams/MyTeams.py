from PyQt6.QtWidgets import QWidget, QGridLayout, QVBoxLayout, QScrollArea, QPushButton
from PyQt6.QtGui import QIcon
from DbHandler import *
from MainWindow.Chart.ScatterItem import ScatterItem
import hashlib
import pyqtgraph


colors = ["#ff0000cc","#00ffffcc","#ffff00cc"]

class MyTeams(QScrollArea):
    def __init__(self, parent):
        super().__init__(parent)
        self.setWidgetResizable(True)
        self.main = QWidget()
        self.main.layout = QVBoxLayout()
        self.main.setLayout(self.main.layout)
        self.setWidget(self.main)
        self.update()

    def update(self):
        print('myteams.update')
        clearLayout(self.main.layout)
        hunts = GetHunts()
        teams = []
        for hunt in hunts:
            team = GetTeamMembers(hunt['timestamp'])
            if len(team) > 0:
                teams.append(team)

        count = {}
        for team in teams:
            team_id = hashlib.md5(str(team['pid']).encode('utf-8')).hexdigest()
            team['team_id'] = team_id
            if team_id not in count:
                count[team_id] = {'pid':team['pid'],'count':0,'games':[]}
            count[team_id]['count'] += 1
            count[team_id]['games'].append(team['timestamp'])
        i = 0
        for t in sorted(count,key=lambda t : count[t]['count'],reverse=True):
            if count[t]['count'] > 1:
                self.main.layout.addWidget(self.TeamWidget(count[t]))
            i += 1
            if i > 10:
                break
        self.main.layout.addStretch()
        

    def TeamWidget(self,team):
        w = QWidget()
        w.layout = QGridLayout()
        w.setLayout(w.layout)
        names = [GetNameByProfileId(pid) for pid in team['pid']]
        if len(team['pid']) == 1:
            w.layout.addWidget(QLabel("%s (solo)" % names[0]),0,0)
        else:
            w.layout.addWidget(QLabel("%s" % ", ".join(names)),0,0)
        w.layout.addWidget(QLabel("Hunted together %d times" % team['count']),1,0)

        w.setObjectName("HuntWidget")
        plot = self.TeamMmrChart(team)
        w.layout.addWidget(plot,2,0)
        return w

    def TeamMmrChart(self,team):
        plotWindow = pyqtgraph.GraphicsLayoutWidget()
        plot = plotWindow.addPlot(0,0)
        plot.getViewBox().installEventFilter(plotWindow)
        vb = pyqtgraph.ViewBox()
        legend = pyqtgraph.LegendItem(colCount=2)
        legend.setParentItem(vb)
        legend.anchor((0,0),(0,0))
        plotWindow.addItem(vb,1,0)

        teamMmrs = {}
        teamData = []
        playersData = {pid : [] for pid in team['pid']}
        playerMmrs = {pid : {} for pid in team['pid']}
        i = 0
        j = 0
        for ts in team['games']:
            teamMmr = execute_query("select mmr from 'teams' where timestamp = %s and ownteam = 'true'" % ts)
            if len(teamMmr) > 0:
                teamMmrs[ts] = teamMmr[0][0]
                teamData.append({'x':i,'y':teamMmr[0][0], 'data':ts})
                for pid in team['pid']: 
                    mmr = execute_query("select mmr from 'hunters' where profileid = %s and timestamp = %s" % (pid, ts))
                    if len(mmr) > 0:
                        playersData[pid].append({'x':i,'y':mmr[0][0],'data':ts})
                        playerMmrs[pid][ts] = mmr[0][0]
            i += 1
        teamPoints = ScatterItem(teamData,brush="#00ff00cc",pen=None,name="Team MMR",parent=self)
        playerPoints = []
        i = 0
        for pid in playersData:
            playerPoints.append(ScatterItem(playersData[pid],pen=None,brush=colors[i],name=GetNameByProfileId(pid),parent=self))
            i += 1
        teamLine = pyqtgraph.PlotDataItem(teamData,pen="#ffffff66")
        playerLines = [pyqtgraph.PlotDataItem(playersData[pid],pen="#ffffff66") for pid in playersData]

        plot.addItem(teamPoints)
        plot.addItem(teamLine)
        for pts in playerPoints:
            plot.addItem(pts)
        for line in playerLines:
            plot.addItem(line)
        plotWindow.setFixedHeight(int(plot.size().width()/2))
        legend.addItem(teamPoints,name=teamPoints.opts['name'])
        for player in playerPoints:
            legend.addItem(player,name=player.opts['name'])
        legend.getViewBox().setMaximumHeight(legend.boundingRect().height())
        plot.showGrid(x=True,y=True,alpha=0.4)
        return plotWindow

def toggle(widget : QWidget, btn : QPushButton):
    if widget.isVisible():
        widget.setHidden(True)
        btn.setIcon(QIcon(resource_path("assets/icons/plus.png")))
    else:
        widget.setVisible(True)
        btn.setIcon(QIcon(resource_path("assets/icons/minus.png")))