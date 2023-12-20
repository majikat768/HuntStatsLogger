from PyQt6.QtCore import Qt
from PyQt6.QtGui import QResizeEvent
from PyQt6.QtWidgets import QWidget, QGridLayout, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QSizePolicy
from resources import settings, stars_pixmap, mmr_to_stars
from DbHandler import get_my_team_data
from Screens.MyTeams.components.AddTeamDialog import AddTeamDialog
from Screens.MyTeams.components.TeamWidget import TeamWidget 

class MyTeams(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground)      
        self.setObjectName("MyTeamsWidget")

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.dialog = AddTeamDialog()

        self.nCols = 3

        addTeamButton = QPushButton("Add Team")
        addTeamButton.clicked.connect(self.startAddTeam)
        addTeamButton.setSizePolicy(QSizePolicy.Policy.Fixed,QSizePolicy.Policy.Fixed)
        self.layout.addWidget(addTeamButton)

        self.my_teams = eval(settings.value("my_teams","[]"))


        self.main = QWidget()
        self.main.setAttribute(Qt.WidgetAttribute.WA_StyledBackground)      
        self.main.setObjectName("MyTeamsWidget")
        self.main.layout = QGridLayout()
        self.main.setLayout(self.main.layout)
        self.layout.addWidget(self.main)
        self.widgets = []
        self.update()
        self.layout.addStretch()

    def update(self):
        self.widgets = []
        self.my_teams = eval(settings.value("my_teams","[]"))
        for i in range(len(self.my_teams)):
            team = self.my_teams[i]
            teamdata = get_my_team_data(team)
            if teamdata != None:
                self.widgets.append(TeamWidget(teamdata,team,i))
        self.widgets = list(reversed(sorted(self.widgets, key=lambda x : x.winPrc)))
        for i in range(len(self.widgets)):
            self.widgets[i].setRank(i)
            self.main.layout.addWidget(self.widgets[i],i//self.nCols,i%self.nCols)

    def startAddTeam(self):
        if self.dialog.exec():
            # do something here ? nah
            pass

    def adjustLayout(self,size):
        if len(self.widgets) > 0:
            n = int(size.width() // (self.widgets[0].minimumSizeHint().width()*1.2))
            if self.nCols != n:
                self.nCols = n
                for i in range(len(self.widgets)):
                    widget = self.widgets[i]
                    self.main.layout.addWidget(widget,i//n,i%n)
                self.main.layout.setRowStretch(self.main.layout.rowCount(),1)

    def resizeEvent(self, a0: QResizeEvent) -> None:
        return super().resizeEvent(a0)
