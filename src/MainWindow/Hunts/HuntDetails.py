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
        self.rewards = QLabel()
        self.teamKills = QLabel()
        self.yourKills = QLabel()
        self.yourAssists = QLabel()
        self.yourDeaths = QLabel()
        self.monsterKills = QLabel()

        huntDetails.layout.addWidget(self.bounties)
        huntDetails.layout.addWidget(self.nTeams)
        huntDetails.layout.addWidget(self.clues)
        huntDetails.layout.addWidget(self.rewards)
        huntDetails.layout.addWidget(self.teamKills)
        huntDetails.layout.addWidget(self.yourKills)
        huntDetails.layout.addWidget(self.yourDeaths)
        huntDetails.layout.addWidget(self.yourAssists)
        huntDetails.layout.addWidget(self.monsterKills)
        huntDetails.layout.addStretch()
        self.huntDetails = huntDetails

        self.setWidget(huntDetails)

        self.setBaseSize(self.sizeHint())
        self.setMinimumHeight(int(self.sizeHint().height()*1.1))

    def update(self, hunt,entries, accolades):
        #print('huntdetails.update')
        qp = 1 if hunt['MissionBagIsQuickPlay'].lower() == 'true' else 0
        bounties = GetBounties(hunt)
        rewards = calculateRewards(accolades,entries)
        self.rewards.setText(
            "<br>".join(["%s: %s" % (k, rewards[k]) for k in rewards if rewards[k] > 0])
        )
        if not qp:
            self.bounties.setText(" and ".join(bounties))
        else:
            self.bounties.setText('Quick Play')

        self.nTeams.setText("%d %s" % (hunt['MissionBagNumTeams'], "hunters" if qp else "teams"))
        #self.setFixedWidth(int(self.huntDetails.sizeHint().width()*1.1))

        if qp:
            rifts_closed = 0
        else:
            bosses = {
                'assassin': {
                    "clues": 0,
                    "killed": 0,
                    "banished": 0
                },
                'spider': {
                    "clues": 0,
                    "killed": 0,
                    "banished": 0
                },
                'butcher': {
                    "clues": 0,
                    "killed": 0,
                    "banished": 0
                },
                'scrapbeak': {
                    "clues": 0,
                    "killed": 0,
                    "banished": 0
                },
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
            your_kills[mmr] += k[0]
        for d in your_total_deaths:
            mmr = mmr_to_stars(d[1])
            your_deaths[mmr] += d[0]

        monsters_killed = {}
        assists = 0
        for accolade in accolades:
            cat = accolade['category']
            if "killed_" in cat:
                print(cat)
                boss = cat.split("_")[2]
                if boss in bosses:
                    bosses[boss]["killed"] = 1
            if "banished" in cat:
                boss = cat.split("_")[2]
                if boss in bosses:
                    bosses[boss]["banished"] = 1

        for entry in entries:
            cat = entry['category']
            if 'wellsprings_found' in cat:
                rifts_closed += 1
            if 'clues_found' in cat:
                boss = entry['descriptorName'].split(' ')[1]
                bosses[boss]['clues'] += 1
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
            for name in bosses:
                boss = bosses[name]
                if sum(boss.values()) > 0:
                    text.append("<br><b>%s</b>:<br>" % name.capitalize())
                if boss['clues'] > 0:
                    text.append("\tFound %d clues.<br>" % boss['clues'])
                if boss['killed']:
                    text.append("\tKilled.<br>")
                if boss['banished']:
                    text.append("\tBanished.<br>")
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

        self.adjustSize()
        self.window().adjustSize()

def calculateRewards(accolades, entries):
    bounty = 0
    gold = 0
    bb = 0
    xp = 0
    eventPoints = 0

    for acc in accolades:
        bounty += acc['bounty']
        xp += acc['xp']
        bb += acc['generatedGems']
        eventPoints += acc['eventPoints']

    xp += 4*bounty
    gold += bounty
    return {
        'Hunt Dollars':gold,
        'Blood Bonds':bb,
        'XP':xp,
        'Event Points':eventPoints
    }