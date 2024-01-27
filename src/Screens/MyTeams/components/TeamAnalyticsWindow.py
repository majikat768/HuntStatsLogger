from PyQt6.QtWidgets import QMainWindow, QWidget
from PyQt6.QtGui import QColor
from Screens.Analytics.components.PlotItem import PlotItem
from datetime import datetime
import pyqtgraph

brushes = [
    "#f1282b",
    "#83aff7",
    "#83ffa7",
    "#898c8d"
]
class TeamAnalyticsWindow(QMainWindow):
    def __init__(self, data, parent: QWidget | None = None):
        super().__init__(parent)
        if len(data) == 0:
            return
        hunters = [data[0]['p1_name']]
        if 'p2_name' in data[0]:
            hunters += [data[0]['p2_name']]
        if 'p3_name' in data[0]:
            hunters += [data[0]['p3_name']]

        self.setWindowTitle(", ".join(hunters) + " Team Analysis")

        window = pyqtgraph.GraphicsLayoutWidget()

        plot = PlotItem()
        self.legend = plot.addLegend(colCount=4)
        self.legend.setLabelTextColor(QColor("#fff"))
        vb = pyqtgraph.ViewBox()
        self.legend.setParentItem(vb)
        self.legend.anchor((0,0),(0,0))
        self.legend.setFixedHeight(100)
        window.addItem(vb,1,0)
        plotData = [
            [
                {
                    'x':i,
                    'y':data[i]['p%d_mmr' % (j+1)],
                    'data':datetime.fromtimestamp(data[i]['timestamp']).strftime("%H:%M %b %d")
                } for i in range(len(data))
            ] for j in range(len(hunters))
        ]

        for i in range(len(plotData)):
            item = plotData[i]
            plot.addItem(pyqtgraph.PlotDataItem(item))
            pts = pyqtgraph.ScatterPlotItem(
                [{
                    'x':pt['x'],
                    'y':pt['y'],
                    'data':pt['data']
                } for pt in item],
                tip=("MMR: {y:.0f}\n{data}").format,
                pen="#000",
                brush=brushes[i],
                size=12,
                hoverSize=14,
                name=hunters[i],
                hoverable=True
            )
            plot.addItem(pts)

        teamData = [
            {
                'x':i,
                'y':data[i]['team_mmr'],
                'data':datetime.fromtimestamp(data[i]['timestamp']).strftime("%H:%M %b %d")
            } for i in range(len(data))
        ]
        plot.addItem(pyqtgraph.PlotDataItem(teamData))
        teamPts = pyqtgraph.ScatterPlotItem(
            [{
                'x':pt['x'],
                'y':pt['y'],
                'data':pt['data']
            } for pt in teamData],
            tip=("Team MMR: {y:.0f}\n{data}").format,
            pen="#000",
            brush=brushes[3],
            size=12,
            hoverSize=14,
            name="Team MMR",
            hoverable=True
        )
        plot.addItem(teamPts)

        plot.showGrid(x=True,y=True,alpha=0.4)
        plot.getAxis("bottom").setTicks([])

        self.legend.getViewBox().setMaximumHeight(self.legend.boundingRect().height())
        window.addItem(plot,0,0)

        plot.setLimits(yMin=0,yMax=6000,xMin=0,xMax=len(data)+2)
        plot.setXRange(
            max(-1,len(data)-30), len(data)+2)

        self.setCentralWidget(window)