from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QSizePolicy
from PyQt6.QtCore import Qt
from resources import clearLayout, star_path, debug
from DbHandler import getKillData

class KillsWidget(QWidget):
    def __init__(self, parent = None):
        super().__init__(parent)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.setSizePolicy(QSizePolicy.Policy.Minimum,QSizePolicy.Policy.Fixed)

    def update(self,isQp,ts,mmrChange):
        if debug:
            print("teamdetails.update")
        kills = getKillData(ts)
        clearLayout(self.layout)
        team_kills = kills['team_kills']
        your_kills = kills['your_kills']
        your_deaths = kills['your_deaths']
        assists = kills['assists']
        if not isQp:
            teamKills = QLabel(
                "Team kills: %d<br>%s" % (
                    sum(team_kills.values()),
                    '<br>'.join(["%sx %s" % (
                        team_kills[stars],
                        "<img src='%s'>" % (star_path())*stars
                    ) for stars in team_kills.keys() if team_kills[stars] > 0])
                )
            )
            self.layout.addWidget(teamKills)

        yourKills = QLabel(
            "Your kills: %d<br>%s" % (
                sum(your_kills.values()),
                '<br>'.join(["%sx %s" % (
                    your_kills[stars],
                    "<img src='%s'>" % (star_path())*stars
                ) for stars in your_kills.keys() if your_kills[stars] > 0])
            )
        )
        self.layout.addWidget(yourKills)
        self.layout.setAlignment(yourKills,Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)

        yourDeaths = QLabel(
            "Your deaths: %d<br>%s" % (
                sum(your_deaths.values()),
                '<br>'.join(["%sx %s" % (
                    your_deaths[stars],
                    "<img src='%s'>" % (star_path())*stars
                ) for stars in your_deaths.keys() if your_deaths[stars] > 0])
            )
        )
        self.layout.addWidget(yourDeaths)
        self.layout.setAlignment(yourDeaths,Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)

        yourAssists = QLabel("%d assists." % assists)
        self.layout.addWidget(yourAssists)
        self.layout.setAlignment(yourAssists,Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)

        mmrChangeLabel = QLabel(mmrChange)
        self.layout.addWidget(mmrChangeLabel)
        self.layout.setAlignment(mmrChangeLabel,Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self.layout.addStretch()