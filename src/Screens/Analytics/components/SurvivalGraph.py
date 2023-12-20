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

    def setSurvivalData(self):
        self.clear()
        survival = execute_query("select sum(case when g.MissionBagIsHunterDead = 'false' then 1 else 0 end) as survived,\
                             count(*) as total from 'games' g where g.MissionBagIsQuickPlay = 'false'")
        if(survival[0][0] == None):
            survival = [0,0]
        else:
            survival = survival[0]
        survivalRate = survival[0] / max(1,survival[1])
        deathRate = 1.0 - survivalRate
        wins = execute_query("select count(a.category) from 'accolades' a where a.category like 'accolade_extract\_%' escape '\\'")
        if wins[0] == None:
            wins = 0
        else:
            wins = wins[0][0]
        winRate = wins / max(1,survival[1])
        lossRate = (survival[0] - wins) / max(1,survival[1])


        x = [0,25,50,75]
        width = 15

        surviveBar = pyqtgraph.BarGraphItem(
            x = x[0],
            height = survivalRate*100,
            width = width,
            brush = QColor("#798c5d")
        )
        deathBar = pyqtgraph.BarGraphItem(
            x = x[3],
            height = deathRate*100,
            width = width,
            brush = QColor("#51181b")
        )
        winBar = pyqtgraph.BarGraphItem(
            x = x[1],
            height = winRate*100,
            width=width,
            brush=QColor("#c3cfc7")
        )
        lossBar = pyqtgraph.BarGraphItem(
            x = x[2],
            height = lossRate*100,
            width=width,
            brush=QColor("#c3cfc7")
        )

        survivalLabel = pyqtgraph.TextItem("%.1f%%" % (survivalRate*100.0),anchor=(0.5,1),color=(233,233,233))
        survivalLabel.setPos(x[0],survivalRate*100)
        survivalLabel.setFont(self.font)
        deathLabel = pyqtgraph.TextItem("%.1f%%" % (deathRate*100.0),anchor=(0.5,1),color=(233,233,233))
        deathLabel.setPos(x[3],deathRate*100)
        deathLabel.setFont(self.font)
        deathLabel.setFont(self.font)
        winLabel  = pyqtgraph.TextItem("%.1f%%" % (winRate*100.0),anchor=(0.5,1),color=(233,233,233))
        winLabel.setPos(x[1],winRate*100)
        winLabel.setFont(self.font)
        lossLabel  = pyqtgraph.TextItem("%.1f%%" % (lossRate*100.0),anchor=(0.5,1),color=(233,233,233))
        lossLabel.setPos(x[2],lossRate*100)
        lossLabel.setFont(self.font)

        self.addItem(surviveBar)
        self.addItem(deathBar)
        self.addItem(survivalLabel)
        self.addItem(deathLabel)
        self.addItem(winBar)
        self.addItem(winLabel)
        self.addItem(lossBar)
        self.addItem(lossLabel)

        self.setLimits(yMin=0,yMax=max(survivalRate*100,deathRate*100)+15,xMin=x[0]-10,xMax=x[3]+10)
        self.setXRange(x[0]-10,x[3]+10)
        self.setYRange(0,max(survivalRate*100,deathRate*100)+15)
        self.getAxis("bottom").setTicks([
            [ ( x[0], "Extracted"), (x[1], "Ext Bounty"),(x[2],"Ext no Bounty"), (x[3], "Died" ) ]
        ])
        self.getAxis("left").setLabel("Hunts")

    def update(self):
        self.setSurvivalData()

class SurvivalWindow(pyqtgraph.GraphicsLayoutWidget):
    def __init__(self, parent=None, show=False, size=None, title=None, **kargs):
        super().__init__(parent, show, size, title, **kargs)
        self.survivalGraph  = SurvivalGraph()
        self.addItem(self.survivalGraph,0,0)

    def update(self):
        self.survivalGraph.update()