from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QSizePolicy
from resources import clearLayout

class RewardsWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.setSizePolicy(
            QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)

    def update(self, accolades):
        clearLayout(self.layout)
        rewards = calculateRewards(accolades)
        for k in rewards:
            label = QLabel("%s: %s" % (k,rewards[k]))
            label.setSizePolicy(QSizePolicy.Policy.Fixed,QSizePolicy.Policy.Fixed)
            self.layout.addWidget(label)

def calculateRewards(accolades):
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