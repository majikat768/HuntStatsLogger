from DbHandler import execute_query, GetKillsByMatch
import pyqtgraph
from resources import max
from MainWindow.Chart.Bars import Bars
from PyQt6.QtGui import QColor, QBrush,QPen


class KillsPerHunt():
    def __init__(self):
        self.width = 5
        self.update()
        self.bountyLegendItem = pyqtgraph.ScatterPlotItem([],symbol='s',size=16,brush=QBrush(QColor("#c8ff0000")))
        self.qpLegendItem = pyqtgraph.ScatterPlotItem([],symbol='s',size=16,brush=QBrush(QColor("#c800ffff")))

    def update(self):
        data = {}
        kData = GetKillsByMatch()

        for ts in kData.keys():
            n = kData[ts]['kills']
            if n not in data.keys():
                data[n] = {"bounty":0,"qp":0}
            if kData[ts]['isQp'].lower() == "true":
                data[n]['qp'] += 1
            elif kData[ts]['isQp'].lower() == "false":
                data[n]['bounty'] += 1

        x0 = []
        self.ticks = [[]]

        for i in range(len(data.keys())):
            x0.append(self.width+(i)*3*self.width)
            x0.append(2*self.width+(i)*3*self.width)
        x1 = [i + self.width for i in x0]
        height = []
        self.maxHeight = 0
        for i in range(len(data.keys())):
            height.append(data[i]['bounty'])
            height.append(data[i]['qp'])
            self.maxHeight = max(self.maxHeight,max(data[i]['bounty'],data[i]['qp']))
        brushes = [QColor("#c8ff0000"),QColor("#c800ffff")]*len(data.keys())
        self.bars = Bars(x0=x0,x1=x1,height=height,brushes=brushes)

        for i in range(len(x0)//2):
            self.ticks[0].append(((i+1)*self.width*3-self.width,str(i)))
        self.bars.hoverable = False

'''
{1: {'bounty': 51, 'qp': 38}, 0: {'bounty': 139, 'qp': 79}, 2: {'bounty': 14, 'qp': 12}, 4: {'bounty': 3, 'qp': 2}, 3: {'bounty': 8, 'qp': 1}}
'''