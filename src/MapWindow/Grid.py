from PyQt6.QtWidgets import QGraphicsLineItem, QGraphicsItem, QWidget
from PyQt6.QtCore import Qt, QRectF
from PyQt6.QtGui import QPen, QColor
import typing

class Grid(QGraphicsItem):
    def __init__(self, size=0, n=0, parent=None) -> None:
        super().__init__(parent)
        self.size = size
        self.n = n
        self.lines = []

        self.step = self.size//n

        pen = QPen(QColor("#66000000"))
        pen.setWidth(2)
        pen.setStyle(Qt.PenStyle.DashLine)
        pen.setDashPattern([2,2])
        for i in range(1,self.n):
            x = i*self.step
            line = QGraphicsLineItem(x,0,x,self.size)
            line.setPen(pen)
            self.lines.append(line)
        for j in range(1,self.n):
            y = j*self.step
            line = QGraphicsLineItem(0,y,self.size,y)
            line.setZValue(3)
            line.setPen(pen)
            self.lines.append(line)
        self.setZValue(4)

    def boundingRect(self):
        return QRectF(0,0,self.size,self.size)

    def paint(self, painter,option, widget):
        for line in self.lines:
            line.paint(painter,option,widget)