from PyQt6.QtWidgets import QWidget, QPushButton, QScrollArea, QVBoxLayout, QGridLayout, QSizePolicy
from PyQt6.QtCore import Qt, QEvent

line_height = 24
class ScrollWidget(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.layout = QGridLayout()
        self.setLayout(self.layout)

        self.layout.setContentsMargins(0,0,0,0)
        self.setContentsMargins(0,0,0,0)
        self.layout.setSpacing(0)

        self.upArrow = ScrollButton(direction='up',parent=self)
        self.downArrow = ScrollButton(direction='down',parent=self)
        self.scrollArea = ScrollArea(self)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setSizePolicy(QSizePolicy.Policy.MinimumExpanding,QSizePolicy.Policy.Expanding)
        self.scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scrollBar = self.scrollArea.verticalScrollBar()
        self.setSizePolicy(QSizePolicy.Policy.MinimumExpanding,QSizePolicy.Policy.Expanding)

        self.main = QWidget()
        self.main.setObjectName("ScrollAreaMain")
        self.main.layout = QVBoxLayout()
        self.main.setLayout(self.main.layout)
        self.scrollArea.setWidget(self.main)

        self.layout.addWidget(self.scrollArea,0,0,3,1)
        self.layout.addWidget(self.upArrow,0,0,1,1)
        self.layout.addWidget(self.downArrow,2,0,1,1)
        self.layout.setRowStretch(1,1)


    def addWidget(self,widget):
        self.main.layout.addWidget(widget)
        self.toggleButtons()

    def scrollDown(self):
        self.scrollBar.setValue(self.scrollBar.value() + line_height)
        self.toggleButtons()

    def scrollUp(self):
        self.scrollBar.setValue(self.scrollBar.value() - line_height)
        self.toggleButtons()

    def toggleButtons(self):
        self.upArrow.setVisible(self.scrollBar.value() > 0)
        self.downArrow.setVisible(self.scrollBar.value() < self.scrollBar.maximum())

    def update(*args):
        return



class ScrollButton(QPushButton):
    def __init__(self,direction=None,parent=None):
        super().__init__()
        self.direction = direction
        self.scrolling = False
        self.scrollArea = parent
        if self.direction == 'up':
            self.setObjectName("ScrollUpButton") 
            self.clicked.connect(parent.scrollUp)
        elif self.direction == 'down':
            self.setObjectName("ScrollDownButton") 
            self.clicked.connect(parent.scrollDown)
        self.installEventFilter(self)

    def eventFilter(self,obj,event):
        if(event.type() == QEvent.Type.MouseButtonPress):
            self.scrolling = True
        elif(event.type() == QEvent.Type.MouseButtonRelease):
            self.scrolling = False
        return super().eventFilter(obj, event)

class ScrollArea(QScrollArea):
    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)

    def wheelEvent(self, a0) -> None:
        super().wheelEvent(a0)
        self.parent().toggleButtons()
