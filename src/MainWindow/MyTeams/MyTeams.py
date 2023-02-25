from PyQt6.QtWidgets import QWidget, QGridLayout, QVBoxLayout, QHBoxLayout, QScrollArea, QPushButton, QLineEdit, QFileDialog
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QEvent, Qt
from DbHandler import *
from MainWindow.Chart.ScatterItem import ScatterItem
from MainWindow.MyTeams.TeamMmrChart import TeamMmrChart
from MainWindow.MyTeams.AddNewTeam import AddNewTeamWindow
from Widgets.Modal import Modal
import hashlib
import pyqtgraph


colors = ["#ff0000cc","#00ffffcc","#ffff00cc"]

class MyTeams(QScrollArea):
    def __init__(self, parent):
        if debug:
            print("myTeams.__init__")
        super().__init__(parent)
        self.setWidgetResizable(True)
        self.main = QWidget()
        self.main.layout = QVBoxLayout()
        self.main.setLayout(self.main.layout)

        self.buttons = QWidget()
        self.buttons.layout = QHBoxLayout()
        self.buttons.setLayout(self.buttons.layout)
        self.buttons.setSizePolicy(QSizePolicy.Policy.Fixed,QSizePolicy.Policy.Fixed)

        self.updateTeamsButton = QPushButton("Calculate my teams")
        self.updateTeamsButton.clicked.connect(self.CalculateTeams)
        self.updateTeamsButton.setSizePolicy(QSizePolicy.Policy.Fixed,QSizePolicy.Policy.Fixed)
        self.addTeamButton = QPushButton("Add new team to track")
        self.addTeamButton.setSizePolicy(QSizePolicy.Policy.Fixed,QSizePolicy.Policy.Fixed)
        self.addTeamButton.clicked.connect(self.AddNewTeam)
        self.updateButton = QPushButton("Update")
        self.updateButton.clicked.connect(self.update)
        self.buttons.layout.addWidget(self.updateTeamsButton)
        self.buttons.layout.addWidget(self.addTeamButton)
        self.buttons.layout.addWidget(self.updateButton)

        self.setWidget(self.main)
        if len(settings.value("my_teams","")) > 0:
            my_teams = eval(settings.value("my_teams","[]"))

    def AddNewTeam(self):
        newTeamDialog = AddNewTeamWindow(parent = self.window())
        newTeamDialog.show()

    def CalculateTeams(self):
        all_teams = []
        teams = []
        hunts = GetHunts()
        for hunt in hunts:
            team = GetTeamMembers(hunt['timestamp'])
            if len(team) > 1:
                all_teams.append(team)

        count = {}
        for team in all_teams:
            team_id = hashlib.md5(str(team['pid']).encode('utf-8')).hexdigest()
            team['team_id'] = team_id
            if team_id not in count:
                count[team_id] = {'pid':team['pid'],'count':0,'games':[]}
            count[team_id]['count'] += 1
            count[team_id]['games'].append(team['timestamp'])
        i = 0
        '''
        for t in sorted(count,key=lambda t : count[t]['count'],reverse=True):
            if count[t]['count'] > 1:
                w = self.TeamWidget(count[t])
                if w == None:
                    continue
                self.main.layout.addWidget(w)
            i += 1
            if i > 10:
                break
        '''
        for t in sorted(count,key=lambda t : count[t]['count'],reverse=True):
            if len(count[t]['pid']) <= 1:
                continue
            elif count[t]['count'] > 1:
                teams.append(count[t]['pid'])
            i += 1
            if i >= 5:
                break
        settings.setValue("my_teams",str(teams))
        self.update()

    def update(self):
        if debug:
            print('myteams.update')
        clearLayout(self.main.layout)
        self.main.layout.addWidget(self.buttons)
        teams = eval(settings.value("my_teams","[]"))
        for pids in teams:
            team = {'pid':pids,'games':GetTeamGames(pids)}
            w = self.TeamWidget(team)
            if w == None:
                continue
            self.main.layout.addWidget(w)
        self.main.layout.addStretch()
        
    def save_chart(self,w):
        filename = "%s_mmr-chart.png" % w.names.lower().replace(' ','').replace(',','-')
        file = QFileDialog.getSaveFileName(
            parent = self.window(),
            directory=os.path.join(QStandardPaths.writableLocation(QStandardPaths.StandardLocation.DesktopLocation),filename),
            filter="PNG (*.png)"
        )[0]
        if len(file) <= 0:
            return
        scrn = QApplication.primaryScreen().grabWindow(w.winId())
        scrn.save(file)

    def TeamWidget(self,team):
        if len(team['pid']) <= 1 or len(team['games']) < 1:
            return None
        team['games'] = sorted(team['games'])
        w = QWidget()
        w.setVisible(False)
        w.layout = QGridLayout()
        w.setLayout(w.layout)
        w.names = ", ".join([GetNameByProfileId(pid) for pid in team['pid']])
        w.layout.addWidget(QLabel("%s" % w.names),0,0)
        w.layout.addWidget(QLabel("Hunted together %d times" % len(team['games'])),1,0)

        w.setObjectName("HuntWidget")
        w.plot = TeamMmrChart(team)
        bestMmrs = w.plot.bestMmrs
        bestWidget = QWidget()
        bestWidget.layout = QGridLayout()
        bestWidget.setLayout(bestWidget.layout)
        i = 0
        for pid in bestMmrs:
            bestWidget.layout.addWidget(QLabel("%s's best: %d" % (GetNameByProfileId(pid),bestMmrs[pid])))
            i += 1
        w.layout.addWidget(bestWidget,0,1,len(bestMmrs.keys()),1)
        w.layout.addWidget(w.plot,len(bestMmrs.keys()),0,1,2)
        w.layout.setRowStretch(w.layout.rowCount(),1)

        wContainer = QWidget()
        wContainer.collapsed = True
        wContainer.layout = QVBoxLayout()
        wContainer.setLayout(wContainer.layout)
        wContainer.setSizePolicy(QSizePolicy.Policy.Expanding,QSizePolicy.Policy.Fixed)
        showButton = QPushButton("%s" % w.names)
        showButton.clicked.connect(lambda : w.setVisible(not w.isVisible()))
        showButton.clicked.connect(lambda : w.screenshotButton.setVisible(not w.screenshotButton.isVisible()))

        w.screenshotButton = QPushButton("Save as image")
        w.screenshotButton.setVisible(False)
        w.screenshotButton.setSizePolicy(QSizePolicy.Policy.Fixed,QSizePolicy.Policy.Fixed)
        w.screenshotButton.clicked.connect(lambda : self.save_chart(w))

        wContainer.layout.addWidget(showButton)
        wContainer.layout.addWidget(w)
        wContainer.layout.addWidget(w.screenshotButton)
        return wContainer

    
def toggle(widget : QWidget, btn : QPushButton):
    if widget.isVisible():
        widget.setHidden(True)
        btn.setIcon(QIcon(resource_path("assets/icons/plus.png")))
    else:
        widget.setVisible(True)
        btn.setIcon(QIcon(resource_path("assets/icons/minus.png")))
