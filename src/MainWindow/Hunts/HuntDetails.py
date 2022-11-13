from PyQt6.QtWidgets import QWidget, QGroupBox, QHBoxLayout, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt
from resources import *
from DbHandler import *


class HuntDetails(QGroupBox):
    def __init__(self, title=None):
        super().__init__(title)
        # self.setWidgetResizable(True)
        # self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.setObjectName("huntDetails")
        self.layout = QHBoxLayout()
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.setLayout(self.layout)

        self.bounties = self.initBounties()
        self.rewards = self.initRewards()
        self.monsters = self.initMonsters()
        self.layout.addWidget(self.bounties)
        self.layout.setAlignment(self.bounties, Qt.AlignmentFlag.AlignTop)
        self.layout.addStretch()
        self.layout.addWidget(self.rewards)
        self.layout.setAlignment(self.rewards, Qt.AlignmentFlag.AlignTop)
        self.layout.addStretch()
        self.layout.addWidget(self.monsters)
        self.layout.setAlignment(self.monsters, Qt.AlignmentFlag.AlignTop)

        self.setSizePolicy(QSizePolicy.Policy.Expanding,
                           QSizePolicy.Policy.Fixed)

        self.setBaseSize(self.sizeHint())
        self.setFixedHeight(int(self.sizeHint().height()*1.1))

    def initBounties(self):
        self.bounties = QLabel()
        self.bounties.setSizePolicy(
            QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        return self.bounties

    def initRewards(self):
        self.rewards = QLabel()
        self.rewards.setSizePolicy(
            QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        return self.rewards

    def initMonsters(self):
        self.monsters = QLabel()
        self.monsters.setSizePolicy(
            QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        return self.monsters

    def updateBounties(self, qp, bounties, targets):
        text = []
        if qp:
            text.append("Quick Play")
            text.append("closed %d rifts." % bounties['rifts_closed'])
        else:
            for name in targets:
                boss = bounties[name.lower()]
                text.append("%s:" % name.capitalize())
                if sum(boss.values()) > 0:
                    if boss['clues'] > 0:
                        text.append(tab+"Found %d clues." % boss['clues'])
                    if boss['killed']:
                        text.append(tab+"Killed.")
                    if boss['banished']:
                        text.append(tab+"Banished.")
                    text.append('')
                text.append('')
        self.bounties.setText("<br>".join(text))

    def updateRewards(self, rewardsData):
        self.rewards.setText("Rewards:<br>%s" % ("<br>".join(
            [tab+"%s: %s" % (k, rewardsData[k]) for k in rewardsData if rewardsData[k] > 0])))

    def updateMonsters(self, monsters_killed):
        n = sum(monsters_killed.values())
        values = [tab+"%d %s" % (monsters_killed[m], m)
                  for m in monsters_killed if monsters_killed[m] > 0]
        monsters_killed = {}
        text = "Monster kills: %d<br>%s" % (
            n,
            '<br>'.join(values)
        )
        self.monsters.setText(text)

    def update(self, qp, bounties, rewards, monsters_killed, targets):
        self.updateBounties(qp, bounties, targets)
        self.updateRewards(rewards)
        self.updateMonsters(monsters_killed)
        self.setFixedHeight(self.sizeHint().height())

    def clearLayout(self, layout):
        for i in reversed(range(layout.count())):
            layout.itemAt(i).widget().setParent(None)


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
        'Hunt Dollars': gold,
        'Blood Bonds': bb,
        'XP': xp,
        'Event Points': eventPoints
    }
