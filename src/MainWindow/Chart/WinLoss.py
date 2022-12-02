import pyqtgraph
from PyQt6.QtGui import QColor, QBrush, QPen
from PyQt6.QtCore import QPointF
from DbHandler import *
from resources import *


class WinLoss():
    def __init__(self) -> None:
        self.brushes = [
            QColor("#6600ff00"),
            QColor("#ccff0000")
        ]
        self.pen = QPen(QColor("#000000"))
        self.update()

    def update(self):
        self.data = self.GetData()

        self.bountyBars = pyqtgraph.BarGraphItem(
            x0 = [10,20],
            x1 = [20,30],
            width=10,
            height=[
                self.data['winRate']['bounty']['wins'],
                self.data['winRate']['bounty']['losses']
            ],
            brushes=self.brushes,
            pen=self.pen
        )
        self.bountyBars.setToolTip("Bounty")
        self.quickplayBars = pyqtgraph.BarGraphItem(
            x0 = [40,50],
            x1 = [50,60],
            height=[
                self.data['winRate']['qp']['wins'],
                self.data['winRate']['qp']['losses']
            ],
            brushes=self.brushes,
            pen=self.pen
        )

        self.survivalBars = pyqtgraph.BarGraphItem(
            x0 = [70,80],
            x1 = [80,90],
            height=[
                self.data['survivalRate']['survived'],
                self.data['survivalRate']['died']
            ],
            brushes=self.brushes,
            pen=self.pen
        )

        self.labels = [[
            (20,"Bounty Hunt"),
            (50,"Quick Play"),
            (80, "Survived")
        ]]


    def GetData(self):
        wins = self.GetWins()
        survival = self.GetSurvival()
        return {
            "winRate": wins,
            "survivalRate":survival
        }

    def GetWins(self):
        data = {
            'bounty' : {},
            'quickplay' : {}
        }
        vals = execute_query("select 'games'.timestamp, 'accolades'.category, 'games'.MissionBagIsQuickPlay as isQp from 'accolades' join 'games' on 'accolades'.timestamp = 'games'.timestamp")
        cols = ['timestamp', 'category', 'qp']
        try:
            accolades = [ {cols[i] : acc[i] for i in range(len(cols))} for acc in vals]
        except:
            accolades = []

        for accolade in accolades:
            ts = accolade['timestamp']
            if accolade['qp'] == 'true':
                if ts not in data['quickplay']:
                    data['quickplay'][ts] = 0
                if 'extract' in accolade['category']:
                    data['quickplay'][ts] = 1
            else:
                if ts not in data['bounty']:
                    data['bounty'][ts] = 0
                if 'extract' in accolade['category']:
                    data['bounty'][ts] = 1
        
        bountyWins = sum(data['bounty'].values())
        qpWins = sum(data['quickplay'].values())
        totalBounty = execute_query("select count(*) from 'games' where MissionBagIsQuickPlay = 'false'")
        totalBounty = 0 if len(totalBounty) == 0 else totalBounty[0][0]
        totalQp = execute_query("select count(*) from 'games' where MissionBagIsQuickPlay = 'true'")
        totalQp = 0 if len(totalQp) == 0 else totalQp[0][0]

        wins = {
            'bounty': {
                'wins':bountyWins,
                'losses':totalBounty - bountyWins,
                'total': totalBounty
            },
            'qp': {
                'wins':qpWins,
                'losses':totalQp - qpWins,
                'total':totalQp
            }
        }
        return wins

    def GetSurvival(self):
        survived = execute_query("select count(*) from 'games' where MissionBagIsHunterDead = 'false' and MissionBagIsQuickPlay = 'false'")
        survived = 0 if len(survived) == 0 else survived[0][0]
        total = execute_query("select count(*) from 'games' where MissionBagIsQuickPlay = 'false'")
        total = 0 if len(total) == 0 else total[0][0]
        return {
            'survived':survived,
            'died':total - survived,
            'total':total
        }