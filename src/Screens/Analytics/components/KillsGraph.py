from PyQt6.QtGui import QColor, QFont, QPen
from PyQt6.QtCore import QRectF
import pyqtgraph
from DbHandler import execute_query
from Screens.Analytics.components.PlotItem import PlotItem

class KillsGraph(PlotItem):
    def __init__(self, parent=None, name=None, labels=None, title=None, viewBox=None, axisItems=None, enableMenu=True, **kargs):
        super().__init__(parent, name, labels, title, viewBox, axisItems, enableMenu, **kargs)
        self.legend = pyqtgraph.LegendItem(colCount=2)
        self.layout.setContentsMargins(0,0,0,0)
        self.ymax = 0
        self.setFixedHeight(200)

        self.setTitle("Kills Per Hunt")

        self.font = QFont()
        self.font.setWeight(600)
        self.font.setPixelSize(16)

        self.setKillsData()

    def setKillsData(self):
        self.clear()
        vals = execute_query("select sum(h.killedbyme+h.downedbyme) from 'hunters' h group by game_id")
        
        data = {}
        for v in vals:
            amt = v[0]
            if str(amt) not in data:
                data[str(amt)] = 0
            data[str(amt)] += 1

        ticks = []
        self.ymax = 0
        i = 0
        for key in sorted(data):
            bar = pyqtgraph.BarGraphItem(
                x = 15*i,
                height = data[key],
                width = 10
            )
            self.addItem(bar)
            ticks.append((int(i)*15,str(key)))
            if key != '0':
                self.ymax = max(self.ymax,data[key])
                label = pyqtgraph.TextItem(str(data[key]),anchor=(0.5,1),color=(223,223,223))
                label.setPos(15*i,data[key])
            else:
                label = pyqtgraph.TextItem(str(data[key]),anchor=(0.5,2),color=(22,22,22))
                label.setPos(15*i,0)
            label.setFont(self.font)
            self.addItem(label)
            i += 1
        ticks = [ticks]

        self.getAxis("bottom").setTicks(ticks)
        self.getAxis("bottom").setLabel("Kills")
        self.getAxis("left").setLabel("Hunts")

        self.setYRange(0,self.ymax*1.2)
        self.setXRange(-10,14*i)
        self.setLimits(yMin=0,yMax=self.ymax*1.2,xMin = -10, xMax = 14*i)

    def update(self):
        self.setKillsData()

class KillsWindow(pyqtgraph.GraphicsLayoutWidget):
    def __init__(self, parent=None, show=False, size=None, title=None, **kargs):
        super().__init__(parent, show, size, title, **kargs)
        self.killsGraph  = KillsGraph()
        self.addItem(self.killsGraph,0,0)
        self.setFixedHeight(200)

    def update(self):
        self.killsGraph.update()