from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QGraphicsItem, QGraphicsRectItem, QGraphicsOpacityEffect, QGraphicsObject
from PyQt6.QtCore import QRectF, QAbstractAnimation, QPropertyAnimation, QObject
from PyQt6.QtGui import QCursor, QColor, QBrush
import pyqtgraph
from Widgets.Popup import Popup

# x0 [], x1 [], height [], brushes []
# y0 []
class Bars(pyqtgraph.BarGraphItem):
    def __init__(self, **opts):
        super().__init__(**opts)
        self.setAcceptHoverEvents(True)
        self.setToolTip(None)
        self.isHovered = False

        self.bars = []
        if 'brushes' in opts:
            self.brushes = opts['brushes']
            self.defaultBrushes = opts['brushes']
        self.width = opts['x1'][0] - opts['x0'][0]
        self.heights = opts['height']
        self.total = sum(self.heights)
        self.popup = None
        if 'y0' not in opts:
            opts['y0'] = [0]*len(opts['x0'])
        for i in range(len(opts['x0'])):
            bar = Bar(
                opts['x0'][i],
                opts['y0'][i],
                self.width,
                opts['height'][i]
            )
            self.bars.append(bar)
        self.hoverable = True

    def hoverEnterEvent(self,ev):
        return super().hoverEnterEvent(ev)

    def hoverMoveEvent(self,ev):
        if not self.hoverable:
            return
        contained = False
        for i in range(len(self.bars)):
            b = self.bars[i]
            if b.contains(ev.pos()):
                contained = True
                self.brushes[i].setAlpha(255)
                if self.popup == None or not self.popup.isVisible():
                    w = self.getViewWidget().window()
                    self.brushes[i].setAlpha(255)
                    val = self.heights[i]
                    perc = (val / self.total) * 100
                    txt = "%d Hunts\n%.2f%%" % (val,perc)
                    info = QWidget()
                    info.layout = QVBoxLayout()
                    info.setLayout(info.layout)
                    info.layout.addWidget(QLabel(txt))
                    self.popup = Popup(info,QCursor.pos().x()+16,QCursor.pos().y()-32)
                    self.popup.show()
                    self.popup.current = b
                    w.raise_()
                    w.activateWindow()
                elif self.popup.current != b:
                    self.popup.hide()
            else:
                self.brushes[i].setAlpha(200)
        self.setOpts()
        if not contained:
            try:
                self.popup.hide()
            except:
                self.popup = None
        self.scene().update()
        return super().hoverEnterEvent(ev)

    def hoverLeaveEvent(self,ev):
        for i in range(len(self.bars)):
            self.brushes[i].setAlpha(200)
        self.setOpts()
        try:
            self.popup.hide()
        except:
            return
        return super().hoverEnterEvent(ev)

class Bar(QGraphicsRectItem, QObject):
    def __init__(self,*args):
        super().__init__(*(args))
        self.setAcceptHoverEvents(True)
    
    def hoverEnterEvent(self, event):
        print('h')
        return super().hoverEnterEvent(event)