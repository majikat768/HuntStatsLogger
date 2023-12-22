from PyQt6 import QtCore
from PyQt6.QtCore import QEvent, QObject, Qt
from PyQt6.QtGui import QMouseEvent
from PyQt6.QtWidgets import QWidget, QGridLayout, QHBoxLayout, QVBoxLayout, QSplitter, QSizePolicy, QLabel, QGroupBox, QScrollArea, QApplication, QSplitterHandle,QSpacerItem
from resources import resource_path
from Screens.HuntsRecap.components.KillsWidget import KillsWidget
from Screens.HuntsRecap.components.MonstersWidget import MonstersWidget
from Screens.HuntsRecap.components.BountiesWidget import BountiesWidget
from Screens.HuntsRecap.components.RewardsWidget import RewardsWidget
from Screens.HuntsRecap.components.TimelineWidget import TimelineWidget 
from Screens.HuntsRecap.components.TeamsWidget import TeamsWidget

class HuntWidget(QWidget):
    def __init__(self, game_id, parent: QWidget | None = None):
        super().__init__(parent)
        self.setObjectName("HuntWidget")
        self.layout = QHBoxLayout()
        self.setLayout(self.layout)
        self.setContentsMargins(0,0,0,0)

        self.setSizePolicy(QSizePolicy.Policy.Expanding,QSizePolicy.Policy.Expanding)
        self.game_id = game_id
        self.layout.setSpacing(16)

        self.splitter = QSplitter()
        self.splitter.setSizePolicy(QSizePolicy.Policy.Expanding,QSizePolicy.Policy.Expanding)
        self.leftPane = LeftPane(self.game_id)
        self.timelineWidget = TimelineWidget(self.game_id)
        self.teamsWidget = TeamsWidget(self.game_id)

        self.splitter.addWidget(self.leftPane)
        self.splitter.addWidget(self.teamsWidget)
        self.splitter.addWidget(self.timelineWidget)
        self.splitter.setStretchFactor(0,1)
        self.splitter.setStretchFactor(1,4)
        self.splitter.setStretchFactor(2,3)
        self.layout.addWidget(self.splitter)

        self.layout.setAlignment(self.leftPane,QtCore.Qt.AlignmentFlag.AlignTop)
        #self.layout.addWidget(self.teamsWidget,stretch=4)
        #self.layout.addWidget(self.timelineWidget,stretch=1)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_StyledBackground)      
        self.leftPane.init()
        self.timelineWidget.init()
        self.teamsWidget.init()

        self.setMinimumWidth(self.sizeHint().width())

        self.splitter.setStyleSheet("QSplitter::handle:horizontal{image:url(\"%s\");}" % resource_path('assets/icons/h_handle.png').replace("\\","/"))

    def toggle(self):
        self.setVisible(not self.isVisible())
        if(self.isVisible):
            self.leftPane.init()
            self.timelineWidget.init()
            self.teamsWidget.init()

class LeftPane(QGroupBox):
    def __init__(self, game_id, parent: QWidget | None = None):
        super().__init__(parent)

        self.game_id = game_id

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.layout.setContentsMargins(4,6,4,4)
        self.layout.setSpacing(16)

        self.killsWidget = KillsWidget(self.game_id)
        self.bountiesWidget = BountiesWidget(self.game_id)
        self.monstersWidget = MonstersWidget(self.game_id)
        self.rewardsWidget = RewardsWidget(self.game_id)

        self.layout.addWidget(self.killsWidget)
        self.layout.addStretch()
        self.layout.addWidget(self.bountiesWidget)
        self.layout.addWidget(self.monstersWidget)
        self.layout.addWidget(self.rewardsWidget)
        self.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )

    def init(self):
        self.killsWidget.init()
        self.bountiesWidget.init()
        self.monstersWidget.init()
        self.rewardsWidget.init()