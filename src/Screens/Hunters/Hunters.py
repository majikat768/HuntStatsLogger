from PyQt6.QtWidgets import QWidget, QHBoxLayout, QSizePolicy
from PyQt6.QtCore import Qt
from Screens.Hunters.components.MostKilled import MostKilled
from Screens.Hunters.components.MostKilledBy import MostKilledBy
from Screens.Hunters.components.MostSeen import MostSeen

class Hunters(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground)      
        self.setObjectName("HuntersTable")

        self.layout = QHBoxLayout()
        self.setLayout(self.layout)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self.layout.setSpacing(0)

        self.mostKilled = MostKilled()
        self.mostKilledBy = MostKilledBy()
        self.mostSeen = MostSeen()

        self.setSizePolicy(QSizePolicy.Policy.Expanding,QSizePolicy.Policy.Fixed)

        self.layout.addWidget(self.mostKilled)
        self.layout.addWidget(self.mostSeen)
        self.layout.addWidget(self.mostKilledBy)