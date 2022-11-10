from PyQt6.QtWidgets import QGroupBox, QHBoxLayout, QVBoxLayout, QLabel, QWidget, QSizePolicy, QPushButton
from PyQt6.QtCore import Qt

from resources import settings
from DbHandler import *

gameTypes = ["All Hunts","Bounty Hunt","Quick Play"]

class Header(QGroupBox):
    def __init__(self,parent=None):
        super().__init__(parent)
        self.layout = QHBoxLayout()
        self.setLayout(self.layout)

        self.setObjectName("Header")

        self.initUI()
        self.setMaximumHeight(self.sizeHint().height())
        self.setSizePolicy(QSizePolicy.Policy.Minimum,QSizePolicy.Policy.Maximum)


    def initUI(self):
        self.initKdaBox()
        self.layout.addStretch()
        self.initHunterBox()
        self.layout.addStretch()
        self.initMmrBox()


    def update(self):
        #print('header.update')
        self.updateHunterBox()
        self.updateMmrBox()
        self.updateKdaBox()

    def updateHunterBox(self):
        #print('hunterbox.update')
        self.name.setText(settings.value("steam_name"))
        self.level.setText("level %s" % settings.value("HunterLevel","-1"))
        self.huntsCount.setText("Hunts: %d" % GetTotalHuntCount())
    
    def updateMmrBox(self):
        self.mmr.setText("MMR: %d" % GetCurrentMmr())
        self.bestMmr.setText("Best: %d" % GetBestMmr())

    def updateKdaBox(self):
        timeRange = int(settings.value("kda_range","-1"))
        earliest = 0
        if timeRange > -1:
            earliest = int(time.time() - timeRange)
        condition = "where ts > %d" % earliest
        if self.gameTypeButton.text() != "All Hunts":
            if self.gameTypeButton.text() == "Quick Play":
                condition += " and MissionBagIsQuickPlay is 'true'"
            else:
                condition += " and MissionBagIsQuickPlay is 'false'"

        kData = execute_query("select downedbyme + killedbyme, 'hunters'.timestamp as ts from 'hunters' join 'games' on 'hunters'.game_id = 'games'.game_id %s" % condition)
        dData = execute_query("select downedme + killedme, 'hunters'.timestamp as ts from 'hunters' join 'games' on 'hunters'.game_id = 'games'.game_id %s" % (condition))
        aData = execute_query("select amount from (select amount, 'entries'.timestamp as ts, MissionBagIsQuickPlay from 'entries' join 'games' on 'games'.game_id = 'entries'.game_id where category is 'accolade_players_killed_assist') %s" % (condition))

        kills = sum(k[0] for k in kData) 
        deaths = max(1,sum(d[0] for d in dData))
        assists = sum(a[0] for a in aData) 

        kda = (kills + assists) / deaths

        self.kda.setText("%.3f" % kda)
        self.kdaValues.setText("%dk %dd %da" % (kills,deaths,assists))

    def initHunterBox(self):
        self.HunterBox = box()

        self.name = QLabel(settings.value("steam_name","Hunter"))
        self.name.setObjectName("HunterTitle")
        self.name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.huntsCount = QLabel("Hunts: %d" % GetTotalHuntCount())
        self.huntsCount.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.level = QLabel("level %s" % settings.value("HunterLevel","-1"))
        self.level.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.HunterBox.layout.addWidget(self.name)
        self.HunterBox.layout.addWidget(self.level)
        self.HunterBox.layout.addWidget(self.huntsCount)
        self.HunterBox.layout.addStretch()

        self.layout.addWidget(self.HunterBox)

    def initMmrBox(self):
        self.MmrBox = box()
        mmr = GetCurrentMmr()
        self.stars = QLabel("<img src='%s'>" % (star_path()) * mmr_to_stars(mmr))
        self.stars.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.mmr = QLabel("MMR: %d" % mmr)
        self.mmr.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.bestMmr = QLabel("Best: %d" % GetBestMmr())
        self.bestMmr.setAlignment(Qt.AlignmentFlag.AlignRight)

        self.MmrBox.layout.addWidget(self.stars)
        self.MmrBox.layout.addWidget(self.mmr)
        GetCurrentMmr()
        self.MmrBox.layout.addWidget(self.bestMmr)
        self.MmrBox.layout.addStretch()

        self.layout.addWidget(self.MmrBox)

    def initKdaBox(self):
        self.KdaBox = box()

        self.kda = QLabel("0.000")
        self.kda.setObjectName("kdaTitle")
        self.kda.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.kdaValues = QLabel("0k 0d 0a")
        self.kdaValues.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.gameTypeButton = QPushButton("All Hunts")
        self.gameTypeButton.setObjectName("link")
        self.gameTypeButton.clicked.connect(self.toggleKda)
        self.gameTypeButton.setSizePolicy(QSizePolicy.Policy.Maximum,QSizePolicy.Policy.Maximum)

        self.KdaBox.layout.addWidget(self.kda)
        self.KdaBox.layout.addWidget(self.kdaValues)
        self.KdaBox.layout.addWidget(self.gameTypeButton)
        self.KdaBox.layout.addStretch()

        self.layout.addWidget(self.KdaBox)

    def toggleKda(self):
        current = self.gameTypeButton.text()
        self.gameTypeButton.setText(gameTypes[(gameTypes.index(current)+1)%len(gameTypes)])
        print(self.gameTypeButton.text())
        self.updateKdaBox()

def box():
    box = QWidget()
    box.layout = QVBoxLayout()
    box.setLayout(box.layout)

    return box