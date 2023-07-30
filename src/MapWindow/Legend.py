from PyQt6.QtWidgets import QWidget, QVBoxLayout,QGridLayout,QPushButton, QComboBox, QGraphicsView, QGraphicsScene,QGraphicsItem,QGraphicsRectItem
from PyQt6.QtGui import QColor

class Legend():
    def __init__(self,w,h):
        self.w = w;
        self.h = h;
        self.bg = QGraphicsRectItem(0,0,w,h)
        self.bgColor = QColor("#000000")
        self.bg.setBrush(self.bgColor)