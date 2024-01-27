from PyQt6.QtCore import QEvent, QObject, QPoint
from PyQt6.QtGui import QResizeEvent
from PyQt6.QtWidgets import QLabel
from Widgets.Tooltip import Tooltip

class Label(QLabel):
    def __init__(self,text='',parent=None):
        if(parent != None):
            super().__init__(text,parent)
        else:
            super().__init__(text)
        self.toolTip = None
        self.setMouseTracking(True)
        self.installEventFilter(self)


    def setText(self, a0: str) -> None:
        return super().setText(a0)

    def setToolTip(self, a0: str) -> None:
        self.toolTip = Tooltip(str(a0))
        #return super().setToolTip(a0)

    def leaveEvent(self, a0: QEvent) -> None:
        if self.toolTip != None:
            self.toolTip.hide()
        return super().leaveEvent(a0)

    def eventFilter(self, a0: QObject, a1: QEvent) -> bool:
        if a1.type() == QEvent.Type.Enter and self.toolTip != None:
            self.toolTip.show(self.mapToGlobal(QPoint(self.sizeHint().width(),0)))
            self.activateWindow()
        return super().eventFilter(a0, a1)