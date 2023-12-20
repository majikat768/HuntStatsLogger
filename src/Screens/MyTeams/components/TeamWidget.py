from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QGridLayout, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QSizePolicy
from resources import stars_pixmap, mmr_to_stars


class TeamWidget(QWidget):
    def __init__(self, teamData, profileids, team_num, parent: QWidget | None = None):
        super().__init__(parent)
        self.teamData = teamData
        self.profileids = profileids
        self.setObjectName("MyTeamWidget")
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Fixed,
        )
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(4,0,0,0)
        if len(teamData) == 0:
            return

        last_hunt = teamData[0]

        titleWidget = QWidget()
        titleWidget.setObjectName("TeamTitle")
        titleWidget.layout = QHBoxLayout()
        titleWidget.setLayout(titleWidget.layout)
        titleWidget.layout.addWidget(QLabel("Team %d" % (team_num+1)),stretch=1)
        titleWidget.layout.addWidget(QLabel(str(last_hunt['team_mmr'])),alignment=Qt.AlignmentFlag.AlignRight)
        self.layout.addWidget(titleWidget)

        huntersWidget = QWidget()
        huntersWidget.setObjectName("TeamBody")
        huntersWidget.layout = QGridLayout()
        huntersWidget.setLayout(huntersWidget.layout)
        for i in range(3):
            if i < len(profileids):
                huntersWidget.layout.addWidget(QLabel(last_hunt["p%d_name" % (i+1)]),i,0)
                stars = QLabel()
                stars.setPixmap(stars_pixmap(mmr_to_stars(last_hunt["p%d_mmr"%(i+1)]),h=12))
                huntersWidget.layout.addWidget(stars,i,1)
                huntersWidget.layout.addWidget(QLabel(str(last_hunt["p%d_mmr"%(i+1)])),i,2)
            else:
                huntersWidget.layout.addWidget(QLabel(),i,0,1,4)
        huntersWidget.layout.setColumnStretch(0,1)

        extractions = self.n_extractions()
        wins = self.n_wins()
        self.extPrc = "%.2f%%" % ((extractions / len(teamData))*100)
        self.winPrc = "%.2f%%" % ((wins / len(teamData))*100)
        detailsWidget = QWidget()
        detailsWidget.setObjectName("TeamDetails")
        detailsWidget.layout = QGridLayout()
        detailsWidget.setLayout(detailsWidget.layout)
        detailsWidget.layout.setSpacing(0)
        detailsWidget.layout.setContentsMargins(4,4,4,16)
        detailsWidget.layout.addWidget(QLabel("Played"),0,0,1,2)
        detailsWidget.layout.addWidget(QLabel(str(len(teamData))),0,2,1,1,alignment=Qt.AlignmentFlag.AlignRight)
        detailsWidget.layout.addWidget(QLabel("Extracted"),1,0,1,2)
        detailsWidget.layout.addWidget(QLabel(str(extractions)),1,2,1,1,alignment=Qt.AlignmentFlag.AlignRight)
        detailsWidget.layout.addWidget(QLabel("Wins"),2,0,1,2)
        detailsWidget.layout.addWidget(QLabel(str(wins)),2,2,1,1,alignment=Qt.AlignmentFlag.AlignRight)
        detailsWidget.layout.addWidget(QLabel("Extract %"),3,0,1,2)
        detailsWidget.layout.addWidget(QLabel(str(self.extPrc)),3,2,1,1,alignment=Qt.AlignmentFlag.AlignRight)
        detailsWidget.layout.addWidget(QLabel("Win %"),4,0,1,2)
        detailsWidget.layout.addWidget(QLabel(str(self.winPrc)),4,2,1,1,alignment=Qt.AlignmentFlag.AlignRight)
        #detailsWidget.layout.addWidget(QLabel("Wins/Extracts"),5,0,1,1)
        #detailsWidget.layout.addWidget(QLabel("%.2f%%" % ((wins/max(1,extractions))*100)),5,1,1,1,alignment=Qt.AlignmentFlag.AlignRight)

        rankWidget = QWidget()
        rankWidget.layout = QVBoxLayout()
        rankWidget.setLayout(rankWidget.layout)
        rankWidget.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )
        l = QLabel("Rank")
        rankWidget.layout.addWidget(l,alignment=Qt.AlignmentFlag.AlignCenter,stretch=1)
        self.rankLabel = QLabel("0")
        self.rankLabel.setObjectName("MyTeamRankLabel")
        rankWidget.layout.addWidget(self.rankLabel,alignment=Qt.AlignmentFlag.AlignCenter,stretch=2)
        btn = QPushButton("Analytics")
        btn.setSizePolicy(
            QSizePolicy.Policy.Fixed,
            QSizePolicy.Policy.Fixed,
        )
        btn.setDisabled(True)
        rankWidget.layout.addWidget(btn,alignment=Qt.AlignmentFlag.AlignCenter,stretch=1)
        detailsWidget.layout.addWidget(rankWidget,0,3,5,4,alignment=Qt.AlignmentFlag.AlignCenter)

        self.layout.addWidget(huntersWidget)
        self.layout.addWidget(detailsWidget)

    def setRank(self,rank):
        self.rankLabel.setText(str(rank+1))
    
    def n_extractions(self):
        n = 0
        for hunt in self.teamData:
            if hunt['p1_teamextract'] == 'true': 
                if len(self.profileids) > 1:
                    if hunt['p2_teamextract'] == 'true':
                        if len(self.profileids) == 3:
                            if hunt['p3_teamextract'] == 'true':
                                n += 1
                        else:
                            n += 1
                else:
                    n += 1
        return n

    def n_wins(self):
        n = 0
        for hunt in self.teamData:
            if hunt['p1_bountyextract'] > 0:
                n += 1
            elif len(self.profileids) > 1 and hunt['p2_bountyextract'] > 0:
                n += 1
            elif len(self.profileids) == 3 and hunt['p3_bountyextract'] > 0:
                n += 1
        return n



