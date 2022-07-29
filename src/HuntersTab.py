from PyQt5.QtWidgets import QGroupBox, QVBoxLayout,QLabel, QScrollArea,QWidget,QGridLayout
from PyQt5.QtCore import QSettings, Qt
from GroupBox import GroupBox
from HunterLabel import HunterLabel

settings = QSettings('./settings.ini',QSettings.Format.IniFormat)

class HuntersTab(GroupBox):
    def __init__(self, parent, layout, title=''):
        super().__init__(layout, title)
        self.parent = parent
        self.connection = self.parent.connection

        self.topHuntersBox = self.initTopHunters()
        self.layout.addWidget(self.topHuntersBox,1,0,1,2)

        self.topKillerBox = self.initTopKiller()
        self.layout.addWidget(self.topKillerBox,0,0)

        self.topKilledBox = self.initTopKilled()
        self.layout.addWidget(self.topKilledBox,0,1)

        self.layout.setRowStretch(self.layout.rowCount(),1)

    def initTopKiller(self):
        topKiller = self.parent.connection.GetTopKiller()
        topKillerBox = QGroupBox('Top Killer')
        topKillerBox.layout = QVBoxLayout()
        topKillerBox.setLayout(topKillerBox.layout) 
        if len(topKiller) > 0:
            topKillerBox.layout.addWidget(HunterLabel(topKiller['blood_line_name']))
            topKillerBox.layout.addWidget(QLabel('Has killed you %d times' % topKiller['kills']))
        return topKillerBox

    def initTopKilled(self):
        topKilled = self.parent.connection.GetTopKilled()
        topKilledBox = QGroupBox('Top Killed')
        topKilledBox.layout = QVBoxLayout()
        topKilledBox.setLayout(topKilledBox.layout) 
        if len(topKilled) > 0:
            topKilledBox.layout.addWidget(HunterLabel(topKilled['blood_line_name']))
            topKilledBox.layout.addWidget(QLabel('Have killed them %d times' % topKilled['kills']))
        return topKilledBox


    def update(self):
        print('updating hunters tab')
        self.layout.removeWidget(self.topHuntersBox)
        self.layout.removeWidget(self.topKilledBox)
        self.layout.removeWidget(self.topKillerBox)
        self.topHuntersBox = self.initTopHunters()
        self.topHuntersBox.setStyleSheet('QGroupBox{padding-top:24px;border:0px;}QGroupBox:title{margin-top:4px;}')
        self.topKillerBox = self.initTopKiller()
        self.topKillerBox.setStyleSheet('QGroupBox{padding-top:24px;border:0px;}QGroupBox:title{margin-top:4px;}')
        self.topKilledBox = self.initTopKilled()
        self.topKilledBox.setStyleSheet('QGroupBox{padding-top:24px;border:0px;}QGroupBox:title{margin-top:4px;}')
        self.layout.addWidget(self.topKilledBox,0,0)
        self.layout.addWidget(self.topKillerBox,0,1)
        self.layout.addWidget(QLabel(),1,1)
        self.layout.addWidget(self.topHuntersBox,2,0,1,2)

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
        topHuntersWidget.layout = QGridLayout()
        topHuntersWidget.setLayout(topHuntersWidget.layout)
        for hunter in topHunters:
            hunterWidget = QWidget()
            hunterWidget.layout = QGridLayout()
            hunterWidget.setLayout(hunterWidget.layout)
            hunterWidget.layout.addWidget(HunterLabel('\'%s\'' % hunter['blood_line_name']),0,0)
            hunterWidget.layout.addWidget(QLabel('Seen in %d hunts' % hunter['count']),1,0)
            row = 0
            if hunter['downedbyme'] > 0 or hunter['killedbyme'] > 0:
                hunterWidget.layout.addWidget(QLabel('Killed them %d times' % (hunter['downedbyme']+hunter['killedbyme'])),row,1)
                row += 1
            if hunter['downedme'] > 0 or hunter['killedme'] > 0:
                hunterWidget.layout.addWidget(QLabel('Killed by them %d times' % (hunter['downedme']+hunter['killedme'])),row,1)
                row += 1
            if hunter['ispartner'] > 0:
                hunterWidget.layout.addWidget(QLabel('Been on their team %d times' % hunter['ispartner']),row,1)

            topHuntersWidget.layout.addWidget(hunterWidget)
            topHuntersWidget.layout.addWidget(QLabel())
        topHuntersBox.layout.addStretch()

        return topHuntersBox