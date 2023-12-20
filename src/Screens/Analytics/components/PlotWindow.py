
from PyQt6.QtGui import QColor, QFont, QPen
from PyQt6.QtCore import QRectF
import pyqtgraph

class PlotWindow(pyqtgraph.GraphicsLayoutWidget):
    def __init__(self, parent=None, show=False, size=None, title=None, **kargs):
        super().__init__(parent, show, size, title, **kargs)