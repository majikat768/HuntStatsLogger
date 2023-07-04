from PyQt6.QtWidgets import QLabel, QScrollArea, QWidget, QVBoxLayout, QHBoxLayout, QComboBox, QGraphicsView, QGraphicsScene, QGraphicsEllipseItem, QSizePolicy, QGraphicsItemGroup, QGraphicsRectItem, QApplication, QPushButton, QFileDialog
import numpy as np
from PyQt6.QtCore import Qt, QEvent, QRectF, QStandardPaths
from PyQt6.QtGui import QColor
import pyqtgraph
import os, time
from MainWindow.Chart.TeamMmrData import TeamMmrData
from MainWindow.Chart.MmrData import MmrData
from MainWindow.Chart.KdaData import KdaData
from MainWindow.Chart.WinLoss import WinLoss
from MainWindow.Chart.KillsPerHunt import KillsPerHunt
from MainWindow.Chart.TeamKillsPerHunt import TeamKillsPerHunt
from resources import debug

class Chart(QScrollArea):
    def __init__(self, parent=None):
        if debug:
            print("chart.__init__")
        super().__init__(parent)
        self.setWidgetResizable(True)
        self.main = QWidget()
        self.main.layout = QVBoxLayout()
        self.main.setLayout(self.main.layout)
        self.setWidget(self.main)
        self.options = {
            "MMR":self.setMmr,
            "Team MMR":self.setTeamMmr,
            "Own MMR / Team MMR":self.setBothMmrs,
            "KDA":self.setKda,
            "Win/Loss":self.setWinLoss,
            "Kills Per Hunt":self.setKills,
            "Team Kills Per Hunt":self.setTeamKills
        }

        self.initUI()

        self.bounty = None

    def initDropdown(self):
        if debug:
            print("chart.initDropdown")
        self.dropdownWidget = QWidget()
        self.dropdownWidget.layout = QHBoxLayout()
        self.dropdownWidget.setLayout(self.dropdownWidget.layout)

        self.dataSelect = QComboBox()
        self.dataSelect.addItems(self.options.keys())
        self.dataSelect.activated.connect(self.update)

        self.updateButton = QPushButton("refresh")
        self.updateButton.setSizePolicy(QSizePolicy.Policy.Fixed,QSizePolicy.Policy.Fixed)
        self.updateButton.clicked.connect(self.update)

        self.dropdownWidget.layout.addWidget(self.dataSelect)
        self.dropdownWidget.layout.addWidget(self.updateButton)
        self.main.layout.addWidget(self.dropdownWidget)

    def initPlot(self):
        if debug:
            print("chart.initPlot")
        self.plotWindow = pyqtgraph.GraphicsLayoutWidget()
        self.plot = pyqtgraph.PlotItem()
        self.plotWindow.addItem(self.plot,0,0)
        vb = pyqtgraph.ViewBox()
        self.legend = pyqtgraph.LegendItem(colCount=2)
        self.legend.setParentItem(vb)
        self.legend.anchor((0,0),(0,0))
        self.plotWindow.addItem(vb,1,0)
        self.plot.getViewBox().installEventFilter(self)
        self.main.layout.addWidget(self.plotWindow)

    def initUI(self):
        if debug:
            print("chart.initUI")
        self.initDropdown()
        self.initPlot()

        self.screenshotButton = QPushButton("Save as image")
        self.screenshotButton.setSizePolicy(QSizePolicy.Policy.Fixed,QSizePolicy.Policy.Fixed)
        self.screenshotButton.clicked.connect(self.save_chart)
        self.main.layout.addWidget(
            QLabel("Use scroll wheel to zoom y axis; Shift+scroll to zoom x axis."))
        self.main.layout.addWidget(self.screenshotButton)

    def update(self):
        if debug:
            print("chart.update")
        opt = self.dataSelect.currentText()
        self.plot.clear()
        self.legend.clear()
        self.options[opt]()
        self.legend.getViewBox().setMaximumHeight(self.legend.boundingRect().height())
        self.plot.showGrid(x=True,y=True,alpha=0.4)
        for i in range(10):
            QApplication.processEvents()

    def setBothMmrs(self):
        self.setMmr()
        self.setTeamMmr(color="#ffffff")

    def setTeamMmr(self,color="#ff0000"):
        mmr = TeamMmrData(color,parent=self)
        self.plot.addItem(mmr.line)
        self.plot.addItem(mmr.points)
        for line in mmr.stars:
            self.plot.addItem(line)
        self.plot.setLabel('left','MMR')
        self.plot.setLabel('bottom', 'Hunts')
        self.legend.addItem(mmr.points,name=mmr.points.opts['name'])
        self.plot.setLimits(xMin=0,yMin=0,yMax=6000,xMax=len(mmr.line.xData)+5)
        xrange = int(self.plot.getAxis("bottom").range[1])
        self.plot.getAxis("bottom").setTicks([])

    def setMmr(self):
        mmr = MmrData(parent=self)
        self.plot.addItem(mmr.line)
        self.plot.addItem(mmr.qpPoints)
        self.plot.addItem(mmr.bhPoints)
        self.plot.addItem(mmr.nextPoint)
        for line in mmr.stars:
            self.plot.addItem(line)
        self.plot.setLabel('left','MMR')
        self.plot.setLabel('bottom', 'Hunts')
        self.legend.addItem(mmr.qpPoints,name=mmr.qpPoints.opts['name'])
        self.legend.addItem(mmr.bhPoints,name=mmr.bhPoints.opts['name'])
        self.plot.setLimits(xMin=0, yMin=0, yMax=6000,
                            xMax=len(mmr.line.xData)+2)
        self.plot.setYRange(mmr.minMmr - 400, mmr.maxMmr + 400)
        self.plot.setXRange(
            max(-1, len(mmr.line.xData)-20), len(mmr.line.xData)+2)
        xrange = self.plot.getAxis("bottom").range[1]
        self.plot.getAxis("bottom").setTicks([])

    def setKda(self):
        kda = KdaData(parent=self)
        self.plot.addItem(kda.line)
        self.plot.addItem(kda.qpPoints)
        self.plot.addItem(kda.bhPoints)

        self.plot.setLabel('left', 'KDA')
        self.plot.setLabel('bottom', 'Hunts')

        self.legend.addItem(kda.qpPoints, name=kda.qpPoints.opts['name'])
        self.legend.addItem(kda.bhPoints, name=kda.bhPoints.opts['name'])
        self.plot.setLimits(xMin=0, yMin=0, yMax=6000,
                             xMax=len(kda.line.xData)+5)
        self.plot.setYRange(kda.minKda - 0.1, kda.maxKda + 0.1)
        self.plot.setXRange(
            max(-1, len(kda.line.xData)-20), len(kda.line.xData)+5)
        #self.plot.getAxis("bottom").setTickSpacing()
        xrange = self.plot.getAxis("bottom").range[1]
        self.plot.getAxis("bottom").setTicks([])

    def setWinLoss(self):
        winLoss = WinLoss()
        '''
        height = max(
            winLoss.data['survivalRate']['total'], max(
                winLoss.data['winRate']['bounty']['total'],winLoss.data['winRate']['qp']['total']
            )
        ) + 32
        '''
        height =  winLoss.ymax+10

        self.plot.addItem(winLoss.bountyBars)
        self.plot.addItem(winLoss.quickplayBars)
        self.plot.addItem(winLoss.survivalBars)
        self.plot.setLabel('left','# of Hunts')
        self.plot.setLimits(xMin=0, xMax=80,yMin=0, yMax=height)
        self.plot.setXRange(0,80)
        self.plot.setYRange(0,height)
        '''
        self.plot.getAxis("left").setTicks([
            [(i*10,"%d%%" %(i*10)) for i in range(11)]
        ])
        '''
        self.plot.getAxis("bottom").setTicks(winLoss.labels)
        self.plot.setLabel('bottom', ' ')

    def setKills(self):
        kills = KillsPerHunt()
        xmax = (len(kills.ticks[0])+1)*3*kills.width
        ymax = max(kills.bountyline.value(),kills.qpline.value())+30
        self.plot.addItem(kills.bars)
        self.plot.addItem(kills.bountyline)
        self.plot.addItem(kills.qpline)
        self.plot.getAxis("bottom").setTicks(kills.ticks)
        self.plot.setLimits(xMin=0, xMax=xmax,yMin=0, yMax=ymax)
        self.plot.setXRange(0,xmax)
        self.plot.setYRange(0,ymax)
        self.plot.setLabel('left', 'Hunts')
        self.plot.setLabel('bottom', 'Kills Per Hunt')
        self.legend.addItem(kills.bountyLegendItem, name="Bounty Hunt")
        self.legend.addItem(kills.qpLegendItem, name="Quick Play")
        self.plot.showGrid(x=True,y=False,alpha=0.4)
        '''
        self.plot.getAxis("left").setTicks([
            [(i,"%d" %(i)) for i in np.linspace(0,ymax,10)]
        ])
        '''
        for i in range(10):
            QApplication.processEvents()

    def setTeamKills(self):
        kills = TeamKillsPerHunt()
        self.plot.addItem(kills.bars)
        self.plot.getAxis("bottom").setTicks(kills.ticks)
        xmax = (len(kills.ticks[0])+1)*2*kills.width
        ymax = kills.line.value()+10
        self.plot.setLimits(xMin=0, xMax=xmax,yMin=0, yMax=ymax)
        self.plot.setXRange(0,xmax)
        self.plot.setYRange(0,ymax)
        self.plot.addItem(kills.line)
        self.plot.setLabel('left', 'Hunts')
        self.plot.setLabel('bottom', 'Team Kills Per Hunt')
        #self.legend.addItem(kills.legendItem, name="Team Kills")

    def resizeEvent(self, a0):
        return super().resizeEvent(a0)

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.GraphicsSceneWheel:
            if Qt.KeyboardModifier.ShiftModifier in event.modifiers():
                self.plot.setMouseEnabled(y=False, x=True)
            else:
                self.plot.setMouseEnabled(y=True, x=False)
        elif event.type() == QEvent.Type.GrabMouse:
            self.plot.setMouseEnabled(x=True)
        return super().eventFilter(obj, event)

    def save_chart(self):
        name = "chart_%s.png" % int(time.time())
        file = QFileDialog.getSaveFileName(
            parent=self.window(),
            directory=os.path.join(QStandardPaths.writableLocation(QStandardPaths.StandardLocation.DesktopLocation),name),
            filter="PNG (*.png)"
        )[0]
        if len(file) <= 0:
            return
        
        scrn = QApplication.primaryScreen().grabWindow(self.plotWindow.winId())
        scrn.save(file)
