from PyQt6.QtGui import QResizeEvent
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QStackedWidget, QScrollArea, QSizePolicy
from PyQt6.QtCore import QEvent, QObject, Qt
from Widgets.Header.Header import Header;
from Screens.HuntsRecap.HuntsRecap import HuntsRecap
from Screens.MyTeams.MyTeams import MyTeams
from Screens.Hunters.Hunters import Hunters
from Screens.Analytics.Analytics import Analytics
from Screens.Records.Records import Records

class Body(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0,0,0,0)
        self.layout.setSpacing(0)
        self.setLayout(self.layout)
        self.setMouseTracking(True)
        self.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Fixed,
        )

        self.header = Header(self)

        self.layout.addWidget(self.header)

        self.scrollArea = QScrollArea()
        self.scrollArea.setWidgetResizable(True)
        self.main = QWidget()
        self.main.layout = QVBoxLayout()
        self.main.setLayout(self.main.layout)
        self.stack = QStackedWidget(self)
        self.layout.addWidget(self.scrollArea)
        self.scrollArea.setWidget(self.stack)
        self.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.stack.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Minimum,
        )

        self.stack.installEventFilter(self)

        self.widgets = {
            "Hunts Recap": HuntsRecap(parent=self),
            "Hunters": Hunters(parent=self),
            "Teams": MyTeams(parent=self),
            "Analytics":Analytics(parent=self),
            "Records":Records(parent=self)
        }

        for w in self.widgets:
            self.stack.addWidget(self.widgets[w])
        self.setCurrentWidget("Hunts Recap")

    def update(self):
        self.header.update()
        self.stack.currentWidget().update()

    def setCurrentWidget(self,button):
        if(button in self.widgets):
            self.stack.setCurrentWidget(self.widgets[button])
            self.stack.currentWidget().update()
            self.header.setWidgetName(button)

    def resizeEvent(self, a0: QResizeEvent) -> None:
        return super().resizeEvent(a0)

    def eventFilter(self, a0: QObject, a1: QEvent) -> bool:
        return super().eventFilter(a0, a1)