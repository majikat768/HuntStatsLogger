from PyQt6.QtWidgets import QWidget, QGridLayout, QVBoxLayout, QLabel,QSizePolicy,QSpacerItem, QGroupBox
from PyQt6.QtCore import Qt
from DbHandler import GetHuntAccolades 
from resources import get_icon

class RewardsWidget(QGroupBox):
    def __init__(self, game_id, parent: QWidget | None = None):
        super().__init__(parent)
        self.game_id = game_id

        self.data = {}
        self.setTitle("Rewards")
        self.setObjectName("RewardsWidget")
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.layout.setContentsMargins(0,6,0,0)
        self.layout.setSpacing(2)

        self.main = QWidget()
        self.main.layout = QGridLayout()
        self.main.layout.setContentsMargins(8,8,8,8)
        self.main.setLayout(self.main.layout)

        self.layout.addWidget(self.main)

    def init(self):
        if len(self.data) == 0:
            accolades = GetHuntAccolades(self.game_id)

            rewards = {
                'Hunt Dollars':0,
                'XP':0,
                'Blood Bonds':0,
                'Event Points':0,
            }
            for acc in accolades:
                rewards['Hunt Dollars'] += acc['bounty']
                rewards['XP'] += acc['xp']
                rewards['Blood Bonds'] += acc['generatedGems']
                rewards['Event Points'] += acc['eventPoints']

            rewards['XP'] += 4*rewards['Hunt Dollars']

            i = 0
            j = 0
            for reward in rewards:
                if reward == 'Event Points' and rewards[reward] == 0:
                    continue
                ic = get_icon(path="assets/icons/rewards/%s.png" % reward,height=24)
                ic.setToolTip(reward)
                self.main.layout.addWidget(ic,i,j)
                j += 1
                self.main.layout.addWidget(QLabel(str(rewards[reward])),i,j,alignment=Qt.AlignmentFlag.AlignRight)
                j += 2
                if j == 6:
                    i += 1
                    j = 0
            self.main.layout.setColumnStretch(2,1)
            self.main.layout.setRowStretch(self.main.layout.rowCount(),1)