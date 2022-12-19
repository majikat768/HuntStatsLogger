from PyQt6.QtWidgets import QWidget, QGridLayout, QVBoxLayout, QGroupBox, QLabel, QScrollArea
from PyQt6.QtCore import Qt
from resources import settings, star_path, mmr_to_stars
from DbHandler import GetTopNHunters, GetHunterByName, execute_query

class FrequentHunters(QGroupBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("Frequently Seen Hunters")
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.area = QScrollArea()
        self.area.setWidgetResizable(True)
        self.area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)

        self.main = QWidget()
        self.main.layout = QVBoxLayout()
        self.main.setLayout(self.main.layout)

        self.area.setWidget(self.main)

        self.area.setStyleSheet("*{border:0px;}")

        self.layout.addWidget(self.area)

    def update(self):
        for i in reversed(range(self.main.layout.count())):
            self.main.layout.itemAt(i).widget().setParent(None)
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
            self.main.layout.addWidget(hWidget)
        pass

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
