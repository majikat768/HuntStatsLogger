from PyQt6.QtWidgets import QWidget, QTabBar, QVBoxLayout, QHBoxLayout, QSizePolicy

class Body(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("body")
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0,0,0,0)

        self.tabBar = TabBar(self)
        self.stack = Stack(self)

        self.tabBar.tabBarClicked.connect(self.setTab)

        self.layout.addWidget(self.tabBar)
        self.layout.addWidget(self.stack)

    def setTab(self,index):
        if self.stack.currentIndex != index:
            self.stack.setCurrentIndex(index)

    def addTab(self,widget, title = None):
        self.tabBar.addTab(title)
        self.stack.addWidget(widget)

class Stack(QWidget):
    def __init__(self, parent: QWidget | None = None )-> None:
        super().__init__(parent)
        self.setObjectName("bodyStack")
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.setSizePolicy(QSizePolicy.Policy.Expanding,QSizePolicy.Policy.Expanding)

        self.widgets = []
        self.currentIndex = -1

    def addWidget(self,widget):
        for w in self.widgets:
            w.setVisible(False)
        self.widgets.append(widget)
        self.layout.addWidget(widget)
        widget.setVisible(True)

        self.setCurrentIndex(0)

    def setCurrentIndex(self,i):
        for w in self.widgets:
            w.setVisible(False)
        dict(enumerate(self.widgets))[i].setVisible(True)
        self.currentIndex = i

class TabBar(QTabBar):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("tabBar")
        self.layout = QHBoxLayout()
        self.setLayout(self.layout)
        self.layout.setSpacing(0)
        self.setContentsMargins(0,0,0,0)