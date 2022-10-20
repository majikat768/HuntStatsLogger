from math import inf
from PyQt6.QtWidgets import QWidget,QVBoxLayout,QHBoxLayout,QGridLayout,QPushButton,QComboBox, QSizePolicy
from PyQt6.QtCore import QEvent
import pyqtgraph
from DbHandler import *
from resources import *

class Chart(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.initUI()


    def initTools(self):
        self.tools = QWidget()
        self.tools.layout = QHBoxLayout()
        self.tools.setLayout(self.tools.layout)
        self.dataSelect = QComboBox()
        self.updateButton = QPushButton("refresh")
        self.updateButton.clicked.connect(self.update)
        self.updateButton.setSizePolicy(QSizePolicy.Policy.Fixed,QSizePolicy.Policy.Fixed)
        self.tools.layout.addWidget(self.dataSelect)
        self.tools.layout.addWidget(self.updateButton)
        self.layout.addWidget(self.tools)

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


    def update(self):
        self.legend.clear()
        self.graphWindow.removeItem(self.graph)
        self.graph = self.graphWindow.addPlot(0,0)
        self.initMmrGraph()
        self.legend.getViewBox().setMaximumHeight(self.legend.boundingRect().height())
        self.graph.showGrid(x=True, y=True, alpha=0.6)
        self.graph.getViewBox().installEventFilter(self)
        #self.graph.setMouseEnabled(x=False)

    def initMmrGraph(self):
        data = []
        mmrs = GetAllMmrs(name=settings.value('steam_name'))
        i = 0
        minMmr = inf;
        maxMmr = -inf;
        for ts in mmrs.keys():
            mmr = mmrs[ts]['mmr']
            qp = mmrs[ts]['qp']
            if mmr > maxMmr:
                maxMmr = mmr
            if mmr < minMmr:
                minMmr = mmr
            data.append({'x':i,'y':mmr, 'qp':qp, 'ts':ts})
            i += 1
        line = pyqtgraph.PlotDataItem(data)
        qpPoints = pyqtgraph.ScatterPlotItem(
            [{'x': pt['x'], 'y': pt['y']} for pt in data if pt['qp'] == 'true'],
            size=12,hoverable=True,hoverSize=16,symbol='o',pen="#000000",brush="#00ffff",name="Quick Play"
        )
        bhPoints = pyqtgraph.ScatterPlotItem(
            [{'x': pt['x'], 'y': pt['y']} for pt in data if pt['qp'] == 'false'],
            size=12,hoverable=True,hoverSize=16,symbol='o',pen="#000000",brush="#ff0000",name="Bounty Hunt"
        )

        self.graph.addItem(line)
        self.graph.addItem(qpPoints)
        self.graph.addItem(bhPoints)

        self.graph.setLabel('left','MMR')
        self.graph.setLabel('bottom','Hunts')

        stars = [2000,2300,2600,2750,3000,5000]

        for s in stars:
            c = s/5000*255
            line = pyqtgraph.InfiniteLine(pos=s, angle=0, pen=pyqtgraph.mkPen("#ff0000",width=2))
            label = pyqtgraph.TextItem(text="%d+: %d stars"%(s,mmr_to_stars(s)), color="#ffffff")
            label.setParentItem(line)
            label.setPos(0,0)
            self.graph.addItem(line)

        self.legend.addItem(qpPoints,name=qpPoints.opts['name'])
        self.legend.addItem(bhPoints,name=bhPoints.opts['name'])
        self.graph.setYRange(minMmr - 100, maxMmr + 100)
        self.graph.setXRange(max(0,len(data)-20),min(20,len(data)))
        self.graph.setLimits(xMin=0,yMin=0,yMax=6000,xMax=inf)

            

    def eventFilter(self,obj,event):
        if event.type() == QEvent.Type.GraphicsSceneWheel:
            self.graph.setMouseEnabled(x=False)
        elif event.type() == QEvent.Type.GrabMouse:
            self.graph.setMouseEnabled(x=True)
        return super().eventFilter(obj,event)