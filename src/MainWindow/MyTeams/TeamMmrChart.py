import pyqtgraph
from PyQt6.QtCore import QEvent, Qt
from DbHandler import execute_query, GetNameByProfileId
from MainWindow.Chart.ScatterItem import ScatterItem

colors = ["#ff0000cc","#00ffffcc","#ffff00cc"]

class TeamMmrChart(pyqtgraph.GraphicsLayoutWidget):
    def __init__(self,team) -> None:
        super().__init__()
        self.plot = self.addPlot(0,0)
        self.plot.getViewBox().installEventFilter(self)
        vb = pyqtgraph.ViewBox()
        legend = pyqtgraph.LegendItem(colCount=2)
        legend.setParentItem(vb)
        legend.anchor((0,0),(0,0))
        self.addItem(vb,1,0)

        self.bestMmrs = {pid : 0 for pid in team['pid']}
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
        self.bestMmrs = {pid : max(playerMmrs[pid].values()) for pid in team['pid']}
        teamPoints = ScatterItem(teamData,brush="#00ff00cc",pen=None,name="Team MMR",parent=self)
        playerPoints = []
        i = 0
        for pid in playersData:
            playerPoints.append(ScatterItem(playersData[pid],pen=None,brush=colors[i],name=GetNameByProfileId(pid),parent=self))
            i += 1
        teamLine = pyqtgraph.PlotDataItem(teamData,pen="#ffffff66")
        playerLines = [pyqtgraph.PlotDataItem(playersData[pid],pen="#ffffff66") for pid in playersData]

        self.plot.addItem(teamPoints)
        self.plot.addItem(teamLine)
        for pts in playerPoints:
            self.plot.addItem(pts)
        for line in playerLines:
            self.plot.addItem(line)
        self.setFixedHeight(int(self.plot.size().width()/2))
        legend.addItem(teamPoints,name=teamPoints.opts['name'])
        for player in playerPoints:
            legend.addItem(player,name=player.opts['name'])
        legend.getViewBox().setMaximumHeight(legend.boundingRect().height())
        self.plot.showGrid(x=True,y=True,alpha=0.4)
        self.plot.setXRange(
            max(-1, len(teamLine.xData)-20), len(teamLine.xData)+2)
        self.plot.setLimits(xMin=0, yMin=0, yMax=6000,
                            xMax=len(teamLine.xData)+2)

    def eventFilter(self, obj, event):
            if event.type() == QEvent.Type.GraphicsSceneWheel:
                if Qt.KeyboardModifier.ShiftModifier in event.modifiers():
                    self.plot.setMouseEnabled(y=False, x=True)
                else:
                    self.plot.setMouseEnabled(y=True, x=False)
            elif event.type() == QEvent.Type.GrabMouse:
                self.plot.setMouseEnabled(x=True)
            return super().eventFilter(obj, event)

