from PyQt6.QtWidgets import QComboBox,QSlider,QLabel,QGroupBox,QGridLayout
from PyQt6.QtCore import Qt,QEvent
import pyqtgraph
from resources import *
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

        self.legend = pyqtgraph.LegendItem()
        self.plot = self.plotWindow.addPlot(0,0)

        vb = self.plotWindow.addViewBox(1,0)
        self.legend = pyqtgraph.LegendItem()
        self.legend.setParentItem(vb)
        self.legend.anchor((0,0),(0,0))

        self.plot.getViewBox().installEventFilter(self)

        self.xZoom = QSlider(Qt.Orientation.Horizontal)
        self.xZoom.setRange(0,90)
        self.xZoom.valueChanged.connect(self.zoom)

        self.yZoom = QSlider(Qt.Orientation.Vertical)
        self.yZoom.setRange(0,90)
        self.yZoom.valueChanged.connect(self.zoom)

        self.xZoom.setValue(20)
        self.yZoom.setValue(90)

        self.layout.addWidget(self.dataSelect,0,0,1,4)
        self.layout.addWidget(self.plotWindow,1,1,3,3)
        self.layout.addWidget(self.xZoom,4,2,1,1)
        self.layout.addWidget(QLabel('<center>+</center>'),4,3,1,1)
        self.layout.addWidget(QLabel('<center>-</center>'),4,1,1,1)
        self.layout.addWidget(self.yZoom,2,0,1,1)
        self.layout.addWidget(QLabel('<center>+</center>'),1,0,1,1)
        self.layout.addWidget(QLabel('<center>-</center>'),3,0,1,1)
        self.layout.addWidget(QLabel(
            'Showing last 50 games.\nUse x and y sliders to zoom out.\nDrag with mouse to pan across.'
        ),5,0,1,3)
        self.plot.setMouseEnabled(x=True,y=True)

        self.update()

    def zoom(self):
        #xRange = self.plot.getViewBox().viewRange()[0]
        #yRange = self.plot.getViewBox().viewRange()[1]
        xLimits = self.plot.getViewBox()._effectiveLimits()[0]
        yLimits = self.plot.getViewBox()._effectiveLimits()[1]

        xMid = (xLimits[0] + xLimits[1])/2
        yMid = (yLimits[0] + yLimits[1])/2

        xZoom = self.xZoom.value()/100
        yZoom = self.yZoom.value()/100

        xRange = (xLimits[1] - xLimits[0]) * (1-xZoom)
        yRange = (yLimits[1] - yLimits[0]) * (1-yZoom)

        xView = self.plot.getViewBox().viewRange()[0]
        yView = self.plot.getViewBox().viewRange()[1]
        xMid = (xView[1] + xView[0]) / 2
        yMid = (yView[1] + yView[0]) / 2
        self.plot.setXRange(xMid - xRange/2, xMid + xRange/2)
        self.plot.setYRange(yMid - yRange/2, yMid + yRange/2)

    def update(self):
        #self.plotWindow.clear()
        self.plot.clear()
        self.legend.clear()
        #vb = self.plotWindow.addViewBox(1,0)
        #self.legend = pyqtgraph.LegendItem()
        #self.legend.setParentItem(vb)
        #self.legend.anchor((0,0),(0,0))
        if self.dataSelect.currentText() == 'MMR':
            self.initMmrGraph()
        elif self.dataSelect.currentText() == 'KDA':
            self.initKdaGraph()
        self.legend.getViewBox().setMaximumHeight(self.legend.boundingRect().height())

    def calcKda(self,kills,deaths,assists,hunts,gameType='all'):
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
            if gameType == 'all' or h[1] == gameType:
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
        qpKdas = self.calcKda(kills,deaths,assists,hunts,1)
        bhKdas = self.calcKda(kills,deaths,assists,hunts,0)
        
        #self.plot = self.plotWindow.addPlot(0,0)
        kdaP = self.plot.plot(kdas['x'],kdas['y'],pen='#ffffff44',symbol='t',symbolPen=None,symbolBrush='#ff0000')
        qpKdaP = self.plot.plot(qpKdas['x'],qpKdas['y'],pen='#ffffff44',symbol='t1',symbolPen=None,symbolBrush='#ffff00')
        bhKdaP = self.plot.plot(bhKdas['x'],bhKdas['y'],pen='#ffffff44',symbol='t1',symbolPen=None,symbolBrush='#0088ff')
        self.legend.addItem(kdaP, name='KDA')
        self.legend.addItem(bhKdaP, name='Bounty KDA')
        self.legend.addItem(qpKdaP, name='QP KDA')

        self.plot.showGrid(x = True, y = True, alpha = 0.4)
        self.plot.getViewBox().setLimits(xMin=0,xMax=len(kdas['x']),yMin=0,yMax=max(kdas['y'])*4)
        self.plot.setXRange(len(kdas['x'])-50,len(kdas['x']))
        self.plot.setYRange(0,max(kdas['y'])*2)
        self.xZoom.setValue(100-(50/len(kdas['x'])*100))
        self.yZoom.setValue(100-(max(kdas['y'])+0.5)/(max(kdas['y'])*2)*100)
        self.plot.setLabel('left','KDA')
        self.plot.setLabel('bottom','Hunts')

    def initMmrGraph(self):
        mmrs = DbHandler.execute_query("select timestamp,mmr from 'hunter' where blood_line_name is '%s'" % settings.value('steam_name',''))
        gameTypes = DbHandler.execute_query("select timestamp,MissionBagIsQuickPlay from 'game'")
        if mmrs is None or gameTypes is None:   return
        mmrs = {i[0]:i[1] for i in mmrs}
        gameTypes = {i[0]:i[1] for i in gameTypes}

        qpM = {'x':[],'y':[]}
        bhM = {'x':[],'y':[]}
        points = {'x':[],'y':[]}
        #plot.setLabel('bottom','Hunts')
        i = 0
        for t in mmrs:
            if t is None:   continue
            if t not in gameTypes:  continue
            mmr = mmrs[t]
            qp = gameTypes[t]
            points['x'].append(i)
            points['y'].append(mmr)
            if qp:
                qpM['x'].append(i)
                qpM['y'].append(mmr)
            else:
                bhM['x'].append(i)
                bhM['y'].append(mmr)
            i += 1
        if len(points['x']) == 0:
            return
        
        self.plot.plot(points['x'],points['y'],pen='#ffffff44', symbol=None)
        qpP = self.plot.plot(qpM['x'],qpM['y'],pen=None, symbolPen=None,symbolBrush='#00ffff',symbol='o',name='Quick Play')
        bhP = self.plot.plot(bhM['x'],bhM['y'],pen=None, symbolPen=None,symbolBrush='#ff0000',symbol='o', name='Bounty Hunt')
        self.legend.addItem(bhP, name=bhP.opts['name'])
        self.legend.addItem(qpP, name=qpP.opts['name'])
        self.plot.showGrid(x = True, y = True, alpha = 0.1)
        self.plot.getViewBox().setLimits(xMin=0,xMax=len(points['x']),yMin=0,yMax=5000)
        for mmr in [0,2000,2300,2600,2750,3000,5000]:
            line = pyqtgraph.InfiniteLine(mmr,pen="#ffaaaa88",angle=0)
            self.plot.addItem(line)
        self.plot.setXRange(len(points['x'])-50,len(points['x']))
        self.xZoom.setValue(100-(50/len(points['x'])*100))
        self.plot.setYRange(min(points['y'])-100,max(points['y'])+100)
        self.yZoom.setValue(100-
            ((((max(points['y'])+100) - (min(points['y'])-100)) / 5000) * 100)
        )
        self.plot.setLabel('left','MMR')
        self.plot.setLabel('bottom','Hunts')

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.GraphicsSceneWheel:
            return True
        return super().eventFilter(obj, event)