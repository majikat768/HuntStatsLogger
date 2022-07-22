from PyQt5.QtWidgets import QGridLayout, QLabel, QVBoxLayout,QSpacerItem, QSizePolicy
from PyQt5.QtCore import QSettings, Qt
from PyQt5 import QtGui
from Connection import MmrToStars
from GroupBox import GroupBox

class Hunter(GroupBox):
    def __init__(self,parent,layout,title='') -> None:
        super().__init__(layout,title)
        self.parent = parent
        self.connection = parent.connection
        self.setStyleSheet('QLabel{padding:0px;margin:0px;}')
        self.settings = QSettings('majikat','HuntStats')
        self.layout = layout
        self.setLayout(self.layout)
        self.layout.setSpacing(0)
        self.setSizePolicy(QSizePolicy.MinimumExpanding,QSizePolicy.Fixed)

        self.layout.addWidget(self.HunterBox(),0,0,Qt.AlignLeft | Qt.AlignTop)

        self.layout.addWidget(self.MmrBox(),0,2,Qt.AlignRight | Qt.AlignTop)

        self.layout.addWidget(self.KdaBox(),0,1, Qt.AlignHCenter)

        self.layout.setRowStretch(self.layout.rowCount(),1)
        #self.layout.setColumnStretch(self.layout.columnCount(),1)
        self.layout.setColumnStretch(1,1)
    
    def KdaBox(self):
        self.kdaBox = GroupBox(QGridLayout())
        self.kdaBox.setAlignment(Qt.AlignCenter)

        self.connection.SetKDA()
        print(self.settings.value('kda'))
        print(type(self.settings.value('kda')))
        self.KDA = QLabel('%s' % self.settings.value('kda',-1))
        self.KDA.setStyleSheet('QLabel{font-size:32px;}')
        self.kdaBox.addWidget(self.KDA,0,1)
        self.kdaBox.addWidget(QLabel('kda'),1,1)

        self.kdaBox.layout.setRowStretch(2,1)
        self.kdaBox.layout.addItem(QSpacerItem(16,16,QSizePolicy.Expanding,QSizePolicy.Expanding),2,0,1,1)
        self.connection.SetTotalKills()
        self.kills = QLabel('%d' % self.settings.value('total_kills',-1))
        self.kdaBox.addWidget(self.kills,3,0)
        self.kdaBox.addWidget(QLabel('kills'),4,0)

        self.connection.SetTotalDeaths()
        self.deaths = QLabel('%d' % self.settings.value('total_deaths',-1))
        self.kdaBox.addWidget(self.deaths,3,1)
        self.kdaBox.addWidget(QLabel('deaths'),4,1)

        self.connection.SetTotalAssists()
        self.assists = QLabel('%d' % self.settings.value('total_assists',-1))
        self.kdaBox.addWidget(self.assists,3,2)
        self.kdaBox.addWidget(QLabel('assists'),4,2)
        #self.AvgKDA = QLabel('Avg KDA')
        #self.kdaBox.addWidget(self.AvgKDA,5,1)
        self.kdaBox.setBorderVisible(False)

        return self.kdaBox

    def HunterBox(self):
        self.hunterBox = GroupBox(QVBoxLayout())
        self.hunterBox.setBorderVisible(False)

        self.hunterLabel = QLabel(self.settings.value('hunterName',''))
        self.hunterLabel.setObjectName('HunterTitle')
        self.hunterBox.layout.addWidget(self.hunterLabel,Qt.AlignLeft)

        self.connection.SetTotalHuntCount()
        self.totalHunts = QLabel('Hunts: %d' % self.settings.value('total_hunts',-1))
        self.hunterBox.addWidget(self.totalHunts)

        return self.hunterBox

    def MmrBox(self):
        self.mmrBox = GroupBox(QVBoxLayout())
        self.mmrBox.setBorderVisible(False)

        self.connection.SetOwnMMR()
        mmr = self.settings.value('mmr',-1)
        stars = MmrToStars(mmr)
        self.starLabel = QLabel()
        self.starLabel.setPixmap(QtGui.QPixmap('./assets/icons/_%dstar.png' % stars))
        self.starLabel.setAlignment(Qt.AlignRight)
        self.mmrLabel = QLabel('Current MMR: %d' % mmr)
        self.mmrLabel.setAlignment(Qt.AlignRight)
        self.bestMmrLabel = QLabel('Best MMR: %d' % mmr)
        self.bestMmrLabel.setAlignment(Qt.AlignRight)

        self.mmrBox.addWidget(self.starLabel)
        self.mmrBox.addWidget(self.mmrLabel)
        self.mmrBox.addWidget(self.bestMmrLabel)

        return self.mmrBox

    def UpdateHunterBox(self):
        self.hunterLabel.setText(self.settings.value('hunterName',''))