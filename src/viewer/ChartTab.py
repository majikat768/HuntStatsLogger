from PyQt6.QtWidgets import QComboBox,QSlider,QLabel,QGroupBox,QGridLayout, QGraphicsSceneWheelEvent,QMainWindow,QWidget,QVBoxLayout
from PyQt6.QtCore import Qt,QEvent,QSizeF,QSize,QPoint
import pyqtgraph
from resources import *
from util.Popup import Popup
from viewer import DbHandler

def lerp(a,b,x):
    return a + x * (b-a)

class ChartTab(QGroupBox):
    def __init__(self, parent): 
        super().__init__(parent)
        self.layout = QGridLayout()
        self.setLayout(self.layout)

        self.plotWindow = pyqtgraph.GraphicsLayoutWidget()

        self.dataSelect = QComboBox()
        self.dataSelect.addItems(["MMR","KDA"])
        self.dataSelect.currentTextChanged.connect(self.update)

        self.popup = None

        self.plot = self.plotWindow.addPlot(0,0)

        vb = pyqtgraph.ViewBox()
        self.plotWindow.addItem(vb,1,0)
        self.legend = pyqtgraph.LegendItem()
        self.legend.setParentItem(vb)
        self.legend.anchor((0,0),(0,0))

        self.plot.getViewBox().installEventFilter(self)
        self.xZoom = QSlider(Qt.Orientation.Horizontal)
        self.xZoom.setRange(0,90)
        self.xZoom.valueChanged.connect(self.zoom)

        self.xZoom.setValue(20)

        self.layout.addWidget(self.dataSelect,0,0,1,4)
        self.layout.addWidget(self.plotWindow,1,0,3,3)
        self.layout.addWidget(self.xZoom,4,1,1,1)
        self.layout.addWidget(QLabel('<center>+</center>'),4,2,1,1)
        self.layout.addWidget(QLabel('<center>-</center>'),4,0,1,1)
        self.layout.addWidget(QLabel(
            'Showing last 20 games.\nUse mousewheel to scale y axis, and slider to scale x axis.\nDrag with mouse to pan across.'
        ),5,0,1,3)

        self.update()

    def zoom(self):
        xLimits = self.plot.getViewBox()._effectiveLimits()[0]

        xMid = (xLimits[0] + xLimits[1])/2

        xZoom = self.xZoom.value()/100

        xRange = (xLimits[1] - xLimits[0]) * (1-xZoom)

        xView = self.plot.getViewBox().viewRange()[0]
        xMid = (xView[1] + xView[0]) / 2
        self.plot.setXRange(xMid - xRange/2, xMid + xRange/2)

    def update(self):
        self.legend.clear()
        if self.dataSelect.currentText() == 'MMR':
            self.initMmrGraph()
        elif self.dataSelect.currentText() == 'KDA':
            self.initKdaGraph()
        self.legend.getViewBox().setMaximumHeight(self.legend.boundingRect().height())

    def calcKda(self,kills,deaths,assists,hunts,gameType=-1):
        allKills = {}
        for k in kills:
            timestamp = k[0]
            if timestamp not in allKills:
                allKills[timestamp] = 0
            allKills[timestamp] += int(k[1]) + int(k[2])

        allDeaths = {}
        for d in deaths:
            timestamp = d[0]
            if timestamp not in allDeaths:
                allDeaths[timestamp] = 0
            allDeaths[timestamp] += int(d[1]) + int(d[2])

        allAssists = {}
        for a in assists:
            timestamp = a[0]
            if timestamp not in allAssists:
                allAssists[timestamp] = 0
            allAssists[timestamp] += int(a[1])

        kdas = {'x':[],'y':[]}

        runningKills = 0
        runningDeaths = 0
        runningAssists = 0

        i = 0
        for h in hunts:
            if gameType < 0 or h[1] == gameType:
                if h[0] in allKills:
                    runningKills += allKills[h[0]]
                if h[0] in allDeaths:
                    runningDeaths += allDeaths[h[0]]
                if h[0] in allAssists:
                    runningAssists += allAssists[h[0]]

                kda = (runningKills+runningAssists) / (max(1,runningDeaths))
                kdas['x'].append(i)
                kdas['y'].append(kda)
            i += 1
        return kdas


    def initKdaGraph(self):
        kills = DbHandler.execute_query("select timestamp, downedbyme, killedbyme from hunter where downedbyme > 0 or killedbyme > 0")
        deaths = DbHandler.execute_query("select timestamp, downedme, killedme from hunter where downedme > 0 or killedme > 0")
        assists = DbHandler.execute_query("select timestamp, amount from 'entry' where category is 'accolade_players_killed_assist'")
        hunts = DbHandler.execute_query("select timestamp,MissionBagIsQuickPlay from 'game'")

        kdas = self.calcKda(kills,deaths,assists,hunts)
        qpKdas = self.calcKda(kills,deaths,assists,hunts,gameType=1)
        bhKdas = self.calcKda(kills,deaths,assists,hunts,gameType=0)
        kdaP = pyqtgraph.PlotDataItem(kdas['x'],kdas['y'],size=12, connect="all", hoverable=True, hoverSize=16, pen='#ffffff44',symbol='t',symbolPen=None,symbolBrush='#88ff00',name="Overall")
        qpKdaP = pyqtgraph.PlotDataItem(qpKdas['x'],qpKdas['y'],size=12,hoverable=True,hoverSize=16,pen='#ffffff44',symbol='t1',symbolPen=None,symbolBrush='#00ffff', name="Quick Play")
        bhKdaP = pyqtgraph.PlotDataItem(bhKdas['x'],bhKdas['y'],size=12,hoverable=True,hoverSize=16,pen='#ffffff44',symbol='t1',symbolPen=None,symbolBrush='#ff0000', name="Bounty")

        kdaP.sigPointsClicked.connect(self.mouseOver)
        qpKdaP.sigPointsClicked.connect(self.mouseOver)
        bhKdaP.sigPointsClicked.connect(self.mouseOver)

        self.plot.addItem(kdaP)
        self.plot.addItem(qpKdaP)
        self.plot.addItem(bhKdaP)

        self.legend.addItem(kdaP, name='Overall')
        self.legend.addItem(bhKdaP, name='Bounty')
        self.legend.addItem(qpKdaP, name='Quick Play')

        self.plot.showGrid(x = True, y = True, alpha = 0.4)
        self.plot.getViewBox().setLimits(xMin=0,xMax=len(kdas['x']),yMin=0,yMax=max(kdas['y'])*4)
        self.plot.setXRange(len(kdas['x'])-20,len(kdas['x']))
        self.plot.setYRange(0,max(kdas['y']))
        self.xZoom.setValue(int(100-(20/len(kdas['x'])*100)))
        self.plot.setLabel('left','KDA')
        self.plot.setLabel('bottom','Hunts')

    def initMmrGraph(self):
        mmrs = DbHandler.execute_query("select timestamp,mmr from 'hunter' where blood_line_name is '%s'" % settings.value('steam_name',''))
        gameTypes = DbHandler.execute_query("select timestamp,MissionBagIsQuickPlay from 'game'")

        if mmrs is None or gameTypes is None:   return

        mmrs = {i[0]:i[1] for i in mmrs}
        gameTypes = {i[0]:i[1] for i in gameTypes}

        points = []
        qpM = []
        bhM = []
        i = 0
        for t in mmrs:
            if t is None:   continue
            if t not in gameTypes:  continue
            mmr = mmrs[t]
            qp = gameTypes[t]
            points.append({
                'x':i,'y':mmr
            })
            if qp:
                qpM.append({'x':i,'y':mmr})
            else:
                bhM.append({'x':i,'y':mmr})
            i += 1
        if len(points) == 0:
            return
        
        dataLine = pyqtgraph.PlotDataItem(points)
        qpDataItem = pyqtgraph.ScatterPlotItem(qpM,size=12,hoverable=True,hoverSize=16,symbol='o',pen="#000000",brush="#00ffff",name="Quick Play",tip=None)
        bhDataItem = pyqtgraph.ScatterPlotItem(bhM,size=12,hoverable=True,hoverSize=16,symbol='o',pen="#000000",brush="#ff0000",name="Bounty",tip=None)

        qpDataItem.sigClicked.connect(self.mouseOver)
        bhDataItem.sigClicked.connect(self.mouseOver)

        self.plot.addItem(dataLine)
        self.plot.addItem(qpDataItem)
        self.plot.addItem(bhDataItem)

        self.legend.addItem(bhDataItem,name=bhDataItem.opts['name'])
        self.legend.addItem(qpDataItem,name=qpDataItem.opts['name'])
        self.plot.showGrid(x = True, y = True, alpha = 0.1)

        self.plot.getViewBox().setLimits(xMin=0,xMax=len(points),yMin=0,yMax=5000)
        for mmr in [0,2000,2300,2600,2750,3000,5000]:
            line = pyqtgraph.InfiniteLine(mmr,pen="#ffaaaa88",angle=0)
            self.plot.addItem(line)
        self.plot.setXRange(len(points)-20,len(points))
        self.xZoom.setValue(int(100-(20/len(points)*100)))
        self.plot.setYRange(min(points, key = lambda p : p['y'])['y']-100,max(points, key = lambda p : p['y'])['y']+100)
        self.plot.setLabel('left','MMR')
        self.plot.setLabel('bottom','Hunts')

    def mouseOver(self,obj,pts,e):
        if len(pts) > 0:
            mmr = pts[0].pos().y()
            info = QWidget()
            info.layout = QVBoxLayout()
            info.setLayout(info.layout)
            info.layout.addWidget(QLabel(str(mmr)))
            self.popup = Popup(info,e.screenPos())
            self.popup.keepAlive(True) 
            self.popup.show()

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.GraphicsSceneWheel:
            #print(obj,event)
            yLimits = self.plot.getViewBox()._effectiveLimits()[1]
            yLimRange = yLimits[1] - yLimits[0]
            yView = self.plot.getViewBox().viewRange()[1]
            yViewRange = yView[1] - yView[0]

            if event.delta() > 0:
                if yViewRange  < yLimRange/25:
                    return True
                diff = [
                    yView[0]+(yViewRange*0.15),
                    yView[1]-(yViewRange*0.15)
                ]
                self.plot.setYRange(diff[0],diff[1])
                return True
            elif event.delta() < 0:
                if yViewRange > yLimRange/2:
                    return True
                diff = [
                    yView[0]-(yViewRange*0.15),
                    yView[1]+(yViewRange*0.15)
                ]
                self.plot.setYRange(diff[0],diff[1])
                return True
        return super().eventFilter(obj, event)