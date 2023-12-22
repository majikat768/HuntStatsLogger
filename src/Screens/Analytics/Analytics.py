from PyQt6.QtCore import Qt
from PyQt6.QtGui import QResizeEvent, QColor, QCursor
from PyQt6. QtWidgets import QWidget, QVBoxLayout, QLabel, QSizePolicy, QHBoxLayout
import pyqtgraph
import numpy
from DbHandler import execute_query, get_id_from_timestamp
from resources import settings
from Screens.Analytics.components.MmrGraph import MmrWindow
from Screens.Analytics.components.BountiesGraph import BountiesWindow
from Screens.Analytics.components.KillsGraph import KillsWindow
from Screens.Analytics.components.SurvivalGraph import SurvivalWindow

class Analytics(QWidget):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )

        self.body = parent

        self.setObjectName("Analytics")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground)      
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.layout.setContentsMargins(8,8,8,8)
        self.layout.setSpacing(0)

        self.mmrPlot = MmrWindow()
        self.bountiesPlot = BountiesWindow()
        self.killsPlot = KillsWindow()
        self.survivalPlot = SurvivalWindow()

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
        self.topRow.layout.addWidget(self.bountiesPlot,stretch=5)
        self.topRow.layout.addWidget(self.survivalPlot,stretch=3)
        self.topRow.layout.addWidget(self.killsPlot,stretch=6)
        self.layout.addWidget(self.topRow)
        self.layout.addWidget(self.mmrHeader,stretch=0)
        self.layout.addWidget(self.mmrPlot)

        self.update()
        self.layout.addStretch()
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
        self.mmrGain.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.mmrLoss = QLabel()
        self.mmrLoss.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.mmrAvg.setObjectName("avg")
        self.mmrGain.setObjectName("gain")
        self.mmrLoss.setObjectName("loss")
        mmrHeader.layout.addWidget(self.mmrGain)
        mmrHeader.layout.addWidget(self.mmrAvg)
        mmrHeader.layout.addWidget(self.mmrLoss)
        return mmrHeader

    def redirectRecap(self,timestamp):
        self.body.menu.set_focus("Hunts Recap")
        self.body.setCurrentWidget("Hunts Recap")
        self.body.stack.currentWidget().show_hunt(get_id_from_timestamp(timestamp))

    def setStats(self):
        avgMmr = execute_query("select avg(mmr) from 'hunters' where profileid = ?", settings.value("profileid"))
        if len(avgMmr) == 0:
            avgMmr = 0
        else:
            avgMmr = avgMmr[0][0]

        mmrGain = execute_query("select\
                                g.timestamp, lag(h.mmr) over (order by g.timestamp desc) - h.mmr as mmr_gain\
                                from 'hunters' h join 'games' g on h.game_id = g.game_id where h.profileid = ? order by mmr_gain desc limit 1", settings.value("profileid",0))
        if len(mmrGain) == 0:
            mmrGain = 0
        else:
            mmrGain = mmrGain[0]
        mmrLoss = execute_query("select\
                                g.timestamp, lag(h.mmr) over (order by g.timestamp desc) - h.mmr as mmr_loss\
                                from 'hunters' h join 'games' g on h.game_id = g.game_id where h.profileid = ? order by mmr_loss asc limit 1 offset 2", settings.value("profileid",0))
        if len(mmrLoss) == 0:
            mmrLoss = 0
        else:
            mmrLoss = mmrLoss[0]
        return [avgMmr,mmrGain,mmrLoss]

    def update(self):
        self.mmrPlot.update()
        self.bountiesPlot.update()
        [avg,gain,loss] = self.setStats()
        if avg == None or gain == None or loss == None:
            return
        self.mmrAvg.setText("Avg MMR: %d" % avg)
        self.mmrGain.setText("Greatest MMR Gain: %d" % gain[1])
        self.mmrGain.mousePressEvent = lambda x : self.redirectRecap(gain[0])
        self.mmrLoss.setText("Greatest MMR Loss: %d" % loss[1])
        self.mmrLoss.mousePressEvent = lambda x : self.redirectRecap(loss[0])
        self.mmrPlot.mmrPlot.setFixedWidth(int(self.mmrPlot.size().width()-16))
        self.bountiesPlot.bountiesGraph.setFixedWidth(int(self.bountiesPlot.size().width()-16))
        self.killsPlot.killsGraph.setFixedWidth(int(self.killsPlot.size().width()-16))

    def resizeEvent(self, a0: QResizeEvent) -> None:
        self.mmrPlot.mmrPlot.setFixedWidth(int(self.mmrPlot.size().width()-16))
        self.bountiesPlot.bountiesGraph.setFixedWidth(int(self.bountiesPlot.size().width()-16))
        self.killsPlot.killsGraph.setFixedWidth(int(self.killsPlot.size().width()-16))
        return super().resizeEvent(a0)