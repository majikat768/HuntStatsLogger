from PyQt5.QtWidgets import QGridLayout, QVBoxLayout,QSpacerItem, QSizePolicy, QWidget, QLabel,QComboBox
from PyQt5.QtCore import QSettings, Qt
from PyQt5 import QtGui
from Connection import MmrToStars
from GroupBox import GroupBox
import HunterLabel

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
        self.setStyleSheet('Hunter{padding:0px;margin:0px};QLabel{padding:0px;margin:0px;}')
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
        self.KDAQLabel.setStyleSheet('QLabel{font-size:36px;}')
        kdaBox.layout.addWidget(self.KDAQLabel,0,2)

        self.missionSelect = QComboBox();
        self.missionSelect.setStyleSheet("QComboBox{font-size:12px;}")
        self.missionSelect.addItem('All Hunts')
        self.missionSelect.addItem('Bounty Hunt')
        self.missionSelect.addItem('Quick Play')
        self.missionSelect.currentIndexChanged.connect(self.UpdateKdaBox)
        kdaBox.layout.addWidget(self.missionSelect,2,2)

        self.deathQLabel = QLabel('%sk %sd %sa' % (self.settings.value('total_kills',-1),self.settings.value('total_deaths',-1),self.settings.value('total_assists',-1)))
        self.deathQLabel.setAlignment(Qt.AlignCenter)
        kdaBox.layout.addWidget(self.deathQLabel,1,2)

        return kdaBox

    def UpdateKdaBox(self):
        gameType = self.missionSelect.currentText();
        kills = self.connection.execute_query(
            "select downedbyme + killedbyme,timestamp from 'hunter' where (downedbyme > 0 or killedbyme > 0)"
        )
        deaths = self.connection.execute_query(
            "select downedme + killedme,timestamp from 'hunter' where (downedme > 0 or killedme > 0)"
        )
        assists = self.connection.execute_query(
            "select amount,timestamp from 'entry' where category is 'accolade_players_killed_assist'"
        )
        if gameType != 'All Hunts':
            valid = [i[0] for i in self.connection.execute_query("select timestamp from 'game' where MissionBagIsQuickPlay is %d" % (0 if gameType == 'Bounty Hunt' else 1))]
            kills = [k for k in kills if k[1] in valid]
            deaths = [d for d in deaths if d[1] in valid]
            assists = [a for a in assists if a[1] in valid]
        

        kills = sum([k[0] for k in kills])
        deaths = sum([d[0] for d in deaths])
        assists = sum([a[0] for a in assists])

        print(kills,deaths,assists)
        if int(deaths) == 0:
            kda = (kills + assists)
        else:
            kda = (kills + assists) / deaths

        self.KDAQLabel.setText('%s' % '{:.3f}'.format(kda))
        self.KDAQLabel.setAlignment(Qt.AlignHCenter)
        self.deathQLabel.setText('%sk %sd %sa' % (kills,deaths,assists))
        self.deathQLabel.setAlignment(Qt.AlignHCenter)

    def HunterBox(self):
        hunterBox = QWidget()
        hunterBox.layout = QVBoxLayout()
        hunterBox.setLayout(hunterBox.layout)

        self.hunterQLabel = HunterLabel.HunterLabel(self.settings.value('hunterName',''))
        self.hunterQLabel.setObjectName('HunterTitle')
        hunterBox.layout.addWidget(self.hunterQLabel)

        self.totalHunts = QLabel('Hunts: %s' % self.settings.value('total_hunts',-1))
        self.level = QLabel('Level 0')
        hunterBox.layout.addWidget(self.totalHunts)
        hunterBox.layout.addWidget(self.level)
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
        self.bestMmrQLabel = QLabel('Best: %d' % self.connection.GetMaxMMR())
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
        self.bestMmrQLabel = QLabel('Best: %d' % self.connection.GetMaxMMR())

    def UpdateHunterBox(self):
        self.hunterQLabel.setText(self.settings.value('hunterName',''))
        self.totalHunts.setText('Hunts: %d' % self.connection.GetTotalHuntCount())
        lvl = self.connection.execute_query("select HunterLevel from 'game' order by timestamp desc limit 1")
        print('lvl',lvl)
        if lvl == None or lvl == [] or lvl == [(None,)]:
            self.level.setText('')
        else:
            self.level.setText('Level %d' % lvl[0][0])

    def update(self):
        self.UpdateHunterBox()
        self.UpdateMmrBox()
        self.UpdateKdaBox()