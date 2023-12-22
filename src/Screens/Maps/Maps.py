from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QComboBox, QPushButton
from PyQt6.QtCore import Qt
from Screens.Maps.components.MapsView import MapsView, maps

class Maps(QWidget):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.selectMap = QComboBox()
        self.selectMap.view().setSpacing(4)

        for name in maps.keys():
            self.selectMap.addItem(name,maps[name])

        self.selectMap.activated.connect(self.update)

        self.current = list(maps.keys())[0]

        self.mapView = MapsView(parent=self)

        self.buttons = self.init_buttons()
        self.layout.addWidget(self.selectMap)
        self.layout.addWidget(self.buttons)
        self.layout.addWidget(self.mapView,alignment=Qt.AlignmentFlag.AlignCenter)

        self.layout.addStretch()

    def init_buttons(self):
        cmpLabelBtn = QPushButton("Compound Labels")
        cmpLabelBtn.clicked.connect(self.mapView.toggleCompoundLabels)
        cmpBorderBtn = QPushButton("Compound Borders")
        cmpBorderBtn.clicked.connect(self.mapView.toggleCompoundBorders)

        w = QWidget()
        w.layout = QHBoxLayout()
        w.setLayout(w.layout)
        w.layout.addWidget(cmpLabelBtn)
        w.layout.addWidget(cmpBorderBtn)
        return w

    def update(self):
        self.current = self.selectMap.currentText()
        self.mapView.setMap(self.current)