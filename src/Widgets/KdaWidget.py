from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QSizePolicy
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
        game = self.button.text()
        condition = ""
        if game != "All Hunts":
            if game == "Quick Play":
                condition += "where MissionBagIsQuickPlay is 'true'"
            else:
                condition += "where MissionBagIsQuickPlay is 'false'"
        
        kData = execute_query("select downedbyme + killedbyme, 'hunters_view'.timestamp as ts from 'hunters_view' join 'games_view' on 'hunters_view'.game_id = 'games_view'.game_id %s" % condition)
        dData = execute_query("select downedme + killedme, 'hunters_view'.timestamp as ts from 'hunters_view' join 'games_view' on 'hunters_view'.game_id = 'games_view'.game_id %s" % (condition))
        aData = execute_query("select amount from (select 'entries_view'.amount, 'entries_view'.timestamp as ts from 'entries_view' join 'games_view' on 'games_view'.game_id = 'entries_view'.game_id where category is 'accolade_players_killed_assist' %s)" % (condition.replace('where','and')))

        kills = sum(k[0] for k in kData) 
        deaths = max(1,sum(d[0] for d in dData))
        assists = sum(a[0] for a in aData) 

        self.kda = (kills + assists) / deaths
        self.kdaLabel.setText("%.3f" % self.kda)
        self.values.setText("%dk %dd %da" % (kills,deaths,assists))