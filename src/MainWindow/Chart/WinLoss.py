import pyqtgraph
from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt6.QtGui import QColor, QBrush, QPen, QCursor
from PyQt6.QtCore import QPointF, QRectF
from DbHandler import *
from resources import *
from Widgets.Popup import Popup


class WinLoss():
    def __init__(self) -> None:
        self.brushes = [
            QColor("#c800ff00"),
            QColor("#c8ff0000")
        ]
        self.pen = QPen(QColor("#000000"))
        self.update()

    def update(self):
        self.data = self.GetData()

        self.bountyBars = Bars(
            x0 = [10,20],
            x1 = [20,30],
            height=[
                self.data['winRate']['bounty']['wins'],
                self.data['winRate']['bounty']['losses']
            ],
            brushes=self.brushes,
            pens=[self.pen]*2
        )
        self.quickplayBars = Bars(
            x0 = [40,50],
            x1 = [50,60],
            height=[
                self.data['winRate']['qp']['wins'],
                self.data['winRate']['qp']['losses']
            ],
            brushes=self.brushes,
            pens=[self.pen]*2
        )

        self.survivalBars = Bars(
            x0 = [70,80],
            x1 = [80,90],
            height=[
                self.data['survivalRate']['survived'],
                self.data['survivalRate']['died']
            ],
            brushes=self.brushes,
            pens=[self.pen]*2
        )

        self.labels = [[
            (20,"Bounty Hunt\n(extract at least 1 token)"),
            (50,"Quick Play\n(soul survivor)"),
            (80, "Survived\n(Bounty)")
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

# for this to work I have to make sure the constructor contains:
# x0 [], x1 [], height [], brushes [], pens []
class Bars(pyqtgraph.BarGraphItem):
    def __init__(self, **opts):
        super().__init__(**opts)
        self.setAcceptHoverEvents(True)
        self.setToolTip(None)
        self.isHovered = False

        self.bars = []
        self.pens = opts['pens']
        self.brushes = opts['brushes']
        self.defaultBrushes = opts['brushes']
        self.width = opts['x1'][0] - opts['x0'][0]
        self.heights = opts['height']
        self.total = sum(self.heights)
        self.popup = None
        for i in range(len(opts['x0'])):
            self.bars.append(QRectF(
                opts['x0'][i],
                0,
                self.width,
                opts['height'][i]
            ))

    def hoverEnterEvent(self,ev):
        return None#super().hoverEnterEvent(ev)

    def hoverMoveEvent(self,ev):
        contained = False
        for i in range(len(self.bars)):
            b = self.bars[i]
            if b.contains(ev.pos()):
                contained = True
                if self.popup == None or not self.popup.isVisible():
                    w = self.getViewWidget().window()
                    self.brushes[i].setAlpha(255)
                    val = self.heights[i]
                    perc = (val / self.total) * 100
                    txt = "%d\n%.2f%%" % (val,perc)
                    info = QWidget()
                    info.layout = QVBoxLayout()
                    info.setLayout(info.layout)
                    info.layout.addWidget(QLabel(txt))
                    self.popup = Popup(info,QCursor.pos().x()+16,QCursor.pos().y()-32)
                    self.popup.show()
                    w.raise_()
                    w.activateWindow()
                    self.setOpts()
            else:
                self.brushes[i].setAlpha(200)
                self.setOpts()
        if not contained:
            try:
                self.popup.close()
            except:
                self.popup = None
        self.scene().update()
        return None#super().hoverEnterEvent(ev)

    def hoverLeaveEvent(self,ev):
        try:
            self.popup.close()
        except:
            self.popup = None
        return super().hoverEnterEvent(ev)
