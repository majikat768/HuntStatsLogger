from PyQt6.QtWidgets import QScrollArea, QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt
from resources import *
from DbHandler import *

class HuntDetails(QScrollArea):
    def __init__(self):
        super().__init__()
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        huntDetails = QWidget()
        huntDetails.setObjectName("HuntDetails")
        huntDetails.layout = QVBoxLayout()
        huntDetails.setLayout(huntDetails.layout)

        self.bounties = QLabel()
        self.bounties.setWordWrap(True)
        self.nTeams = QLabel()
        self.nTeams.setWordWrap(True)
        self.clues = QLabel()
        self.clues.setWordWrap(True)
        self.teamKills = QLabel()
        self.yourKills = QLabel()
        self.yourAssists = QLabel()
        self.yourDeaths = QLabel()
        self.monsterKills = QLabel()

        huntDetails.layout.addWidget(self.bounties)
        huntDetails.layout.addWidget(self.nTeams)
        huntDetails.layout.addWidget(self.clues)
        huntDetails.layout.addWidget(QLabel())
        huntDetails.layout.addWidget(self.teamKills)
        huntDetails.layout.addWidget(QLabel())
        huntDetails.layout.addWidget(self.yourKills)
        huntDetails.layout.addWidget(QLabel())
        huntDetails.layout.addWidget(self.yourDeaths)
        huntDetails.layout.addWidget(QLabel())
        huntDetails.layout.addWidget(self.yourAssists)
        huntDetails.layout.addWidget(QLabel())
        huntDetails.layout.addWidget(self.monsterKills)
        huntDetails.layout.addStretch()
        self.huntDetails = huntDetails

        self.setWidget(huntDetails)

    def update(self, hunt,entries):
        #print('huntdetails.update')
        qp = 1 if hunt['MissionBagIsQuickPlay'].lower() == 'true' else 0
        bounties = GetBounties(hunt)
        if not qp:
            self.bounties.setText("Bounties: " + ' and '.join(bounties))
        else:
            self.bounties.setText('Quick Play')

        self.nTeams.setText("%d %s" % (hunt['MissionBagNumTeams'], "hunters" if qp else "teams"))
        self.setFixedWidth(int(self.huntDetails.sizeHint().width()*1.1))

        if qp:
            rifts_closed = 0
        else:
            clues_found = {
                'assassin':0,
                'spider':0,
                'butcher':0,
                'scrapbeak':0
            }
        team_kills = {
            0:0,
            1:0,
            2:0,
            3:0,
            4:0,
            5:0,
            6:0,
        }
        your_kills = {
            0:0,
            1:0,
            2:0,
            3:0,
            4:0,
            5:0,
            6:0
        }
        your_deaths = {
            0:0,
            1:0,
            2:0,
            3:0,
            4:0,
            5:0,
            6:0
        }
        your_total_kills = execute_query("select downedbyme+killedbyme,mmr from 'hunters' where timestamp is %d and (downedbyme > 0 or killedbyme > 0)" % hunt['timestamp'])
        your_total_deaths = execute_query("select downedme+killedme,mmr from 'hunters' where timestamp is %d and (downedme > 0 or killedme > 0)" % hunt['timestamp'])
        for k in your_total_kills:
            mmr = mmr_to_stars(k[1])
            your_kills[mmr] = k[0]
        for d in your_total_deaths:
            mmr = mmr_to_stars(d[1])
            your_deaths[mmr] = d[0]

        monsters_killed = {}
        assists = 0

        for entry in entries:
            cat = entry['category']
            if 'wellsprings_found' in cat:
                rifts_closed += 1
            if 'clues_found' in cat:
                clues_found[entry['descriptorName'].split(' ')[1]] += 1
            if 'players_killed' in cat:
                if 'assist' in cat:
                    assists += entry['amount']
                elif 'mm rating' in entry['descriptorName']:
                    stars = int(entry['descriptorName'].split(' ')[4])
                    team_kills[stars] += entry['amount']
            if 'monsters_killed' in cat:
                monster = entry['descriptorName'].split(' ')[1]
                if monster not in monsters_killed.keys():
                    monsters_killed[monster] = 0
                monsters_killed[monster] += entry['amount']
        if qp:
            self.clues.setText('closed %d rifts.' % rifts_closed)
        else:
            text = []
            for boss in clues_found:
                if clues_found[boss] > 0:
                    text.append("Found %d of the clues for %s." % (clues_found[boss],boss.capitalize()))
            self.clues.setText('\n'.join(text))

        if not qp:
            self.teamKills.setText(
                "Team kills: %d<br>%s" % (
                    sum(team_kills.values()),
                    '<br>'.join(["%sx %s" % (
                            team_kills[stars],
                            "<img src='%s'>"%(star_path())*stars
                        ) for stars in team_kills.keys() if team_kills[stars] > 0])
                )
            )
        else:
            self.teamKills.setText('')

        self.yourKills.setText(
            "Your kills: %d<br>%s" % (
                sum(your_kills.values()),
                '<br>'.join(["%sx %s" % (
                        your_kills[stars],
                        "<img src='%s'>"%(star_path())*stars
                    ) for stars in your_kills.keys() if your_kills[stars] > 0])
            )
        )

        self.yourAssists.setText("%d assists." % assists)
        self.yourDeaths.setText(
            "Your deaths: %d<br>%s" % (
                sum(your_deaths.values()),
                '<br>'.join(["%sx %s" % (
                        your_deaths[stars],
                        "<img src='%s'>"%(star_path())*stars
                    ) for stars in your_deaths.keys() if your_deaths[stars] > 0])
            )
        )

        self.monsterKills.setText(
            "Monster kills: %d<br>%s" % (
                sum(monsters_killed.values()),
                '<br>'.join(["%d %s" % (monsters_killed[m], m) for m in monsters_killed if monsters_killed[m] > 0])
                )
            )