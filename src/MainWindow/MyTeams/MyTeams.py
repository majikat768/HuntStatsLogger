from PyQt6.QtWidgets import QWidget, QGridLayout, QVBoxLayout, QHBoxLayout, QScrollArea, QPushButton
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QEvent, Qt
from DbHandler import *
from MainWindow.Chart.ScatterItem import ScatterItem
from MainWindow.MyTeams.TeamMmrChart import TeamMmrChart
import hashlib
import pyqtgraph


colors = ["#ff0000cc","#00ffffcc","#ffff00cc"]

class MyTeams(QScrollArea):
    def __init__(self, parent):
        super().__init__(parent)
        self.setWidgetResizable(True)
        self.main = QWidget()
        self.main.layout = QVBoxLayout()
        self.main.setLayout(self.main.layout)
        self.setWidget(self.main)
        self.update()

    def update(self):
        if debug:
            print('myteams.update')
        clearLayout(self.main.layout)
        hunts = GetHunts()
        teams = []
        for hunt in hunts:
            team = GetTeamMembers(hunt['timestamp'])
            if len(team) > 0:
                teams.append(team)

        count = {}
        for team in teams:
            team_id = hashlib.md5(str(team['pid']).encode('utf-8')).hexdigest()
            team['team_id'] = team_id
            if team_id not in count:
                count[team_id] = {'pid':team['pid'],'count':0,'games':[]}
            count[team_id]['count'] += 1
            count[team_id]['games'].append(team['timestamp'])
        i = 0
        for t in sorted(count,key=lambda t : count[t]['count'],reverse=True):
            if count[t]['count'] > 1:
                w = self.TeamWidget(count[t])
                if w == None:
                    continue
                self.main.layout.addWidget(w)
            i += 1
            if i > 10:
                break
        self.main.layout.addStretch()
        

    def TeamWidget(self,team):
        if len(team['pid']) == 1:
            return None
        team['games'] = sorted(team['games'])
        w = QWidget()
        w.layout = QGridLayout()
        w.setLayout(w.layout)
        names = [GetNameByProfileId(pid) for pid in team['pid']]
        w.layout.addWidget(QLabel("%s" % ", ".join(names)),0,0)
        w.layout.addWidget(QLabel("Hunted together %d times" % team['count']),1,0)

        w.setObjectName("HuntWidget")
        plot = TeamMmrChart(team)
        bestMmrs = plot.bestMmrs
        bestWidget = QWidget()
        bestWidget.layout = QGridLayout()
        bestWidget.setLayout(bestWidget.layout)
        i = 0
        for pid in bestMmrs:
            bestWidget.layout.addWidget(QLabel("%s's best: %d" % (GetNameByProfileId(pid),bestMmrs[pid])))
            i += 1
        w.layout.addWidget(bestWidget,0,1,len(bestMmrs.keys()),1)
        w.layout.addWidget(plot,len(bestMmrs.keys()),0,1,2)
        return w

    
def toggle(widget : QWidget, btn : QPushButton):
    if widget.isVisible():
        widget.setHidden(True)
        btn.setIcon(QIcon(resource_path("assets/icons/plus.png")))
    else:
        widget.setVisible(True)
        btn.setIcon(QIcon(resource_path("assets/icons/minus.png")))
