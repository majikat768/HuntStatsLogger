from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QComboBox, QSizePolicy, QLabel, QScrollArea, QApplication, QFileDialog
from PyQt6.QtCore import QEvent, Qt
from PyQt6.QtGui import QScreen
import pyqtgraph
from DbHandler import *
from MainWindow.Chart.MmrData import MmrData
from MainWindow.Chart.KdaData import KdaData
from MainWindow.Chart.KillsData import KillsData
from resources import *


class Chart(QScrollArea):
    def __init__(self, parent):
        super().__init__(parent)
        self.setWidgetResizable(True)
        self.main = QWidget()
        self.main.layout = QVBoxLayout()
        self.main.setLayout(self.main.layout)
        self.setWidget(self.main)
        self.dataSelections = {
            "mmr": self.initMmrGraph,
            "kda": self.initKdaGraph
        }
        '''
        self.dataSelections = {
            "mmr":self.initMmrGraph,
            "kda":self.initKdaGraph,
            "wins":self.initMmrGraph,
            "kills":self.initKillsGraph
            }
        '''

        self.initUI()

    def initTools(self):
        self.tools = QWidget()
        self.tools.layout = QHBoxLayout()
        self.tools.setLayout(self.tools.layout)
        self.initDataSelect()
        self.updateButton = QPushButton("refresh")
        self.updateButton.clicked.connect(self.update)
        self.updateButton.setSizePolicy(
            QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.tools.layout.addWidget(self.updateButton)
        self.main.layout.addWidget(self.tools)

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
            plots = self.dataSelections[data]()
            for plot in plots:
                plot.sigClicked.connect(self.clickHandle)
        except Exception as e:
            print('setdata')
            print(e)

    def clickHandle(self, plot, spots):
        ts = spots[0].data()
        mainframe = self.window().mainframe
        huntsTab = mainframe.huntsTab
        mainframe.tabs.setCurrentWidget(huntsTab)
        if ts > 0:
            idx = huntsTab.HuntSelect.findData(ts)
        else:
            idx = -1 
        huntsTab.HuntSelect.setCurrentIndex(idx+1)
        huntsTab.updateDetails()

    def initUI(self):
        self.initTools()
        self.graphWidget = QWidget()
        self.graphWidget.layout = QVBoxLayout()
        self.graphWidget.setLayout(self.graphWidget.layout)
        self.graphWindow = pyqtgraph.GraphicsLayoutWidget()
        self.graph = self.graphWindow.addPlot(0, 0)

        self.legendVb = pyqtgraph.ViewBox()
        self.legend = pyqtgraph.LegendItem(colCount=2)
        self.legend.setParentItem(self.legendVb)
        self.legend.anchor((0, 0), (0, 0))
        self.graphWindow.addItem(self.legendVb, 1, 0)
        self.graphWidget.layout.addWidget(self.graphWindow)
        self.graphWidget.setSizePolicy(
            QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.MinimumExpanding)
        self.main.layout.addWidget(self.graphWidget)
        self.main.layout.addWidget(
            QLabel("Use scroll wheel to zoom y axis; Shift+scroll to zoom x axis."))
        self.screenshotButton = QPushButton("Save as image")
        self.screenshotButton.setSizePolicy(QSizePolicy.Policy.Fixed,QSizePolicy.Policy.Fixed)
        self.screenshotButton.clicked.connect(self.save_chart)
        self.main.layout.addWidget(self.screenshotButton)

    def update(self):
        self.legend.clear()
        self.graphWindow.removeItem(self.graph)
        self.graph = self.graphWindow.addPlot(0, 0)
        self.SetData()
        self.legend.getViewBox().setMaximumHeight(self.legend.boundingRect().height())
        self.graph.showGrid(x=True, y=True, alpha=0.4)
        self.graph.getViewBox().installEventFilter(self)
        # self.graph.setMouseEnabled(x=False)

    def initKdaGraph(self):
        kda = KdaData()
        self.graph.addItem(kda.line)
        self.graph.addItem(kda.qpPoints)
        self.graph.addItem(kda.bhPoints)

        self.graph.setLabel('left', 'KDA')
        self.graph.setLabel('bottom', 'Hunts')

        self.legend.addItem(kda.qpPoints, name=kda.qpPoints.opts['name'])
        self.legend.addItem(kda.bhPoints, name=kda.bhPoints.opts['name'])
        self.graph.setYRange(kda.minKda - 0.1, kda.maxKda + 0.1)
        self.graph.setXRange(
            max(-1, len(kda.line.xData)-20), len(kda.line.xData)+5)
        self.graph.setLimits(xMin=0, yMin=0, yMax=6000,
                             xMax=len(kda.line.xData)+5)
        return [kda.qpPoints, kda.bhPoints]

    def initKillsGraph(self):
        kills = KillsData()
        # self.graph.addItem(kills.line)
        self.graph.addItem(kills.qpPoints)
        self.graph.addItem(kills.bhPoints)

        self.graph.setLabel('left', 'Kills')
        self.graph.setLabel('bottom', 'Hunts')

        self.legend.addItem(kills.qpPoints, name=kills.qpPoints.opts['name'])
        self.legend.addItem(kills.bhPoints, name=kills.bhPoints.opts['name'])
        self.graph.setYRange(-1, kills.maxKills+1)
        self.graph.setXRange(
            max(-1, len(kills.line.xData)-20), len(kills.line.xData)+5)
        self.graph.setLimits(
            xMin=0, yMin=-1, yMax=kills.maxKills+1, xMax=len(kills.line.xData)+5)

    def initMmrGraph(self):
        mmr = MmrData()
        self.graph.addItem(mmr.line)
        self.graph.addItem(mmr.qpPoints)
        self.graph.addItem(mmr.bhPoints)
        self.graph.addItem(mmr.nextPoint)
        for line in mmr.stars:
            self.graph.addItem(line)

        self.graph.setLabel('left', 'MMR')
        self.graph.setLabel('bottom', 'Hunts')

        self.legend.addItem(mmr.qpPoints, name=mmr.qpPoints.opts['name'])
        self.legend.addItem(mmr.bhPoints, name=mmr.bhPoints.opts['name'])
        self.graph.setYRange(mmr.minMmr - 400, mmr.maxMmr + 400)
        self.graph.setXRange(
            max(-1, len(mmr.line.xData)-20), len(mmr.line.xData)+5)
        self.graph.setLimits(xMin=0, yMin=0, yMax=6000,
                             xMax=len(mmr.line.xData)+5)
        return [mmr.qpPoints, mmr.bhPoints, mmr.nextPoint]

    def save_chart(self):
        name = "chart_%s.png" % int(time.time())
        file = QFileDialog.getSaveFileName(
            parent=self.window(),
            directory=os.path.join(QStandardPaths.writableLocation(QStandardPaths.StandardLocation.DesktopLocation),name),
            filter="PNG (*.png)"
        )[0]

        scrn = QApplication.primaryScreen().grabWindow(self.graphWindow.winId())
        scrn.save(file)

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.GraphicsSceneWheel:
            if Qt.KeyboardModifier.ShiftModifier in event.modifiers():
                self.graph.setMouseEnabled(y=False, x=True)
            else:
                self.graph.setMouseEnabled(y=True, x=False)
        elif event.type() == QEvent.Type.GrabMouse:
            self.graph.setMouseEnabled(x=True)
        return super().eventFilter(obj, event)