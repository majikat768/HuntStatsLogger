from DbHandler import GetAllMmrs
import pyqtgraph
from DbHandler import *
from resources import *

class MmrData():
    def __init__(self) -> None:
        data = []
        mmrs = GetAllMmrs(name=settings.value('steam_name'))
        i = 0
        self.minMmr = 6001;
        self.maxMmr = -1;
        for ts in mmrs.keys():
            mmr = mmrs[ts]['mmr']
            qp = mmrs[ts]['qp']
            if mmr > self.maxMmr:
                self.maxMmr = mmr
            if mmr < self.minMmr:
                self.minMmr = mmr
            data.append({'x':i,'y':mmr, 'qp':qp, 'ts':ts})
            i += 1
        self.line = pyqtgraph.PlotDataItem(data,pen="#ffffff88")
        self.qpPoints = pyqtgraph.ScatterPlotItem(
            [{
                'x': pt['x'],
                'y': pt['y'],
                'data':pt['ts']
            } for pt in data if pt['qp'] == 'true'],
            size=12,hoverable=True,hoverSize=16,symbol='o',pen="#000000",brush="#00ffff",name="Quick Play",tip="MMR: {y:.0f}".format
        )
        self.bhPoints = pyqtgraph.ScatterPlotItem(
            [{'x': pt['x'], 'y': pt['y'], 'data':pt['ts']} for pt in data if pt['qp'] == 'false'],
            size=12,hoverable=True,hoverSize=16,symbol='o',pen="#000000",brush="#ff0000",name="Bounty Hunt",tip="MMR: {y:.0f}".format
        )

        starValues = [0,2000,2300,2600,2750,3000,5000]

        self.stars = []
        for s in starValues:
            c = s/5000*255
            line = pyqtgraph.InfiniteLine(pos=s+1, angle=0, pen=pyqtgraph.mkPen("#ff000088",width=2))
            line.label = pyqtgraph.InfLineLabel(line,text="%d stars"%(mmr_to_stars(s)),movable=True,position=0.1)
            #line.label.setParentItem(line)
            #line.label.setPos(0,0)
            self.stars.append(line)