import pyqtgraph
from PyQt6.QtGui import QColor, QFont,QPen,QBrush
from PyQt6.QtCore import QRectF

class PlotItem(pyqtgraph.PlotItem):
    def __init__(self, parent=None, name=None, labels=None, title=None, viewBox=None, axisItems=None, enableMenu=True, **kargs):
        super().__init__(parent, name, labels, title, viewBox, axisItems, enableMenu, **kargs)
        self.getAxis("left").setTextPen(QPen(QColor("#fff")))
        self.getAxis("bottom").setTextPen(QPen(QColor("#fff")))
        self.getViewBox().setBackgroundColor(QColor("#111111"))

    def paint(self,painter,*args):
        painter.setPen(QPen(QColor("#cccccc")))
        painter.setBrush(QBrush(QColor("#232323")))
        r = self.boundingRect()
        '''
        painter.drawRect(QRectF(
            r.x()-1,
            r.y()-1,
            r.width()+2,
            r.height()+2
        ))
        '''
        pyqtgraph.PlotItem.paint(self,painter,*args)

    def setTitle(self, title=None, **args):
        return super().setTitle(title, color="#fff", **args)
