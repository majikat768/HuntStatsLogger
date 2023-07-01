from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt
from DbHandler import GetTotalHuntCount
from resources import settings

class HunterWidget(QWidget):
    def __init__(self, parent = None):
        super().__init__(parent)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.name = QLabel()
        self.name.setObjectName("HunterTitle")
        self.huntsCount = QLabel()
        self.level = QLabel()

        self.layout.addWidget(self.name)
        self.layout.addWidget(self.huntsCount)
        self.layout.addWidget(self.level)
        self.layout.addStretch()

    def update(self):
        self.name.setText(settings.value("steam_name"))
        self.level.setText("Bloodline %s" % settings.value("HunterLevel","-1"))
        count = str(GetTotalHuntCount())
        lim = settings.value("hunt_limit",False)
        if lim:
            count += " (%s)" % lim
        self.huntsCount.setText("Hunts: %s" % count)