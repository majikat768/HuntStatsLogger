from PyQt5.QtWidgets import QGroupBox, QVBoxLayout,QLabel, QScrollArea,QWidget
from PyQt5.QtCore import QSettings
from GroupBox import GroupBox

settings = QSettings('./settings.ini',QSettings.Format.IniFormat)

class HuntersTab(GroupBox):
    def __init__(self, parent, layout, title=''):
        super().__init__(layout, title)
        self.parent = parent
        self.connection = self.parent.connection
        topHuntersBox = self.initTopHunters()
        self.layout.addWidget(topHuntersBox)

        topKiller = self.parent.connection.GetTopKiller()
        topKillerBox = QGroupBox('Top Killer')
        topKillerBox.layout = QVBoxLayout()
        topKillerBox.setLayout(topKillerBox.layout) 
        if len(topKiller) > 0:
            topKillerBox.layout.addWidget(QLabel(topKiller['blood_line_name']))
            topKillerBox.layout.addWidget(QLabel('has killed you %d times' % topKiller['kills']))

        self.layout.addWidget(topKillerBox)

        topKilled = self.parent.connection.GetTopKilled()
        topKilledBox = QGroupBox('Top Killed')
        topKilledBox.layout = QVBoxLayout()
        topKilledBox.setLayout(topKilledBox.layout) 
        if len(topKilled) > 0:
            topKilledBox.layout.addWidget(QLabel(topKilled['blood_line_name']))
            topKilledBox.layout.addWidget(QLabel('have killed them %d times' % topKilled['kills']))

        self.layout.addWidget(topKilledBox)

        self.layout.setRowStretch(self.layout.rowCount(),1)

    def initTopHunters(self):
        topHunters = self.connection.TopNHunters(10)
        topHuntersBox = QGroupBox('Frequent Hunters')
        topHuntersBox.layout = QVBoxLayout()
        topHuntersBox.setLayout(topHuntersBox.layout) 
        topHuntersScroll = QScrollArea()
        topHuntersBox.layout.addWidget(topHuntersScroll)
        topHuntersWidget = QWidget()
        topHuntersScroll.setWidget(topHuntersWidget)
        topHuntersScroll.setWidgetResizable(True)
        topHuntersWidget.layout = QVBoxLayout()
        topHuntersWidget.setLayout(topHuntersWidget.layout)
        for hunter in topHunters:
            topHuntersWidget.layout.addWidget(QLabel('\'%s\'' % hunter['blood_line_name']))
            topHuntersWidget.layout.addWidget(QLabel('Hunted with them %d times' % hunter['count']))
            if hunter['downedbyme'] > 0 or hunter['killedbyme'] > 0:
                topHuntersWidget.layout.addWidget(QLabel('killed them %d times' % (hunter['downedbyme']+hunter['killedbyme'])))
            if hunter['downedme'] > 0 or hunter['killedme'] > 0:
                topHuntersWidget.layout.addWidget(QLabel('killed by them %d times' % (hunter['downedme']+hunter['killedme'])))
            if hunter['ispartner'] > 0:
                topHuntersWidget.layout.addWidget(QLabel('been on their team %d times' % hunter['ispartner']))

            topHuntersWidget.layout.addWidget(QLabel())

        topHuntersScroll.setFixedHeight(topHuntersScroll.sizeHint().height()//2)

        return topHuntersBox
