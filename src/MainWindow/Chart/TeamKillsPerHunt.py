from DbHandler import execute_query, GetTeamKillsByMatch
import pyqtgraph
from resources import max
from MainWindow.Chart.Bars import Bars
from PyQt6.QtGui import QColor, QBrush,QPen


class TeamKillsPerHunt():
    def __init__(self):
        self.width = 5
        self.update()
        self.legendItem = pyqtgraph.ScatterPlotItem([],symbol='s',size=16,brush=QBrush(QColor("#c8ff0000")))

    def update(self):
        data = {}
        kData = GetTeamKillsByMatch()
        totalHunts = execute_query("select count(*) from 'games' where MissionBagIsQuickPlay = 'false'")
        totalHunts = 0 if len(totalHunts) == 0 else totalHunts[0][0]
        x0 = []
        self.ticks = [[]]

        for ts in kData.keys():
            n = kData[ts]
            if n not in data.keys():
                data[n] = 0
            data[n] += 1
        for i in data.keys():
            x0.append(self.width+(i*2)*self.width)
        x1 = [i + self.width for i in x0]
        height = []
        self.maxHeight = 0
        for i in data.keys():
            height.append(data[i])
            self.maxHeight = max(self.maxHeight,data[i])
        
        brushes = [QColor("#c8ff0000")]*len(data.keys())

        for i in range(len(data.keys())):
            self.ticks[0].append((self.width*1.5 + i*self.width*2,str(i)))
        self.line = pyqtgraph.InfiniteLine(
            pos=totalHunts, angle=0, pen=pyqtgraph.mkPen("#ff000088", width=2))
        self.line.label = pyqtgraph.InfLineLabel(self.line, text="%d Total Bounty Hunts" % (
            totalHunts), movable=False, position=0.7,anchors=[(0,0),(0,0)])
        self.bars = Bars(x0=x0,x1=x1,height=height,brushes=brushes)
