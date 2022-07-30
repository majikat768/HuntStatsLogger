from ast import PyCF_ALLOW_TOP_LEVEL_AWAIT
from GroupBox import GroupBox
from PyQt6.QtWidgets import QComboBox
import pyqtgraph

class Chart(GroupBox):
    def __init__(self, parent, layout, title=''):
        super().__init__(layout, title)
        self.plotWindow = pyqtgraph.GraphicsLayoutWidget()
        self.parent = parent
        self.settings = self.parent.settings
        self.connection = self.parent.connection
        self.dataSelect = QComboBox()
        self.dataSelect.addItem("MMR")
        self.dataSelect.addItem("KDA")
        self.dataSelect.currentTextChanged.connect(self.update)
        self.layout.addWidget(self.dataSelect)
        self.layout.addWidget(self.plotWindow)

        self.update()

    def update(self):
        if self.dataSelect.currentText() == 'MMR':
            self.initMmrGraph()
        elif self.dataSelect.currentText() == 'KDA':
            self.initKdaGraph()

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
        self.plotWindow.clear()
        kills = self.connection.execute_query("select timestamp, downedbyme, killedbyme from hunter where downedbyme > 0 or killedbyme > 0")
        deaths = self.connection.execute_query("select timestamp, downedme, killedme from hunter where downedme > 0 or killedme > 0")
        assists = self.connection.execute_query("select timestamp, amount from 'entry' where category is 'accolade_players_killed_assist'")
        hunts = self.connection.execute_query("select timestamp,MissionBagIsQuickPlay from 'game'")

        kdas = self.calcKda(kills,deaths,assists,hunts)
        qpKdas = self.calcKda(kills,deaths,assists,hunts,1)
        bhKdas = self.calcKda(kills,deaths,assists,hunts,0)
        

        vb = self.plotWindow.addViewBox(1,0)
        legend = pyqtgraph.LegendItem()
        legend.setParentItem(vb)
        legend.anchor((0,0),(0,0))

        plot = self.plotWindow.addPlot(0,0)
        kdaP = plot.plot(kdas['x'],kdas['y'],pen='#ffffff44',symbol='t1',symbolPen=None,symbolBrush='#ff0000')
        qpKdaP = plot.plot(qpKdas['x'],qpKdas['y'],pen='#ffffff44',symbol='t1',symbolPen=None,symbolBrush='#ffff00')
        bhKdaP = plot.plot(bhKdas['x'],bhKdas['y'],pen='#ffffff44',symbol='t1',symbolPen=None,symbolBrush='#0088ff')
        plot.setXRange(0,len(kdas['x']))
        plot.setYRange(0,max(kdas['y'])+0.5)
        legend.addItem(kdaP, name='KDA')
        legend.addItem(bhKdaP, name='Bounty KDA')
        legend.addItem(qpKdaP, name='QP KDA')

        plot.showGrid(x = True, y = True, alpha = 0.4)
        plot.setMouseEnabled(x=False)
        plot.getViewBox().setLimits(xMin=0,xMax=len(kdas['x']),yMin=0,yMax=max(kdas['y'])*2)
        vb.setMaximumHeight(legend.boundingRect().height())
        plot.setLabel('left','KDA')
        plot.setLabel('bottom','Hunts')

    def initMmrGraph(self):
        self.plotWindow.clear()
        mmrs = self.connection.execute_query("select timestamp,mmr from 'hunter' where blood_line_name is '%s'" % self.settings.value('hunterName',''))
        gameTypes = self.connection.execute_query("select timestamp,MissionBagIsQuickPlay from 'game'")
        mmrs = {i[0]:i[1] for i in mmrs}
        gameTypes = {i[0]:i[1] for i in gameTypes}

        qpM = {'x':[],'y':[]}
        bhM = {'x':[],'y':[]}
        points = {'x':[],'y':[]}
        #plot.setLabel('bottom','Hunts')
        i = 0
        for t in mmrs:
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
        
        #qp = plot.plot(qpM[0],qpM[1],pen=None,symbolPen='#000000',symbolBrush="#ff0000",symbol='t1',name="quick play")
        #bh = plot.plot(bhM[0],bhM[1],pen=None,symbolPen='#000000',symbolBrush="#00ffff",symbol='t1',name="bounty hunt")

        vb = self.plotWindow.addViewBox(1,0)
        legend = pyqtgraph.LegendItem()
        legend.setParentItem(vb)
        legend.anchor((0,0),(0,0))

        plot = self.plotWindow.addPlot(0,0)
        plot.plot(points['x'],points['y'],pen='#ffffff44', symbol=None)
        qpP = plot.plot(qpM['x'],qpM['y'],pen=None, symbolPen=None,symbolBrush='#00ffff',symbol='o',name='Quick Play')
        bhP = plot.plot(bhM['x'],bhM['y'],pen=None, symbolPen=None,symbolBrush='#ff0000',symbol='o', name='Bounty Hunt')
        legend.addItem(bhP, name=bhP.opts['name'])
        legend.addItem(qpP, name=qpP.opts['name'])
        plot.showGrid(x = True, y = True, alpha = 0.1)
        plot.setXRange(0,len(points['x']))
        plot.setYRange(min(points['y']),max(points['y']))
        plot.setMouseEnabled(x=False)
        plot.getViewBox().setLimits(xMin=0,xMax=len(points['x']),yMin=0,yMax=5000)
        if max(points['y']) - min(points['y']) < 100:
            plot.setYRange(min(points['y'])-100,max(points['y'])+100)
        for mmr in [0,2000,2300,2600,2750,3000,5000]:
            line = pyqtgraph.InfiniteLine(mmr,pen="#ffaaaa88",angle=0)
            plot.addItem(line)
            #plot.plot(range(len(points)),[mmr]*len(points),pen="#888888")
        vb.setMaximumHeight(legend.boundingRect().height())
        plot.setLabel('left','MMR')
        plot.setLabel('bottom','Hunts')