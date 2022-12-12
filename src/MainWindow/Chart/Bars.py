from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt6.QtCore import QRectF
from PyQt6.QtGui import QCursor, QColor
import pyqtgraph
from Widgets.Popup import Popup

# for this to work I have to make sure the constructor contains:
# x0 [], x1 [], height [], brushes []
class Bars(pyqtgraph.BarGraphItem):
    def __init__(self, **opts):
        super().__init__(**opts)
        self.setAcceptHoverEvents(True)
        self.setToolTip(None)
        self.isHovered = False

        self.bars = []
        self.brushes = opts['brushes']
        self.defaultBrushes = opts['brushes']
        self.width = opts['x1'][0] - opts['x0'][0]
        self.heights = opts['height']
        self.total = sum(self.heights)
        self.popup = None
        if 'y0' not in opts:
            opts['y0'] = [0]*len(opts['x0'])
        for i in range(len(opts['x0'])):
            self.bars.append(QRectF(
                opts['x0'][i],
                opts['y0'][i],
                self.width,
                opts['height'][i]
            ))
        self.hoverable = True

    def hoverEnterEvent(self,ev):
        return None#super().hoverEnterEvent(ev)

    def hoverMoveEvent(self,ev):
        if not self.hoverable:
            return
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