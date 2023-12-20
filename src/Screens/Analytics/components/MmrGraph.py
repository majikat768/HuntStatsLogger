import pyqtgraph
from PyQt6.QtCore import QRectF
from PyQt6.QtGui import QColor, QFont,QPen, QBrush
from DbHandler import get_mmr_history,get_team_mmr_history, predictNextMmr, execute_query
from datetime import datetime
from resources import mmr_to_stars, settings
from Screens.Analytics.components.PlotItem import PlotItem

ptSize = 10
ptHoverSize = 14

font = QFont()
font.setWeight(500)
font.setFamily("Arial")
font.setPixelSize(16)

class MmrGraph(PlotItem):
    def __init__(self, parent=None, name=None, labels=None, title=None, viewBox=None, axisItems=None, enableMenu=True, **kargs):
        super().__init__(parent, name, labels, title, viewBox, axisItems, enableMenu, **kargs)
        self.legend = pyqtgraph.LegendItem(colCount=2)
        self.legend.setLabelTextColor(QColor("#fff"))
        self.legend.setFixedHeight(100)
        self.setTitle("MMR")
        self.showGrid(x=True,y=True,alpha=0.4)
        self.getAxis("bottom").setTicks([])
        self.setFixedHeight(400)

    def update(self):
        self.clear()
        self.legend.clear()
        #self.setTeamMmrData()
        self.setMmrData()
        #self.legend.getViewBox().setMaximumHeight(self.legend.boundingRect().height())

    def setTeamMmrData(self):
        teamMmrData = get_team_mmr_history()
        if len(teamMmrData) == 0:
            return
        plotData = [
            {
                'x':i,
                'y':teamMmrData[i]['mmr'],
                'data':datetime.fromtimestamp(teamMmrData[i]['timestamp']).strftime("%H:%M %b %d")
            } for i in range(len(teamMmrData))
        ]
        mmrLine = pyqtgraph.PlotDataItem(plotData,pen="#ffffff44")
        pts = pyqtgraph.ScatterPlotItem(
            plotData,
            pen="#000000",
            brush="#898c8d",
            name="Team MMR",
            tip=("Team MMR: {y:.0f}\n{data}").format,
            hoverable=True,
            size=ptSize,
            hoverSize=ptHoverSize,
            parent=self.parent
        )
        self.addItem(mmrLine)
        self.addItem(pts)

    def setMmrData(self):
        mmrData = get_mmr_history()
        if len(mmrData) == 0:
            return
        plotData = [
            {
                'x':i,
                'y':mmrData[i]['mmr'],
                'isQp':mmrData[i]['isQp'],
                'ts': mmrData[i]['timestamp']
            } for i in range(len(mmrData))
        ]
        prediction = predictNextMmr()
        plotData.append({'x':len(plotData),'y':prediction,'isQp':None,'ts':None})
        mmrLine = pyqtgraph.PlotDataItem(plotData,pen="#ffffff44")
        bhPts = pyqtgraph.ScatterPlotItem(
            [{
                'x':pt['x'],
                'y':pt['y'],
                'data':datetime.fromtimestamp(pt['ts']).strftime("%H:%M %b %d")
            } for pt in plotData if pt['isQp'] == 'false'],
            pen="#000",
            brush="#f1282B",
            name="Bounty Hunt",
            tip=("MMR: {y:.0f}\n{data}").format,
            hoverable=True,
            size=ptSize,
            hoverSize=ptHoverSize,
            parent=self.parent
        )
        ssPts = pyqtgraph.ScatterPlotItem(
            [{
                'x':pt['x'],
                'y':pt['y'],
                'data':datetime.fromtimestamp(pt['ts']).strftime("%H:%M %b %d")
            } for pt in plotData if pt['isQp'] == 'true'],
            pen="#000000",
            brush="#83aff7",
            name="Soul Survivor",
            tip=("MMR: {y:.0f}\n{data}").format,
            size=ptSize,
            hoverSize=ptHoverSize,
            parent=self.parent
        )
        estPt = pyqtgraph.ScatterPlotItem(
            [{
                'x':len(plotData)-1,
                'y':prediction,
                'data': None,
            }],symbol='t1',pen="#fff",brush="#000",tip="prediction: %d" % prediction,size=ptSize,hoverSize=ptHoverSize,parent=self.parent
        )

        self.addItem(mmrLine)
        self.addItem(bhPts)
        self.addItem(ssPts)
        self.addItem(estPt)


        self.stars = []
        for s in [0,1999,2299,2599,2749,2999,4999]:
            c = s/5000*255
            sline = pyqtgraph.InfiniteLine(
                pos=s,angle=0,pen = pyqtgraph.mkPen("#ff000088",width=1))
            sline.label = pyqtgraph.InfLineLabel(sline,text="%d stars" % (
                mmr_to_stars(s)), movable=False,position = 0.1,anchors=[(0,0),(0,0)])
            self.stars.append(sline)
            self.addItem(sline)

        self.setLimits(yMin=0,yMax=6000,xMin=0,xMax=len(mmrLine.xData)+2)
        self.setXRange(
            max(-1,len(mmrLine.xData)-30), len(mmrLine.xData)+2)
        self.setYRange(
            min(plotData,key=lambda x : x['y'])['y']-20,
            max(plotData,key=lambda x : x['y'])['y']+20,
        )

class MmrWindow(pyqtgraph.GraphicsLayoutWidget):
    def __init__(self, parent=None, show=False, size=None, title=None, **kargs):
        super().__init__(parent, show, size, title, **kargs)
        self.mmrPlot = MmrGraph()
        self.mmrPlot.getViewBox().installEventFilter(self)

        self.legend = pyqtgraph.LegendItem()
        vb = pyqtgraph.ViewBox()
        self.mmrPlot.legend.setParentItem(vb)
        self.mmrPlot.legend.anchor((0,0),(0,0))
        self.addItem(self.mmrPlot,0,0)
        self.addItem(vb,1,0)
        self.ci.layout.setContentsMargins(0,0,0,0)
        self.ci.layout.setSpacing(0)
        self.setFixedHeight(500)

    def update(self):
        self.mmrPlot.update()

    def setStats(self):
        avgMmr = execute_query("select avg(mmr) from 'hunters' where profileid = ?", settings.value("profileid"))
        if len(avgMmr) == 0:
            avgMmr = 0
        else:
            avgMmr = avgMmr[0][0]

        mmrGain = execute_query("select\
                                lag(h.mmr) over (order by g.timestamp desc) - h.mmr as mmr_gain\
                                from 'hunters' h join 'games' g on h.game_id = g.game_id where h.profileid = ? order by mmr_gain desc limit 1", settings.value("profileid",0))
        if len(mmrGain) == 0:
            mmrGain = 0
        else:
            mmrGain = mmrGain[0][0]
        mmrLoss = execute_query("select\
                                lag(h.mmr) over (order by g.timestamp desc) - h.mmr as mmr_loss\
                                from 'hunters' h join 'games' g on h.game_id = g.game_id where h.profileid = ? order by mmr_loss asc limit 1 offset 2", settings.value("profileid",0))
        if len(mmrLoss) == 0:
            mmrLoss = 0
        else:
            mmrLoss = mmrLoss[0][0]
        return [avgMmr,mmrGain,mmrLoss]


class MmrLabelItem(pyqtgraph.ViewBox):
    def __init__(self, parent=None, text="", background=None, color="#ccc", border=None, lockAspect=False, enableMouse=True, invertY=False, enableMenu=True, name=None, invertX=False, defaultPadding=0.02):
        super().__init__(parent, border, lockAspect, enableMouse, invertY, enableMenu, name, invertX, defaultPadding)
        self.label = pyqtgraph.TextItem(text,color=color)
        self.label.setFont(font)
        self.label.setParentItem(self)
        self.setBackgroundColor(background)
        self.setFixedHeight(24)

    def setText(self,text):
        self.label.setText(text=text)