from PyQt6.QtWidgets import QWidget, QGroupBox, QGridLayout, QHBoxLayout, QVBoxLayout, QLabel, QScrollArea, QLineEdit, QPushButton, QMainWindow, QDialog
from PyQt6.QtCore import Qt
from resources import *
from DbHandler import *
from MainWindow.Hunters.TopKills import TopKills
from MainWindow.Hunters.FrequentHunters import FrequentHunters
from MainWindow.Hunters.HunterSearch import HunterSearch
from Widgets.Modal import Modal


class Hunters(QWidget):
    def __init__(self, parent):
        if debug:
            print("hunters.__init__")
        super().__init__(parent)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.topKills = TopKills()
        self.layout.addWidget(self.topKills)
        self.freqHunters = FrequentHunters()
        self.layout.addWidget(self.freqHunters)
        self.search = HunterSearch()
        self.layout.addWidget(self.search)
        #self.initHunterSearch()

        #self.layout.setRowStretch(self.layout.rowCount()+1, 1)
        self.setSizePolicy(
            QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Expanding)

    def initFreqHunters(self):
        if debug:
            print("hunters.initFreq")
        self.FreqHuntersBox = QGroupBox("Frequently Seen Hunters")
        self.FreqHuntersBox.layout = QVBoxLayout()
        self.FreqHuntersBox.setLayout(self.FreqHuntersBox.layout)

        self.FreqHuntersArea = QScrollArea()
        self.FreqHuntersArea.setWidgetResizable(True)
        self.FreqHuntersArea.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.FreqHuntersWidget = QWidget()
        self.FreqHuntersWidget.layout = QVBoxLayout()
        self.FreqHuntersWidget.setLayout(self.FreqHuntersWidget.layout)
        self.FreqHuntersArea.setWidget(self.FreqHuntersWidget)
        self.FreqHuntersBox.layout.addWidget(self.FreqHuntersArea)

        self.FreqHuntersBox.setSizePolicy(
            QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Expanding)
        self.layout.addWidget(self.FreqHuntersBox)

    def initHunterSearch(self):
        if debug:
            print("hunters.hunterSearch")
        self.SearchBox = QGroupBox("Search Hunters")
        self.SearchBox.layout = QHBoxLayout()
        self.SearchBox.setLayout(self.SearchBox.layout)
        self.SearchBar = QLineEdit()
        self.SearchBar.setPlaceholderText("Enter Hunter name")
        self.SearchButton = QPushButton("Search")

        self.SearchBox.layout.addWidget(self.SearchBar)
        self.SearchBox.layout.addStretch()
        self.SearchBox.layout.addWidget(self.SearchButton)

        self.SearchBar.returnPressed.connect(self.SubmitSearch)
        self.SearchButton.clicked.connect(self.SubmitSearch)

        self.layout.addWidget(self.SearchBox)

    def update(self):
        if debug:
            print("hunters.update")
        self.topKills.update()
        self.freqHunters.update()

    def SubmitSearch(self):
        name = self.SearchBar.text()
        if len(name) <= 0:
            return
        res = GetHunterByName(name)
        self.ShowResults(res, name)

    def ShowResults(self, data, name):
        resultsWindow = Modal(parent=self)
        results = QWidget()
        results.layout = QVBoxLayout()
        results.setLayout(results.layout)
        if len(data) <= 0:
            results.layout.addWidget(
                QLabel("You've never encountered %s in a Hunt." % name))
        else:
            pid = data[0]['profileid']
            results.layout.addWidget(
                QLabel("You've seen %s in %d hunts." % (name, len(data))))

            allnamesarray = execute_query(
                "select blood_line_name from 'hunters' where profileid is %d group by blood_line_name" % pid)
            allnames = []
            for n in allnamesarray:
                allnames.append(n[0])
            kills = GetHunterKills(pid)
            killedby = 0
            killed = 0
            for k in kills:
                killedby += k['killedby']
                killed += k['killed']
            sameTeamCount = self.SameTeamCount(data)

            if len(allnames) > 1:
                results.layout.addWidget(
                    QLabel("They've also gone by:\n%s" % ",".join(allnames)))
            if sameTeamCount > 0:
                results.layout.addWidget(
                    QLabel("You've been on their team %d times." % sameTeamCount))
            if killedby > 0:
                results.layout.addWidget(
                    QLabel("They've killed you %d times." % killedby))
            if killed > 0:
                results.layout.addWidget(
                    QLabel("You've killed them %d times." % killed))

        results.layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        resultsWindow.addWidget(results)
        resultsWindow.show()

    def SameTeamCount(self, data):
        teamnums = {}
        for d in data:
            teamnums[d['game_id']] = d['team_num']
        teams = []
        for id in teamnums:
            t = execute_query(
                "select blood_line_name from 'hunters' where game_id is '%s' and team_num is %d" % (id, teamnums[id]))
            team = []
            for n in t:
                team.append(n[0])
            teams.append(team)
        n = 0
        me = settings.value("steam_name")
        for team in teams:
            if me in team:
                n += 1
        return n

    def updateFrequentHunters(self):
        if debug:
            print("hunters.updateFreqHunters")
        for i in reversed(range(self.FreqHuntersWidget.layout.count())):
            self.FreqHuntersWidget.layout.itemAt(i).widget().setParent(None)
        hunters = GetTopNHunters(20)
        for hunter in hunters:
            hWidget = QWidget()
            hWidget.layout = QGridLayout()
            hWidget.setLayout(hWidget.layout)
            hWidget.setObjectName("HunterWidget")
            name = hunter['name']
            data = GetHunterByName(name)
            freq = hunter['frequency']
            mmr = hunter['mmr']
            killedme = hunter['killedme']
            killedbyme = hunter['killedbyme']
            sameTeamCount = self.SameTeamCount(data)
            stars = QLabel("%s<br>%s" % ("<img src='%s'>" %
                           (star_path()) * mmr_to_stars(mmr), mmr))
            hWidget.layout.addWidget(QLabel('%s' % name), 0, 0)
            hWidget.layout.addWidget(stars, 1, 0)
            hWidget.layout.addWidget(QLabel("Seen in %d hunts." % freq), 0, 1)
            if sameTeamCount > 0:
                hWidget.layout.addWidget(
                    QLabel("You've been on their team %d times." % sameTeamCount), 1, 1)
            killText = []
            if killedme > 0:
                killText.append("Has killed you %d times." % killedme)
            if killedbyme > 0:
                killText.append("You've killed them %d times." % killedbyme)
            if len(killText) > 0:
                hWidget.layout.addWidget(QLabel("<br>".join(killText)), 2, 1)

            hWidget.layout.setRowStretch(hWidget.layout.rowCount(), 1)
            self.FreqHuntersWidget.layout.addWidget(hWidget)
