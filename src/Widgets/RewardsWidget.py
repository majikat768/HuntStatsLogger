from PyQt6.QtWidgets import QWidget, QGridLayout, QLabel, QSizePolicy
from resources import resource_path, get_icon

icon_size = 24

class RewardsWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QGridLayout()
        self.setLayout(self.layout)
        self.setSizePolicy(
            QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)

        iconNames = ["hunt_dollars","blood_bonds","xp","event_points"]
        for i in range(len(iconNames)):
            icon = get_icon(resource_path("assets/icons/rewards/%s.png"%iconNames[i]),x=icon_size,y=icon_size)
            icon.setObjectName("icon");
            icon.setStyleSheet("QLabel{border:0px;}")
            self.layout.addWidget(icon,i,0)

        self.labels = { name : QLabel() for name in iconNames }
        i = 0
        for name in self.labels:
            self.labels[name].setSizePolicy(QSizePolicy.Policy.Fixed,QSizePolicy.Policy.Fixed)
            self.layout.addWidget(self.labels[name],i,1)
            i += 1


    def update(self, accolades):
        rewards = calculateRewards(accolades)
        for k in rewards:
            self.labels[k].setText("  %s: %d" % (getLabel(k), rewards[k]))

def getLabel(txt):
    words = txt.split("_")
    for i in range(len(words)):
        words[i] = words[i].capitalize()
    return " ".join(words)

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
        'hunt_dollars': gold,
        'blood_bonds': bb,
        'xp': xp,
        'event_points': eventPoints
    }