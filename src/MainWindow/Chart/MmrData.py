from DbHandler import GetAllMmrs
import pyqtgraph
from MainWindow.Chart.ScatterItem import ScatterItem
from DbHandler import *
from resources import *


class MmrData():
    def __init__(self) -> None:
        data = []
        mmrs = GetAllMmrs(name=settings.value('steam_name'))
        i = 0
        self.minMmr = 6001
        self.maxMmr = -1
        for ts in mmrs.keys():
            mmr = mmrs[ts]['mmr']
            qp = mmrs[ts]['qp']
            if mmr > self.maxMmr:
                self.maxMmr = mmr
            if mmr < self.minMmr:
                self.minMmr = mmr
            data.append({'x': i, 'y': mmr, 'qp': qp, 'ts': ts})
            i += 1
        prediction = predictNextMmr()
        data.append({'x': GetTotalHuntCount(), 'y': prediction,
                    'qp': None, 'ts': GetLastHuntTimestamp()})
        self.line = pyqtgraph.PlotDataItem(data, pen="#ffffff88")
        self.qpPoints = ScatterItem(
            [{
                'x': pt['x'],
                'y': pt['y'],
                'data':pt['ts']
            } for pt in data if pt['qp'] == 'true'],
            pen="#000000", brush="#00ffff", name="Quick Play", tip="MMR: {y:.0f}".format
        )
        self.bhPoints = ScatterItem(
            [{'x': pt['x'], 'y': pt['y'], 'data':pt['ts']}
                for pt in data if pt['qp'] == 'false'],
            pen="#000000", brush="#ff0000", name="Bounty Hunt", tip=("MMR: {y:.0f}").format,
        )
        lastTs = GetLastHuntTimestamp()
        spots = [{'x': GetTotalHuntCount(), 'y': prediction,
                  'data': -1}]

        self.nextPoint = ScatterItem(
            spots, symbol='t1', pen="#ffffff", brush="#000000", tip=("Predicted MMR: %d" % (prediction)).format)

        starValues = [0, 1999, 2299, 2599, 2749, 2999, 4999]

        self.stars = []
        for s in starValues:
            c = s/5000*255
            line = pyqtgraph.InfiniteLine(
                pos=s, angle=0, pen=pyqtgraph.mkPen("#ff000088", width=2))
            line.label = pyqtgraph.InfLineLabel(line, text="%d stars" % (
                mmr_to_stars(s)), movable=False, position=0.1,anchors=[(0,0),(0,0)])
            # line.label.setParentItem(line)
            # line.label.setPos(0,0)
            self.stars.append(line)
