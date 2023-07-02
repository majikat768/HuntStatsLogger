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
        self.layout.setContentsMargins(0,0,0,0)
        self.layout.setSpacing(0)
        self.setContentsMargins(0,0,0,0)
        self.setSizePolicy(QSizePolicy.Policy.Expanding,QSizePolicy.Policy.Expanding)

        self.main = QWidget()
        self.main.setObjectName("bodyStackMain")
        self.main.layout = QVBoxLayout()
        self.main.setLayout(self.main.layout)
        self.main.layout.setContentsMargins(0,0,0,0)
        self.main.layout.setSpacing(0)
        self.main.setContentsMargins(0,0,0,0)
        self.main.setSizePolicy(QSizePolicy.Policy.Expanding,QSizePolicy.Policy.Expanding)

        self.layout.addWidget(self.main)

        self.widgets = []
        self.currentIndex = -1

    def addWidget(self,widget):
        for w in self.widgets:
            w.setVisible(False)
        self.widgets.append(widget)
        self.main.layout.addWidget(widget)
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