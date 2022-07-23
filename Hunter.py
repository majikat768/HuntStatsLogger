from PyQt5.QtWidgets import QGridLayout, QLabel, QVBoxLayout,QSpacerItem, QSizePolicy, QWidget
from PyQt5.QtCore import QSettings, Qt
from PyQt5 import QtGui
from Connection import MmrToStars
from GroupBox import GroupBox

class Hunter(GroupBox):
    def __init__(self,parent,layout,title='') -> None:
        super().__init__(layout,title)
        self.parent = parent
        self.connection = parent.connection
        self.settings = QSettings('majikat','HuntStats')
        self.layout = layout
        self.setLayout(self.layout)
        self.layout.setAlignment(Qt.AlignTop)
        self.layout.setSpacing(0)
        self.setSizePolicy(QSizePolicy.MinimumExpanding,QSizePolicy.Fixed)

        self.hunterBox = self.HunterBox()
        self.kdaBox = self.KdaBox()
        self.mmrBox = self.MmrBox()
        self.layout.addWidget(self.hunterBox)
        self.layout.addStretch()
        self.layout.addWidget(self.KdaBox(), Qt.AlignTop)
        self.layout.addStretch()
        self.layout.addWidget(self.MmrBox(), Qt.AlignRight)

        #self.layout.setRowStretch(self.layout.rowCount(),1)
        #self.layout.setColumnStretch(self.layout.columnCount(),1)
        #self.layout.setColumnStretch(1,1)
    
    def KdaBox(self):
        kdaBox = QWidget()
        kdaBox.layout = QGridLayout()
        kdaBox.setLayout(kdaBox.layout)
        kdaBox.layout.setAlignment(Qt.AlignCenter)

        self.KDALabel = QLabel('%s' % self.settings.value('kda',-1))
        self.KDALabel.setAlignment(Qt.AlignCenter)
        self.KDALabel.setStyleSheet('QLabel{font-size:32px;}')
        kdaBox.layout.addWidget(self.KDALabel,1,2)

        self.killLabel = QLabel('%dk' % self.settings.value('total_kills',-1))
        self.killLabel.setAlignment(Qt.AlignCenter)
        kdaBox.layout.addWidget(self.killLabel,3,1)

        self.deathLabel = QLabel('%dd' % self.settings.value('total_deaths',-1))
        self.deathLabel.setAlignment(Qt.AlignCenter)
        kdaBox.layout.addWidget(self.deathLabel,3,2)

        self.assistLabel = QLabel('%da' % self.settings.value('total_assists',-1))
        self.assistLabel.setAlignment(Qt.AlignCenter)
        kdaBox.layout.addWidget(self.assistLabel,3,3)
        #self.AvgKDA = QLabel('Avg KDA')
        #self.kdaBox.addWidget(self.AvgKDA,5,1)
        #kdaBox.layout.setRowStretch(kdaBox.layout.rowCount(),1)
        #kdaBox.layout.setColumnStretch(kdaBox.layout.columnCount(),1)
        #kdaBox.layout.setColumnStretch(0,1)

        return kdaBox

    def UpdateKdaBox(self):
        self.connection.SetKDA()
        print(self.settings.value('kda'))
        self.KDALabel.setText('%s' % '{:.2f}'.format(float(self.settings.value('kda',-1))))
        self.KDALabel.setAlignment(Qt.AlignHCenter)
        self.connection.SetTotalKills()
        self.killLabel.setText('')
        self.killLabel.setAlignment(Qt.AlignHCenter)
        self.connection.SetTotalDeaths()
        self.deathLabel.setText('%dk %dd %da' % (self.settings.value('total_kills',-1),self.settings.value('total_deaths',-1),self.settings.value('total_assists',-1)))
        self.deathLabel.setAlignment(Qt.AlignHCenter)
        self.connection.SetTotalAssists()
        self.assistLabel.setText('')
        self.assistLabel.setAlignment(Qt.AlignHCenter)

    def HunterBox(self):
        hunterBox = QWidget()
        hunterBox.layout = QVBoxLayout()
        hunterBox.setLayout(hunterBox.layout)

        self.hunterLabel = QLabel(self.settings.value('hunterName',''))
        self.hunterLabel.setObjectName('HunterTitle')
        hunterBox.layout.addWidget(self.hunterLabel)

        self.totalHunts = QLabel('Hunts: %d' % self.settings.value('total_hunts',-1))
        hunterBox.layout.addWidget(self.totalHunts)
        hunterBox.layout.addStretch()

        return hunterBox

    def MmrBox(self):
        mmrBox = QWidget()
        mmrBox.layout = QVBoxLayout()
        mmrBox.setLayout(mmrBox.layout)
        mmrBox.layout.setAlignment(Qt.AlignHCenter)

        mmr = self.settings.value('mmr',-1)
        stars = MmrToStars(mmr)
        self.starLabel = QLabel()
        self.starLabel.setPixmap(QtGui.QPixmap('./assets/icons/_%dstar.png' % stars))
        self.starLabel.setAlignment(Qt.AlignRight)
        self.mmrLabel = QLabel('Current MMR: %d' % mmr)
        self.mmrLabel.setAlignment(Qt.AlignRight)
        self.bestMmrLabel = QLabel('Best MMR: %d' % self.connection.GetMaxMMR())
        self.bestMmrLabel.setAlignment(Qt.AlignRight)

        mmrBox.layout.addWidget(self.starLabel)
        mmrBox.layout.addWidget(self.mmrLabel)
        mmrBox.layout.addWidget(self.bestMmrLabel)

        mmrBox.layout.addStretch()
        return mmrBox

    def UpdateMmrBox(self):
        self.connection.SetOwnMMR()
        mmr = self.settings.value('mmr',-1)
        print('mmr',mmr)
        stars = MmrToStars(mmr)
        self.starLabel.setPixmap(QtGui.QPixmap('./assets/icons/_%dstar.png' % stars))
        self.mmrLabel.setText('Current MMR: %d' % mmr)
        self.bestMmrLabel = QLabel('Best MMR: %d' % self.connection.GetMaxMMR())

    def UpdateHunterBox(self):
        self.hunterLabel.setText(self.settings.value('hunterName',''))
        self.connection.SetTotalHuntCount()
        self.totalHunts.setText('Hunts: %d' % self.settings.value('total_hunts',-1))

    def update(self):
        self.UpdateHunterBox()
        self.UpdateMmrBox()
        self.UpdateKdaBox()