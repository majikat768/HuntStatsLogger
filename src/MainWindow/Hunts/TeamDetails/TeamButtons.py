from PyQt6.QtWidgets import QScrollArea, QSizePolicy, QWidget, QHBoxLayout, QGroupBox
from PyQt6.QtCore import Qt
from MainWindow.Hunts.TeamDetails.TeamButton import TeamButton

class TeamButtons(QScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWidgetResizable(True)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.main = QGroupBox("Teams")
        self.main.layout = QHBoxLayout()
        self.main.setLayout(self.main.layout)

        self.main.setObjectName("TeamButtons")
        self.setSizePolicy(QSizePolicy.Policy.Minimum,QSizePolicy.Policy.Fixed)

        self.setWidget(self.main)

        self.buttons = []

    def addButton(self,button):
        self.buttons.append(button)
        if button.ownTeam or len(button.icons) > 0:
            self.main.layout.insertWidget(0,button)
        else:
            self.main.layout.addWidget(button)