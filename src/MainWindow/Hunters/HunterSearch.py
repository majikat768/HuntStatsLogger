from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QGroupBox, QScrollArea, QLineEdit, QPushButton, QLabel
from PyQt6.QtCore import Qt
from resources import settings, star_path, mmr_to_stars
from DbHandler import GetTopNHunters, GetHunterKills, GetHuntersByPartialName, execute_query, getAllUsernames, SameTeamCount, SameGameCount
from Widgets.Modal import Modal
from Widgets.Label import Label

class HunterSearch(QGroupBox):
    def __init__(self,parent=None):
        super().__init__(parent)
        self.setStyleSheet("*{margin:16px;padding:8px;}")
        self.setTitle("Search Hunters")
        self.layout = QHBoxLayout()
        self.setLayout(self.layout)

        self.searchBar = QLineEdit()
        self.searchBar.setPlaceholderText("Enter Hunter Name")
        self.searchButton = QPushButton("\t\tSearch\t\t")

        self.layout.addWidget(self.searchBar)
        self.layout.addWidget(self.searchButton)
        self.searchBar.returnPressed.connect(self.SubmitSearch)
        self.searchButton.clicked.connect(self.SubmitSearch)

    def SubmitSearch(self):
        name = self.searchBar.text()
        if len(name) <= 0:
            return
        res = GetHuntersByPartialName(name)
        self.ShowResults(res, name)

    def ShowResults(self, huntsPerPlayer, name):
        resultsWindow = Modal(parent=self)
        if len(huntsPerPlayer) <= 0:
            resultsWindow.addWidget(
                Label("You've never encountered %s in a Hunt." % name))
        else:
            for playerHunts in huntsPerPlayer:
                firstHunt = playerHunts[0]
                pid = firstHunt['profileid']
                sameGameCount = SameGameCount(pid)  
                textOutput = ["You've seen %s in %d hunts." % (firstHunt['blood_line_name'], sameGameCount)]

                allnames = getAllUsernames(pid)
                kills = GetHunterKills(pid)
                sameTeamCount = SameTeamCount(pid)

                killedByMe = 0
                killedMe = 0
                for k in kills:
                    killedByMe += (k['killedby'] or 0)
                    killedMe += (k['killed'] or 0)
                
                if len(allnames) > 1:
                    textOutput.append("* They've also gone by:\n%s" % ",".join(allnames))
                if sameTeamCount > 0:
                    textOutput.append("* You've been on their team %d times." % sameTeamCount)
                if killedByMe > 0:
                    textOutput.append("* They've killed you %d times." % killedByMe)
                if killedMe > 0:
                    textOutput.append("* You've killed them %d times." % killedMe)
                label = Label("<br>".join(textOutput))
                label.setAlignment(Qt.AlignmentFlag.AlignLeft)
                resultsWindow.addWidget(label)
        resultsWindow.show()