from PyQt6.QtWidgets import QWidget,QVBoxLayout,QHBoxLayout,QPushButton,QComboBox, QSizePolicy, QLabel
from PyQt6.QtCore import QEvent, Qt
import pyqtgraph
from DbHandler import *
from MainWindow.Chart.MmrData import MmrData
from MainWindow.Chart.KdaData import KdaData
from MainWindow.Chart.KillsData import KillsData 
from resources import *

class Chart(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.dataSelections = {
            "mmr":self.initMmrGraph,
            "kda":self.initKdaGraph
            }
        '''
        self.dataSelections = {
            "mmr":self.initMmrGraph,
            "kda":self.initKdaGraph,
            "wins":self.initMmrGraph,
            "kills":self.initKillsGraph
            }
        '''

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.initUI()


    def initTools(self):
        self.tools = QWidget()
        self.tools.layout = QHBoxLayout()
        self.tools.setLayout(self.tools.layout)
        self.initDataSelect()
        self.updateButton = QPushButton("refresh")
        self.updateButton.clicked.connect(self.update)
        self.updateButton.setSizePolicy(QSizePolicy.Policy.Fixed,QSizePolicy.Policy.Fixed)
        self.tools.layout.addWidget(self.updateButton)
        self.layout.addWidget(self.tools)

    def initDataSelect(self):
        self.dataSelect = QComboBox()
        self.dataSelect.addItems(self.dataSelections.keys())
        self.dataSelect.activated.connect(self.SetData)

        self.tools.layout.addWidget(self.dataSelect)

    def SetData(self):
        self.graph.clear()
        self.legend.clear()
        data = self.dataSelect.currentText()
        try:
            self.dataSelections[data]()
        except Exception as e:
            print('setdata')
            print(e)
            return

    def initUI(self):
        self.initTools()
        self.graphWindow = pyqtgraph.GraphicsLayoutWidget()
        self.graph = self.graphWindow.addPlot(0,0)

        self.legendVb = pyqtgraph.ViewBox()
        self.legend = pyqtgraph.LegendItem(colCount=2)
        self.legend.setParentItem(self.legendVb)
        self.legend.anchor((0,0),(0,0))
        self.graphWindow.addItem(self.legendVb,1,0)
        self.layout.addWidget(self.graphWindow)
        self.layout.addWidget(QLabel("Use scroll wheel to zoom y axis; Shift+scroll to zoom x axis."))


    def update(self):
        self.legend.clear()
        self.graphWindow.removeItem(self.graph)
        self.graph = self.graphWindow.addPlot(0,0)
        self.SetData()
        self.legend.getViewBox().setMaximumHeight(self.legend.boundingRect().height())
        self.graph.showGrid(x=True, y=True, alpha=0.4)
        self.graph.getViewBox().installEventFilter(self)
        #self.graph.setMouseEnabled(x=False)

    def initKdaGraph(self):
        kda = KdaData()
        self.graph.addItem(kda.line)
        self.graph.addItem(kda.qpPoints)
        self.graph.addItem(kda.bhPoints)

        self.graph.setLabel('left','KDA')
        self.graph.setLabel('bottom','Hunts')

        self.legend.addItem(kda.qpPoints,name=kda.qpPoints.opts['name'])
        self.legend.addItem(kda.bhPoints,name=kda.bhPoints.opts['name'])
        self.graph.setYRange(kda.minKda - 0.1, kda.maxKda + 0.1)
        self.graph.setXRange(max(-1,len(kda.line.xData)-20),len(kda.line.xData))
        self.graph.setLimits(xMin=0,yMin=0,yMax=6000,xMax=len(kda.line.xData))

    def initKillsGraph(self):
        kills = KillsData()
        #self.graph.addItem(kills.line)
        self.graph.addItem(kills.qpPoints)
        self.graph.addItem(kills.bhPoints)

        self.graph.setLabel('left','Kills')
        self.graph.setLabel('bottom','Hunts')

        self.legend.addItem(kills.qpPoints,name=kills.qpPoints.opts['name'])
        self.legend.addItem(kills.bhPoints,name=kills.bhPoints.opts['name'])
        self.graph.setYRange(-1,kills.maxKills+1)
        self.graph.setXRange(max(-1,len(kills.line.xData)-20),len(kills.line.xData))
        self.graph.setLimits(xMin=0,yMin=-1,yMax=kills.maxKills+1,xMax=len(kills.line.xData))

    def initMmrGraph(self):
        mmr = MmrData()
        self.graph.addItem(mmr.line)
        self.graph.addItem(mmr.qpPoints)
        self.graph.addItem(mmr.bhPoints)
        for line in mmr.stars:
            self.graph.addItem(line)

        self.graph.setLabel('left','MMR')
        self.graph.setLabel('bottom','Hunts')

        self.legend.addItem(mmr.qpPoints,name=mmr.qpPoints.opts['name'])
        self.legend.addItem(mmr.bhPoints,name=mmr.bhPoints.opts['name'])
        self.graph.setYRange(mmr.minMmr - 400, mmr.maxMmr + 400)
        self.graph.setXRange(max(-1,len(mmr.line.xData)-20),len(mmr.line.xData))
        self.graph.setLimits(xMin=0,yMin=0,yMax=6000,xMax=len(mmr.line.xData))

    def eventFilter(self,obj,event):
        if event.type() == QEvent.Type.GraphicsSceneWheel:
            if Qt.KeyboardModifier.ShiftModifier in event.modifiers():
                self.graph.setMouseEnabled(y=False, x=True)
            else:
                self.graph.setMouseEnabled(y=True, x=False)
        elif event.type() == QEvent.Type.GrabMouse:
            self.graph.setMouseEnabled(x=True)
        return super().eventFilter(obj,event)