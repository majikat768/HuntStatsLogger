from PyQt6.QtGui import QColor, QFont, QPen
from PyQt6.QtCore import QRectF
import pyqtgraph
from DbHandler import execute_query
from Screens.Analytics.components.PlotItem import PlotItem

class SurvivalGraph(PlotItem):
    def __init__(self, parent=None, name=None, labels=None, title=None, viewBox=None, axisItems=None, enableMenu=True, **kargs):
        super().__init__(parent, name, labels, title, viewBox, axisItems, enableMenu, **kargs)
        self.legend = pyqtgraph.LegendItem(colCount=2)
        self.ymax = 0

        self.font = QFont()
        self.font.setWeight(800)
        self.font.setPixelSize(16)
        self.data = {}

        self.setSurvivalData()
        self.setTitle("Lived/Died %")
        self.setFixedHeight(200)

    def setSurvivalData(self):
        self.clear()
        survival = execute_query("select sum(case when g.MissionBagIsHunterDead = 'false' then 1 else 0 end) as survived,\
                             count(*) as total from 'games' g")
        if(survival[0][0] == None):
            survival = [0,0]
        else:
            survival = survival[0]
        survivalRate = survival[0] / max(1,survival[1])
        death = survival[1] - survival[0]
        deathRate = 1.0 - survivalRate

        x = [15,30]
        width = 10

        surviveBar = pyqtgraph.BarGraphItem(
            x = x[0],
            height = survival[0],
            width = width,
            brush = QColor("#798c5d")
        )
        deathBar = pyqtgraph.BarGraphItem(
            x = x[1],
            height = death,
            width = width,
            brush = QColor("#51181b")
        )

        survivalLabel = pyqtgraph.TextItem("%.1f%%" % (survivalRate*100.0),anchor=(0.5,1),color=(233,233,233))
        survivalLabel.setPos(x[0],survivalRate*100)
        survivalLabel.setFont(self.font)
        deathLabel = pyqtgraph.TextItem("%.1f%%" % (deathRate*100.0),anchor=(0.5,1),color=(233,233,233))
        deathLabel.setPos(x[1],deathRate*100)
        deathLabel.setFont(self.font)
        deathLabel.setFont(self.font)

        self.addItem(surviveBar)
        self.addItem(deathBar)
        self.addItem(survivalLabel)
        self.addItem(deathLabel)

        self.setLimits(yMin=0,yMax=max(survival[0],death)*1.2,xMin=x[0]-10,xMax=x[1]+10)
        self.setXRange(x[0]-10,x[1]+10)
        self.setYRange(0,max(survival[0],death)*1.2)
        self.getAxis("bottom").setTicks([
            [ ( x[0], "Extracted"), (x[1], "Died") ]
        ])
        self.getAxis("left").setLabel("Hunts")
        self.getAxis("bottom").setLabel(" ")

    def update(self):
        self.setSurvivalData()

class SurvivalWindow(pyqtgraph.GraphicsLayoutWidget):
    def __init__(self, parent=None, show=False, size=None, title=None, **kargs):
        super().__init__(parent, show, size, title, **kargs)
        self.survivalGraph  = SurvivalGraph()
        self.addItem(self.survivalGraph,0,0)
        self.setFixedHeight(220)

    def update(self):
        self.survivalGraph.update()