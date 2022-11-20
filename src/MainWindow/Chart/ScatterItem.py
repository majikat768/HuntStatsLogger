import pyqtgraph

class ScatterItem(pyqtgraph.ScatterPlotItem):
    def __init__(self, *args, **kargs):
        if 'hoverable' not in kargs:
            kargs['hoverable'] = True
        if 'size' not in kargs:
            kargs['size'] = 8
        if 'hoverSize' not in kargs:
            kargs['hoverSize'] = 12
        if 'symbol' not in kargs:
            kargs['symbol'] = 'o'
        super().__init__(*args, **kargs)

    def mouseClickEvent(self, ev):
        return super().mouseClickEvent(ev)