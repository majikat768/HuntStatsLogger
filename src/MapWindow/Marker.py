from PyQt6.QtWidgets import QGraphicsEllipseItem, QGraphicsTextItem, QGraphicsDropShadowEffect, QGraphicsPolygonItem, QGraphicsBlurEffect
from PyQt6.QtGui import QColor, QBrush, QPen, QFont, QPolygonF
from PyQt6.QtCore import QPointF

class Marker(QGraphicsEllipseItem):
    def __init__(self, parent=None,x=0,y=0,brushColor=QColor("#000000"),penColor=QColor("#ffffff"),size=16):
        super().__init__(x,y,size,size,parent)
        self.brush = QBrush(brushColor)
        self.pen = QPen(penColor)
        self.x = x
        self.y = y
        self.setBrush(self.brush)
        self.setPen(self.pen)

        #self.text = ("(%.0f %.0f)" % (self.x,self.y))
        #self.textBox = QGraphicsTextItem(self.text)
        #self.textBox.setFont(QFont("mono",24))
        #self.textBox.setPos(self.x,self.y)
        #self.textBox.setZValue(2)
        self.setZValue(1)

    def toggle(self):
        if self.zValue() > 0:
            self.setZValue(-1)
        else:
            self.setZValue(1)

class Label(QGraphicsTextItem):
    def __init__(self,text,parent=None,x=0,y=0):
        super().__init__(text,parent)
        self.text = text
        self.font = QFont("Libre Baskerville",10)
        self.font.setBold(True)
        self.setFont(self.font)
        self.w = self.boundingRect().width()
        self.h = self.boundingRect().height()
        self.x = x - self.w//2
        self.y = y - self.h//2
        self.setPos(self.x,self.y)
        self.setDefaultTextColor(QColor("#ffffff"))
        self.shadow = self.setShadow()
        self.setGraphicsEffect(self.shadow)
        self.setZValue(1)

    def setShadow(self):
        shadow = QGraphicsDropShadowEffect()
        shadow.setColor(QColor("#000000"))
        shadow.setBlurRadius(8)
        shadow.setOffset(4,4)

        return shadow

    def setBlur(self):
        blur = QGraphicsBlurEffect()
        blur.setBlurRadius(1)

        return blur

    def toggle(self):
        if self.zValue() > 0:
            self.setZValue(-1)
        else:
            self.setZValue(1)

    def paint(self, painter, option, widget) -> None:
        return super().paint(painter, option, widget)

class Border(QGraphicsPolygonItem):
    def __init__(self,verts=None,parent=None):
        super().__init__(parent)
        self.verts = verts
        self.pen = QPen(QColor("#aadd0000"))
        self.brush = QBrush(QColor("#00000000"))
        self.pen.setWidth(8)
        self.setPolygon(QPolygonF([QPointF(v['x'],v['y']) for v in self.verts]))
        self.setBrush(self.brush)
        self.setPen(self.pen)
        self.setZValue(-1)

    def paint(self, painter, option, widget) -> None:
        return super().paint(painter, option, widget)

    def toggle(self):
        if self.zValue() > 0:
            self.setZValue(-1)
        else:
            self.setZValue(1)