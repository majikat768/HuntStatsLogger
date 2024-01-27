from PyQt6.QtWidgets import QWidget, QVBoxLayout, QSizePolicy, QTreeWidget, QTreeWidgetItem, QGridLayout, QLabel, QHBoxLayout, QComboBox
from PyQt6.QtGui import QPixmap, QIcon
from PyQt6.QtCore import QSize, Qt
from datetime import datetime
from resources import resource_path, tab, comboBoxStyle
from DbHandler import get_n_hunts
from Screens.HuntsRecap.HuntsList import HuntList
from Screens.HuntsRecap.components.HuntWidget import HuntWidget
from Screens.HuntsRecap.HuntPicker import HuntPicker

n = 25

class HuntsRecap(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.setMouseTracking(True)
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0,0,0,0)
        self.main = QWidget()
        self.main.layout = QVBoxLayout()
        self.main.setLayout(self.main.layout)
        self.main.layout.setSpacing(0)
        self.main.layout.setContentsMargins(0,0,0,0)
        self.widget = None
        self.setSizePolicy(QSizePolicy.Policy.Expanding,QSizePolicy.Policy.Expanding)

        self.setObjectName("HuntsRecap")

        #self.hunt_list_widget = HuntList()
        self.initHuntSelect()
        self.layout.addWidget(self.main)
        self.layout.addStretch()
        self.huntList = []

        #self.layout.addWidget(self.hunt_list_widget)

        self.update()

    def show_hunt(self,id):
        widget = HuntWidget(id)
        self.clearLayout()
        self.widget = widget
        self.main.layout.addWidget(self.widget)
        idx = self.huntPicker.findData(id)
        if idx >= 0:
            self.huntPicker.setCurrentIndex(idx)
        self.main.layout.addStretch()

    def update(self):
        self.getLatestHunt()


    def getLatestHunt(self):
        if len(self.huntList) == 0:
            self.huntList = get_n_hunts()
            if len(self.huntList) == 0:
                return
            self.huntPicker.clear()
            for i in range(len(self.huntList)):
                data = self.huntList[i]
                pixmap = QPixmap(
                    resource_path("assets/icons/Hunt %s Icon.png" % ("Loss" if data['extracted'] == 'true' else 'Extract')))
                txt = "|".join([tab()]*2).join([
                        datetime.fromtimestamp(data['timestamp']).strftime("%H:%M  %b %d"),
                        "Bounty Hunt" if data['game_type'] != 'true' else "Soul Survivor",
                        "KDA: %d/%d/%d" % (data['kills'],data['deaths'],data['assists'] if data['assists'] is not None else 0),
                        "Team KD: %d/%d" % (data['team_kills'], data['team_deaths'])
                    ])
                self.huntPicker.addItem(QIcon(pixmap.scaled(32,32)),txt,userData=data['game_id'])

            self.show_hunt(self.huntList[0]['game_id'])
            return
        newHunt = get_n_hunts(1)
        if len(newHunt) == 0:
            return
        if(len(self.huntList) > 0 and self.huntList[0]['game_id'] == newHunt[0]['game_id']):
            return
        newHunt = newHunt[0]
        self.huntList = [newHunt] + self.huntList
        pixmap = QPixmap(
            resource_path("assets/icons/Hunt %s Icon.png" % ("Loss" if newHunt['extracted'] == 'true' else 'Extract')))
        txt = "|".join([tab()]*2).join([
                datetime.fromtimestamp(newHunt['timestamp']).strftime("%H:%M  %b %d"),
                "Bounty Hunt" if newHunt['game_type'] != 'true' else "Soul Survivor",
                "KDA: %d/%d/%d" % (newHunt['kills'],newHunt['deaths'],newHunt['assists'] if newHunt['assists'] is not None else 0),
                "Team KD: %d/%d" % (newHunt['team_kills'], newHunt['team_deaths'])
            ])
        self.huntPicker.insertItem(0,QIcon(pixmap.scaled(32,32)),txt)

        self.show_hunt(self.huntList[0]['game_id'])

    def clearLayout(self):
        for i in reversed(range(self.main.layout.count())): 
            w = self.main.layout.itemAt(i).widget()
            if w != None:
                w.setParent(None)

    def initHuntSelect(self):
        container = QWidget()
        container.layout = QHBoxLayout()
        container.setLayout(container.layout)
        container.layout.setContentsMargins(4,4,4,0)
        container.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Fixed,
        )
        container.setObjectName("comboContainer")
        container.setStyleSheet("#comboContainer{background:#283940;}")
        container.setAttribute(Qt.WidgetAttribute.WA_StyledBackground)      
        self.huntPicker = QComboBox(parent=self)
        self.huntPicker.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Fixed,
        )
        self.huntPicker.setStyleSheet(comboBoxStyle)
        self.huntPicker.setIconSize(QSize(32,32))
        self.huntPicker.activated.connect(lambda x : self.show_hunt(self.huntList[x]['game_id']))

        container.layout.addWidget(self.huntPicker,stretch=0)

        self.layout.addWidget(self.huntPicker,stretch=0)

