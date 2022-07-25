from PyQt5.QtWidgets import QGridLayout, QVBoxLayout,QSpacerItem, QSizePolicy, QWidget, QLabel,QComboBox
from PyQt5.QtCore import QSettings, Qt
from PyQt5 import QtGui
from Connection import MmrToStars
from GroupBox import GroupBox

class Hunter(GroupBox):
    def __init__(self,parent,layout,title='') -> None:
        super().__init__(layout,title)
        self.parent = parent
        self.connection = parent.connection
        self.settings = QSettings('./settings.ini',QSettings.Format.IniFormat)
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

        self.KDAQLabel = QLabel('%s' % self.settings.value('kda',-1))
        self.KDAQLabel.setAlignment(Qt.AlignCenter)
        self.KDAQLabel.setStyleSheet('QLabel{font-size:48px;}')
        kdaBox.layout.addWidget(self.KDAQLabel,1,2)

        self.killQLabel = QLabel('%sk' % self.settings.value('total_kills',-1))
        self.killQLabel.setAlignment(Qt.AlignCenter)
        kdaBox.layout.addWidget(self.killQLabel,3,1)

        self.deathQLabel = QLabel('%sd' % self.settings.value('total_deaths',-1))
        self.deathQLabel.setAlignment(Qt.AlignCenter)
        kdaBox.layout.addWidget(self.deathQLabel,3,2)

        self.assistQLabel = QLabel('%sa' % self.settings.value('total_assists',-1))
        self.assistQLabel.setAlignment(Qt.AlignCenter)
        kdaBox.layout.addWidget(self.assistQLabel,3,3)
        #self.AvgKDA = QLabel('Avg KDA')
        #self.kdaBox.addWidget(self.AvgKDA,5,1)
        #kdaBox.layout.setRowStretch(kdaBox.layout.rowCount(),1)
        #kdaBox.layout.setColumnStretch(kdaBox.layout.columnCount(),1)
        #kdaBox.layout.setColumnStretch(0,1)

        return kdaBox

    def UpdateKdaBox(self):
        self.connection.SetKDA()
        self.KDAQLabel.setText('%s' % '{:.2f}'.format(float(self.settings.value('kda',-1))))
        self.KDAQLabel.setAlignment(Qt.AlignHCenter)
        self.connection.SetTotalKills()
        self.killQLabel.setText('')
        self.killQLabel.setAlignment(Qt.AlignHCenter)
        self.connection.SetTotalDeaths()
        self.deathQLabel.setText('%sk %sd %sa' % (self.settings.value('total_kills',-1),self.settings.value('total_deaths',-1),self.settings.value('total_assists',-1)))
        self.deathQLabel.setAlignment(Qt.AlignHCenter)
        self.connection.SetTotalAssists()
        self.assistQLabel.setText('')
        self.assistQLabel.setAlignment(Qt.AlignHCenter)

    def HunterBox(self):
        hunterBox = QWidget()
        hunterBox.layout = QVBoxLayout()
        hunterBox.setLayout(hunterBox.layout)

        self.hunterQLabel = QLabel(self.settings.value('hunterName',''))
        self.hunterQLabel.setObjectName('HunterTitle')
        hunterBox.layout.addWidget(self.hunterQLabel)

        self.totalHunts = QLabel('Hunts: %s' % self.settings.value('total_hunts',-1))
        hunterBox.layout.addWidget(self.totalHunts)
        hunterBox.layout.addStretch()

        return hunterBox

    def MmrBox(self):
        mmrBox = QWidget()
        mmrBox.layout = QVBoxLayout()
        mmrBox.setLayout(mmrBox.layout)
        mmrBox.layout.setAlignment(Qt.AlignHCenter)

        mmr = int(self.settings.value('mmr',-1))
        stars = MmrToStars(mmr)
        self.starQLabel = QLabel()
        self.starQLabel.setPixmap(QtGui.QPixmap('./assets/icons/_%dstar.png' % stars))
        self.starQLabel.setAlignment(Qt.AlignRight)
        self.mmrQLabel = QLabel('MMR: %d' % mmr)
        self.mmrQLabel.setAlignment(Qt.AlignRight)
        self.bestMmrQLabel = QLabel('Best MMR: %d' % self.connection.GetMaxMMR())
        self.bestMmrQLabel.setAlignment(Qt.AlignRight)

        mmrBox.layout.addWidget(self.starQLabel)
        mmrBox.layout.addWidget(self.mmrQLabel)
        mmrBox.layout.addWidget(self.bestMmrQLabel)

        mmrBox.layout.addStretch()
        return mmrBox

    def UpdateMmrBox(self):
        self.connection.SetOwnMMR()
        mmr = int(self.settings.value('mmr',-1))
        print('mmr',mmr)
        stars = MmrToStars(mmr)
        self.starQLabel.setPixmap(QtGui.QPixmap('./assets/icons/_%dstar.png' % stars))
        self.mmrQLabel.setText('MMR: %d' % mmr)
        self.bestMmrQLabel = QLabel('Best MMR: %d' % self.connection.GetMaxMMR())

    def UpdateHunterBox(self):
        self.hunterQLabel.setText(self.settings.value('hunterName',''))
        self.totalHunts.setText('Hunts: %d' % self.connection.GetTotalHuntCount())

    def update(self):
        self.UpdateHunterBox()
        self.UpdateMmrBox()
        self.UpdateKdaBox()