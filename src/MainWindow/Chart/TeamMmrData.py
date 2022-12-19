from DbHandler import GetTeamMmrs
import pyqtgraph
from MainWindow.Chart.ScatterItem import ScatterItem
from DbHandler import *
from resources import *

class TeamMmrData():
    def __init__(self,color="#ff0000",parent=None):
        self.parent = parent
        data = []
        mmrs = GetTeamMmrs(pid=settings.value('profileid'))
        self.minMmr = 6001
        self.maxMmr = -1
        
        i = 0
        for ts in mmrs.keys():
            mmr = mmrs[ts]
            if mmr > self.maxMmr:
                self.maxMmr = mmr
            if mmr < self.minMmr:
                self.minMmr = mmr

            pt = {'x':i, 'y': mmr, 'ts':ts}
            data.append(pt)
            i += 1
        self.line = pyqtgraph.PlotDataItem(data,pen="#ffffff88")
        self.points = ScatterItem(
            [{
                'x':pt['x'],
                'y':pt['y'],
                'data':pt['ts']
            } for pt in data],
            pen="#000000",brush=color,name="Team MMR",tip=("MMR: {y:d}").format,parent=self.parent
        )

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

