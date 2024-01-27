from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QSizePolicy
from PyQt6.QtCore import Qt
from Screens.Hunters.components.MostKilled import MostKilled
from Screens.Hunters.components.MostKilledBy import MostKilledBy
from Screens.Hunters.components.MostSeen import MostSeen
from Screens.Hunters.components.HunterSearch import HunterSearch

class Hunters(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground)      
        self.setObjectName("HuntersTable")

        self.body = QWidget()
        self.body.layout = QHBoxLayout()
        self.body.setLayout(self.body.layout)
        self.body.layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.body.layout.setSpacing(0)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.mostKilled = MostKilled()
        self.mostKilledBy = MostKilledBy()
        self.mostSeen = MostSeen()
        self.search = HunterSearch()

        self.body.setSizePolicy(QSizePolicy.Policy.Expanding,QSizePolicy.Policy.Fixed)

        self.body.layout.addWidget(self.mostKilled)
        self.body.layout.addWidget(self.mostSeen)
        self.body.layout.addWidget(self.mostKilledBy)
        self.layout.addWidget(self.body)
        self.layout.addWidget(self.search)
        self.layout.addStretch()