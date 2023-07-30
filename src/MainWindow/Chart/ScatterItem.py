import pyqtgraph
from PyQt6.QtWidgets import QLabel, QWidget, QVBoxLayout, QApplication
from PyQt6.QtGui import QCursor
from Widgets.Popup import Popup
from Widgets.Label import Label
from resources import unix_to_datetime, GoToHuntPage

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
        if 'tip' in kargs:
            kargs['tip'] = None
        if 'parent' in kargs:
            self.parent = kargs.pop('parent')
        else:
            self.parent = None
        self.size = kargs['size']
        self.hoverSize = kargs['hoverSize']
        super().__init__(*args, **kargs)
        self.sigHovered.connect(self.mouseOver)
        self.sigClicked.connect(self.handleClick)

        self.isHovered = False
        self.stop = False

    def mouseOver(self,obj,pts,ev):
        if self.stop:
            return
        if len(pts) > 0:
            pt = pts[0]
            p1 = pt.pos()
            p2 = ev.pos()
            ptHovered = abs(p1.x() - p2.x()) < self.hoverSize*2 and abs(p1.y()-p2.y()) < self.hoverSize*2
            if not self.isHovered and ptHovered:
                pos = QCursor.pos()
                info = QWidget()
                info.layout = QVBoxLayout()
                info.setLayout(info.layout)
                # determines if data is MMR or KDA.
                # not perfect, because technically one's MMR could be < 1000, or KDA could be > 1000....
                # but probably won't be.
                if pt.pos().y() > 1000:
                    info.layout.addWidget(Label("%s\n%d" % (unix_to_datetime(pt.data()),pt.pos().y())))
                else:
                    info.layout.addWidget(Label("%s\n%.3f" % (unix_to_datetime(pt.data()),pt.pos().y())))

                w = self.getViewWidget().window()
                self.isHovered = True
                self.popup = Popup(info,pos.x()+32,pos.y())
                self.popup.show()
                w.raise_()
                w.activateWindow()

            elif self.isHovered and not ptHovered:
                self.isHovered = False
                self.popup.hide()
        else:
            self.isHovered = False
            try:
                self.popup.hide()
            except:
                return

    def handleClick(self,obj,pts,ev):
        if self.parent == None:
            return
        if len(pts) == 0:
            return
        self.stop = True
        pt = pts[0]
        mainframe = self.parent.window().mainframe
        GoToHuntPage(pt.data(),mainframe)
        if self.popup:
            self.popup.hide()
            self.popup = None
            self.stop = False