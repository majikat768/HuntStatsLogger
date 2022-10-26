from PyQt6.QtWidgets import QWidget, QGroupBox, QGridLayout, QHBoxLayout, QVBoxLayout, QLabel, QScrollArea
from PyQt6.QtCore import Qt
from resources import *
from DbHandler import *

class Hunters(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.layout = QGridLayout()
        self.setLayout(self.layout)

        self.TopKilledBox = QGroupBox("Top Killed")
        self.TopKilledBox.layout = QVBoxLayout()
        self.TopKilledBox.setLayout(self.TopKilledBox.layout)
        self.TopKillerBox = QGroupBox("Top Killer")
        self.TopKillerBox.layout = QVBoxLayout()
        self.TopKillerBox.setLayout(self.TopKillerBox.layout)

        self.FreqHuntersBox = QGroupBox("Frequently Seen Hunters")
        self.FreqHuntersBox.layout = QVBoxLayout()
        self.FreqHuntersBox.setLayout(self.FreqHuntersBox.layout)
        self.FreqHuntersArea = QScrollArea()
        self.FreqHuntersArea.setWidgetResizable(True)
        self.FreqHuntersArea.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.FreqHuntersWidget = QWidget()
        self.FreqHuntersWidget.layout = QVBoxLayout()
        self.FreqHuntersWidget.setLayout(self.FreqHuntersWidget.layout)
        self.FreqHuntersWidget.layout.addWidget(QLabel("hi"))
        self.FreqHuntersArea.setWidget(self.FreqHuntersWidget)
        self.FreqHuntersBox.layout.addWidget(self.FreqHuntersArea)


        self.layout.addWidget(self.TopKillerBox,0,0,1,1)
        self.layout.addWidget(self.TopKilledBox,0,1,1,1)
        self.layout.addWidget(self.FreqHuntersBox,1,0,1,2)

        self.layout.setRowStretch(self.layout.rowCount(),1)
        
    def update(self):
        self.updateTopKilled()
        self.updateTopKiller()
        self.updateFrequentHunters()

    def updateTopKilled(self):
        for i in reversed(range(self.TopKilledBox.layout.count())):
            self.TopKilledBox.layout.itemAt(i).widget().setParent(None)
        topKilled = GetTopKilled()
        if len(topKilled.keys()) < 1:
            return
        name = topKilled['name']
        kills = topKilled['kills']
        self.TopKilledBox.layout.addWidget(QLabel('%s' % name))
        self.TopKilledBox.layout.addWidget(QLabel('Have killed them %d times' % kills))

    def updateTopKiller(self):
        for i in reversed(range(self.TopKillerBox.layout.count())):
            self.TopKillerBox.layout.itemAt(i).widget().setParent(None)
        topKiller = GetTopKiller()
        if len(topKiller.keys()) < 1:
            return
        name = topKiller['name']
        kills = topKiller['kills']
        self.TopKillerBox.layout.addWidget(QLabel('%s' % name))
        self.TopKillerBox.layout.addWidget(QLabel('Has killed you %d times' % kills))

    def updateFrequentHunters(self):
        for i in reversed(range(self.FreqHuntersWidget.layout.count())):
            self.FreqHuntersWidget.layout.itemAt(i).widget().setParent(None)
        hunters = GetTopNHunters(20)
        for hunter in hunters:
            hWidget = QWidget()
            hWidget.layout = QGridLayout()
            hWidget.setLayout(hWidget.layout)
            name = hunter['name']
            freq = hunter['frequency']
            mmr = hunter['mmr']
            killedme = hunter['killedme']
            killedbyme = hunter['killedbyme']
            stars = QLabel("%s<br>%s" % ("<img src='%s'>" % (star_path()) * mmr_to_stars(mmr),mmr))
            hWidget.layout.addWidget(QLabel('%s' % name),0,0)
            hWidget.layout.addWidget(stars,1,0)
            hWidget.layout.addWidget(QLabel("Seen in %d hunts." % freq),0,1)
            killText = []
            if killedme > 0:
                killText.append("Has killed you %d times." % killedme)
            if killedbyme > 0:
                killText.append("You've killed them %d times." % killedbyme)
            if len(killText) > 0:
                hWidget.layout.addWidget(QLabel("<br>".join(killText)),1,1)

            hWidget.layout.setRowStretch(hWidget.layout.rowCount(),1)
            self.FreqHuntersWidget.layout.addWidget(hWidget)