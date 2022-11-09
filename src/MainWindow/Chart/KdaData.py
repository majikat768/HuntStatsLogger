from cmath import inf
from DbHandler import *
import pyqtgraph

class KdaData():
    def __init__(self):
        kData = GetKillsByMatch()
        dData = GetDeathsByMatch()
        aData = GetAssistsByMatch()

        totalKills = 0
        totalDeaths = 0
        totalAssists = 0

        kda = 0.0
        data = []

        timestamps = execute_query("select timestamp from 'games'")
        GameTypes = GetGameTypes()

        i = 0
        self.minKda = inf
        self.maxKda = -inf
        for ts in GameTypes:
            if ts in kData:
                totalKills += kData[ts]['kills']
            if ts in dData:
                totalDeaths += dData[ts]['deaths']
            if ts in aData:
                totalAssists += aData[ts]['assists']

            kda = (totalKills+totalAssists)/(max(1,totalDeaths))
            if kda > self.maxKda:
                self.maxKda = kda
            if kda < self.minKda:
                self.minKda = kda
            data.append({
                'x':i,
                'y':kda,
                'qp':GameTypes[ts],
                'ts':ts
            })
            i += 1

        self.line = pyqtgraph.PlotDataItem(data,pen="#ffffff88")
        self.qpPoints = pyqtgraph.ScatterPlotItem(
            [{'x': pt['x'], 'y': pt['y'], 'data':unix_to_datetime(pt['ts'])} for pt in data if pt['qp'] == 'true'],
            size=12,hoverable=True,hoverSize=16,symbol='o',pen="#000000",brush="#00ffff",name="Quick Play",tip="{data}<br>KDA: {y:.0f}".format
        )
        self.bhPoints = pyqtgraph.ScatterPlotItem(
            [{'x': pt['x'], 'y': pt['y'], 'data':unix_to_datetime(pt['ts'])} for pt in data if pt['qp'] == 'false'],
            size=12,hoverable=True,hoverSize=16,symbol='o',pen="#000000",brush="#ff0000",name="Bounty Hunt",tip="{data}<br>KDA: {y:.0f}".format
        )
