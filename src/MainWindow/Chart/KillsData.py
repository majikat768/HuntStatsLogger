from DbHandler import execute_query, GetKillsByMatch
from resources import *
from cmath import inf
import pyqtgraph

class KillsData():
    def __init__(self):
        kData = GetKillsByMatch()
        timestamps = execute_query("select timestamp from 'games'")

        data = []

        self.maxKills = -inf

        i = 0
        for timestamp in timestamps:
            ts = timestamp[0]

            if ts in kData:
                if kData[ts]['kills'] > self.maxKills:
                    self.maxKills = kData[ts]['kills']
                data.append({
                    'x':i,
                    'y':kData[ts]['kills'],
                    'qp':kData[ts]['isQp'],
                    'ts':ts
                })
            i += 1

        self.line = pyqtgraph.PlotDataItem(data,pen="#ffffff88")
        self.qpPoints = pyqtgraph.ScatterPlotItem(
            [{'x': pt['x'], 'y': pt['y'], 'data':unix_to_datetime(pt['ts'])} for pt in data if pt['qp'] == 'true'],
            size=12,hoverable=True,hoverSize=16,symbol='o',pen="#000000",brush="#00ffff",name="Quick Play",tip="{data}<br>MMR: {y:.0f}".format
        )
        self.bhPoints = pyqtgraph.ScatterPlotItem(
            [{'x': pt['x'], 'y': pt['y'], 'data':unix_to_datetime(pt['ts'])} for pt in data if pt['qp'] == 'false'],
            size=12,hoverable=True,hoverSize=16,symbol='o',pen="#000000",brush="#ff0000",name="Bounty Hunt",tip="{data}<br>MMR: {y:.0f}".format
        )