from GroupBox import GroupBox
from PyQt5.QtCore import QSettings,Qt
from PyQt5.QtChart import QChart, QChartView, QLineSeries,QValueAxis

settings = QSettings('./settings.ini',QSettings.Format.IniFormat)

class Chart(GroupBox):
    def __init__(self, parent, layout, title=''):
        super().__init__(layout, title)
        self.parent = parent
        self.connection = self.parent.connection
        mmrs = self.connection.execute_query("select mmr from 'hunter' where blood_line_name is '%s'" % settings.value('hunterName',''))
        mmrs = [i[0] for i in mmrs]

        points = QLineSeries()
        for x in range(len(mmrs)):
            points.append(x,mmrs[x])

        chart = QChart()
        xAxis = QValueAxis()
        yAxis = QValueAxis()
        xAxis.setRange(0,len(mmrs))
        xAxis.setLabelFormat('%d')
        yAxis.setRange(min(mmrs),max(mmrs))
        yAxis.setTickInterval(10)
        yAxis.setLabelFormat('%d')
        chart.addAxis(xAxis,Qt.AlignBottom)
        chart.addAxis(yAxis,Qt.AlignLeft)
        chart.addSeries(points)
        points.attachAxis(xAxis)
        points.attachAxis(yAxis)
        chartView = QChartView(chart)
        self.layout.addWidget(chartView)