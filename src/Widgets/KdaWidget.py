from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QSizePolicy
from PyQt6.QtGui import QPixmap, QColor, QPainter
from DbHandler import execute_query
from resources import settings
from time import time

gameTypes = ["All Hunts","Bounty Hunt","Quick Play"]

class KdaWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.kda = 0.0
        self.kdaLabel = QLabel()
        self.kdaLabel.setObjectName("kdaTitle")
        self.values = QLabel()
        self.button = QPushButton(gameTypes[0])
        self.button.setObjectName("link")
        self.button.clicked.connect(self.toggle)
        self.button.setSizePolicy(QSizePolicy.Policy.Fixed,QSizePolicy.Policy.Fixed)

        self.layout.addWidget(self.kdaLabel)
        self.layout.addWidget(self.values)
        self.layout.addWidget(self.button)
        self.layout.addStretch()

    def toggle(self):
        current = self.button.text()
        self.button.setText(gameTypes[(gameTypes.index(current)+1)%len(gameTypes)])
        self.update()

    def update(self):
        range = int(settings.value("kda_range","-1"))
        game = self.button.text()
        earliest = 0
        if range > -1:
            earliest = int(time() - range)
        condition = "where ts > %d" % earliest

        if game != "All Hunts":
            if game == "Quick Play":
                condition += " and MissionBagIsQuickPlay is 'true'"
            else:
                condition += " and MissionBagIsQuickPlay is 'false'"
        
        kData = execute_query("select downedbyme + killedbyme, 'hunters'.timestamp as ts from 'hunters' join 'games' on 'hunters'.game_id = 'games'.game_id %s" % condition)
        dData = execute_query("select downedme + killedme, 'hunters'.timestamp as ts from 'hunters' join 'games' on 'hunters'.game_id = 'games'.game_id %s" % (condition))
        aData = execute_query("select amount from (select amount, 'entries'.timestamp as ts, MissionBagIsQuickPlay from 'entries' join 'games' on 'games'.game_id = 'entries'.game_id where category is 'accolade_players_killed_assist') %s" % (condition))

        kills = sum(k[0] for k in kData) 
        deaths = max(1,sum(d[0] for d in dData))
        assists = sum(a[0] for a in aData) 

        self.kda = (kills + assists) / deaths
        self.kdaLabel.setText("%.3f" % self.kda)
        self.values.setText("%dk %dd %da" % (kills,deaths,assists))