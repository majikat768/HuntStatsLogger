from PyQt6.QtWidgets import QGraphicsLineItem
from PyQt6.QtCore import Qt, QLineF, QPointF
from PyQt6.QtGui import QPen, QColor

class Ruler(QGraphicsLineItem):
    def __init__(self):
        super().__init__()
        self.line = QLineF(-1,-1,-1,-1)
        self.pen = QPen(QColor("#cc0000"))
        self.pen.setStyle(Qt.PenStyle.DashLine)
        self.pen.setWidth(4)
        self.setPen(self.pen)
        self.setZValue(8)
        self.setLine(self.line)

    def setStart(self,x,y):
        self.line.setP1(QPointF(x,y))
        self.line.setP2(QPointF(x,y))
        self.setLine(self.line)

    def setEnd(self,x,y):
        self.line.setP2(QPointF(x,y))
        self.setLine(self.line)

    def moveEnd(self,x,y):
        self.pen.setDashPattern([self.length()/64,self.length()/64])
        self.line.setP2(QPointF(x,y))
        self.setLine(self.line)
        self.scene().update()

    def clear(self):
        self.line.setP1(QPointF(-1,-1))
        self.line.setP2(QPointF(-1,-1))

    def length(self):
        return self.line.length()