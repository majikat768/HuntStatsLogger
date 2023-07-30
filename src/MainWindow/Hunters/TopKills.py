from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QGroupBox
from resources import settings, debug
from Widgets.Label import Label
from DbHandler import GetTopKilled, GetTopKiller, GetHunterByName, execute_query

class TopKills(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QHBoxLayout()
        self.setLayout(self.layout)

        self.killedBox = QGroupBox("Top Killed")
        self.killedBox.layout = QVBoxLayout()
        self.killedBox.setLayout(self.killedBox.layout)

        self.killerBox = QGroupBox("Top Killer")
        self.killerBox.layout = QVBoxLayout()
        self.killerBox.setLayout(self.killerBox.layout)

        self.layout.addWidget(self.killedBox)
        self.layout.addWidget(self.killerBox)

    def update(self):
        self.updateTopKilled()
        self.updateTopKiller()

    def updateTopKilled(self):
        if debug:
            print('topkilled.update')
        for i in reversed(range(self.killedBox.layout.count())):
            self.killedBox.layout.itemAt(i).widget().setParent(None)
        topKilled = GetTopKilled()
        if len(topKilled.keys()) < 1:
            return
        name = topKilled['name']
        kills = topKilled['kills']
        self.killedBox.layout.addWidget(Label('%s' % name))
        self.killedBox.layout.addWidget(
            Label('Have killed them %d times.' % kills))
        data = GetHunterByName(name)
        sameTeamCount = self.SameTeamCount(data)
        if sameTeamCount > -1:
            self.killedBox.layout.addWidget(
                Label("You've been on their team %d times." % sameTeamCount))
        self.killedBox.adjustSize()

    def updateTopKiller(self):
        if debug:
            print('topkiller.update')
        for i in reversed(range(self.killerBox.layout.count())):
            self.killerBox.layout.itemAt(i).widget().setParent(None)
        topKiller = GetTopKiller()
        if len(topKiller.keys()) < 1:
            return
        name = topKiller['name']
        kills = topKiller['kills']
        self.killerBox.layout.addWidget(Label('%s' % name))
        self.killerBox.layout.addWidget(
            Label('Has killed you %d times.' % kills))
        data = GetHunterByName(name)
        sameTeamCount = self.SameTeamCount(data)
        if sameTeamCount > -1:
            self.killerBox.layout.addWidget(
                Label("You've been on their team %d times." % sameTeamCount))
        self.killerBox.adjustSize()

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
