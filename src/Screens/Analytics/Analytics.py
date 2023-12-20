from PyQt6.QtCore import Qt
from PyQt6.QtGui import QResizeEvent, QColor
from PyQt6. QtWidgets import QWidget, QVBoxLayout, QLabel, QScrollArea, QSizePolicy, QHBoxLayout
import pyqtgraph
import numpy
from DbHandler import execute_query
from resources import settings
from Screens.Analytics.components.MmrGraph import MmrWindow, MmrGraph
from Screens.Analytics.components.BountiesGraph import BountiesWindow,BountiesGraph
from Screens.Analytics.components.KillsGraph import KillsWindow,KillsGraph

class Analytics(QWidget):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )

        self.setObjectName("Analytics")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground)      
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.layout.setContentsMargins(8,8,8,8)
        self.layout.setSpacing(0)

        self.mmrPlot = MmrWindow()
        self.bountiesPlot = BountiesWindow()
        self.killsPlot = KillsWindow()
        self.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )
        self.mmrHeader = self.initMmrLabels()
        self.topRow = QWidget()
        self.topRow.layout = QHBoxLayout()
        self.topRow.setLayout(self.topRow.layout)
        self.topRow.layout.setContentsMargins(0,0,0,0)
        self.topRow.layout.setSpacing(0)
        self.topRow.layout.addWidget(self.bountiesPlot)
        self.topRow.layout.addWidget(self.killsPlot)
        self.layout.addWidget(self.topRow,stretch=2)
        self.layout.addWidget(self.mmrHeader,stretch=0)
        self.layout.addWidget(self.mmrPlot,stretch=5)
        self.layout.addStretch()

        self.update()
        return
        self.addItem(self.mmrPlot,2,0,1,2)
        self.addItem(self.bountiesPlot,0,0,1,1)
        vb = pyqtgraph.ViewBox()
        self.mmrPlot.legend.setParentItem(vb)
        self.mmrPlot.legend.anchor((0,0),(0,0))
        self.addItem(vb,3,0)
        self.mmrPlot.getViewBox().installEventFilter(self)
        self.setMouseTracking(True)
        self.setBackground(QColor("#283940"))

        self.setStats()

        self.update()
        self.setContentsMargins(8,8,8,8)

    def initMmrLabels(self):
        mmrHeader = QWidget()
        mmrHeader.setObjectName("AnalyticsMmrHeader")
        mmrHeader.layout = QHBoxLayout()
        mmrHeader.setLayout(mmrHeader.layout) 
        mmrHeader.layout.setSpacing(0)
        mmrHeader.layout.setContentsMargins(0,0,0,0)
        self.mmrAvg = QLabel()
        self.mmrGain = QLabel()
        self.mmrLoss = QLabel()
        self.mmrAvg.setObjectName("avg")
        self.mmrGain.setObjectName("gain")
        self.mmrLoss.setObjectName("loss")
        mmrHeader.layout.addWidget(self.mmrGain)
        mmrHeader.layout.addWidget(self.mmrAvg)
        mmrHeader.layout.addWidget(self.mmrLoss)
        return mmrHeader

    def setStats(self):
        avgMmr = execute_query("select avg(mmr) from 'hunters' where profileid = ?", settings.value("profileid"))
        if len(avgMmr) == 0:
            avgMmr = 0
        else:
            avgMmr = avgMmr[0][0]

        mmrGain = execute_query("select\
                                lag(h.mmr) over (order by g.timestamp desc) - h.mmr as mmr_gain\
                                from 'hunters' h join 'games' g on h.game_id = g.game_id where h.profileid = ? order by mmr_gain desc limit 1", settings.value("profileid",0))
        if len(mmrGain) == 0:
            mmrGain = 0
        else:
            mmrGain = mmrGain[0][0]
        mmrLoss = execute_query("select\
                                lag(h.mmr) over (order by g.timestamp desc) - h.mmr as mmr_loss\
                                from 'hunters' h join 'games' g on h.game_id = g.game_id where h.profileid = ? order by mmr_loss asc limit 1 offset 2", settings.value("profileid",0))
        if len(mmrLoss) == 0:
            mmrLoss = 0
        else:
            mmrLoss = mmrLoss[0][0]
        return [avgMmr,mmrGain,mmrLoss]

    def update(self):
        self.mmrPlot.update()
        self.bountiesPlot.update()
        [avg,gain,loss] = self.setStats()
        self.mmrAvg.setText("Avg MMR: %d" % avg)
        self.mmrGain.setText("Greatest MMR Gain: %d" % gain)
        self.mmrLoss.setText("Greatest MMR Loss: %d" % loss)

    def resizeEvent(self, a0: QResizeEvent) -> None:
        self.mmrPlot.mmrPlot.setFixedWidth(int(self.mmrPlot.size().width()-16))
        self.bountiesPlot.bountiesGraph.setFixedWidth(int(self.bountiesPlot.size().width()-16))
        self.killsPlot.killsGraph.setFixedWidth(int(self.killsPlot.size().width()-16))
        return super().resizeEvent(a0)