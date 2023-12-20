from PyQt6.QtWidgets import QPushButton, QWidget, QSizePolicy
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QEvent, QSize, QObject, QPoint
from Widgets.Tooltip import Tooltip
from resources import MENU_ICON_SIZE

class MenuButton(QPushButton):
    def __init__(self,icon: QIcon, text: str | None = None, parent: QWidget | None = None):
        super(MenuButton,self).__init__(icon, text, parent)
        self.label = text
        self.labelHidden = True

        self.setText("")
        self.setObjectName("")
        self.setIconSize(QSize(MENU_ICON_SIZE,MENU_ICON_SIZE))

        self.setToolTip(self.label)

        self.setMouseTracking(True)
        self.installEventFilter(self)

        self.setMinimumWidth(MENU_ICON_SIZE+16)
        self.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Minimum
        )

    def setToolTip(self, a0: str) -> None:
        self.toolTip = Tooltip(a0)
        #return super().setToolTip(a0)

    def setAction(self,action):
        self.clicked.connect(lambda : action(self.label))

    def showLabel(self,expanded):
        self.setText(" "*2+self.label if expanded else "")
        self.style().polish(self)
        self.ensurePolished()

    def set_focus(self,state):
        if(state):
            #self.setStyleSheet("background-color:rgba(200,200,200,200)")
            self.setObjectName("focus")
        else:
            #self.setStyleSheet("background-color:transparent")
            self.setObjectName("")
        self.style().polish(self)
        self.ensurePolished()

    def leaveEvent(self, a0: QEvent) -> None:
        self.toolTip.hide()
        return super().leaveEvent(a0)

    def eventFilter(self, a0: QObject, a1: QEvent) -> bool:
        if a1.type() == QEvent.Type.Enter:
            self.toolTip.show(self.mapToGlobal(QPoint(self.sizeHint().width(),0)))
            self.activateWindow()
        return super().eventFilter(a0, a1)
