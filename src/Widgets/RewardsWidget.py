from PyQt6.QtWidgets import QWidget, QGridLayout, QLabel, QSizePolicy, QGroupBox
from resources import resource_path, get_icon

icon_size = 24

class RewardsWidget(QGroupBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QGridLayout()
        self.setLayout(self.layout)
        self.setSizePolicy(QSizePolicy.Policy.Minimum,QSizePolicy.Policy.Expanding)
        self.setTitle("Rewards")
        self.setObjectName("RewardsWidget")

        iconNames = ["hunt_dollars","blood_bonds","xp","event_points"]
        self.icons = {name : get_icon(resource_path("assets/icons/rewards/%s.png"%name),x=icon_size,y=icon_size) for name in iconNames}
        for i in range(len(iconNames)):
            icon = self.icons[iconNames[i]]
            icon.setObjectName("icon");
            icon.setStyleSheet("QLabel{border:0px;}")
            #sp = icon.sizePolicy()
            #sp.setRetainSizeWhenHidden(True)
            #icon.setSizePolicy(sp)
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
            if k == "event_points" and rewards[k] == 0:
                self.labels[k].setVisible(False)
                self.icons[k].setVisible(False)
            else:
                self.labels[k].setVisible(True)
                self.icons[k].setVisible(True)

        self.layout.setColumnStretch(self.layout.columnCount(),1)
        self.layout.setRowStretch(self.layout.rowCount(),1)

def getLabel(txt):
    if "_" in txt:
        words = [w[0].capitalize() for w in txt.split("_")]
        return ''.join(words)
    else:
        return txt.upper()
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