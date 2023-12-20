from PyQt6.QtWidgets import QWidget, QVBoxLayout, QSizePolicy, QLabel
from PyQt6.QtCore import Qt
from datetime import datetime

class RecordWidget(QWidget):
    def __init__(self, value, timestamp, title, parent: QWidget | None = None):
        super().__init__(parent)
        self.setObjectName("RecordWidget")
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Fixed,
        )
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground)      
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0,0,0,0)


        titleWidget = QWidget()
        titleWidget.setObjectName("RecordTitle")
        titleWidget.layout = QVBoxLayout()
        titleWidget.setLayout(titleWidget.layout)
        titleWidget.layout.addWidget(QLabel(title),alignment=Qt.AlignmentFlag.AlignCenter)

        self.layout.addWidget(titleWidget)

        bodyWidget = QWidget()
        bodyWidget.setObjectName("RecordBody")
        bodyWidget.layout = QVBoxLayout()
        bodyWidget.setLayout(bodyWidget.layout)
        bodyWidget.layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        valLabel = QLabel(str(value))
        valLabel.setObjectName("RecordValue")
        bodyWidget.layout.addWidget(valLabel,alignment=Qt.AlignmentFlag.AlignCenter)
        dtLabel = QLabel(datetime.fromtimestamp(timestamp).strftime("%H:%M\n%d %b %Y"))
        dtLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        bodyWidget.layout.addWidget(dtLabel,alignment=Qt.AlignmentFlag.AlignCenter)
        bodyWidget.setContentsMargins(8,8,8,8)

        self.layout.addWidget(bodyWidget)