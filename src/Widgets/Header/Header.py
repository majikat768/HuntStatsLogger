from PyQt6.QtWidgets import QWidget, QLabel, QHBoxLayout, QVBoxLayout, QSizePolicy
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6 import QtCore
from PyQt6.QtCore import Qt
from resources import resource_path
from Widgets.Header.MMR import MMR
from Widgets.KDA import KDA

class Header(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.layout.setContentsMargins(0,0,0,0)
        self.layout.setSpacing(0)

        self.main = QWidget()
        self.main.setObjectName("Header")
        self.layout.addWidget(self.main)
        self.KDA = KDA()
        self.layout.addWidget(self.KDA)

        self.main.layout = QHBoxLayout()
        self.main.setLayout(self.main.layout)

        self.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Minimum
        )

        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_StyledBackground)      
        self.currentWidget = QLabel("MATCH RECAP")
        self.currentWidget.setObjectName("current-view")

        self.mmr = MMR()

        self.logoWidget = QWidget()
        self.logoWidget.layout = QHBoxLayout()
        self.logoWidget.layout.setContentsMargins(0,0,0,0)
        self.logoWidget.setLayout(self.logoWidget.layout)
        self.logoWidget.setObjectName("HeaderLogo")
        self.logo = QIcon(resource_path("assets/icons/hsl.ico"))
        self.logo = QLabel()
        self.logo.setPixmap(QPixmap(resource_path("assets/icons/hsl.ico")).scaled(48,48))
        self.logoWidget.layout.addWidget(QLabel("Hunt"))
        self.logoWidget.layout.addWidget(self.logo)
        self.logoWidget.layout.addWidget(QLabel("Logger"))

        self.main.layout.addWidget(self.currentWidget, stretch=1)
        self.main.layout.addWidget(self.logoWidget, stretch=0)
        self.main.layout.addWidget(self.mmr, stretch=1)

        self.setFixedHeight(self.sizeHint().height()+4)

    def setWidgetName(self,text):
        self.currentWidget.setText(text.upper())

    def update(self):
        self.KDA.update()
        self.mmr.update()