from PyQt6.QtWidgets  import QWidget, QVBoxLayout,QLabel,QSizePolicy,QSpacerItem
from PyQt6.QtCore import Qt

class TextArea(QWidget):
    def __init__(self,alignment=Qt.AlignmentFlag.AlignLeft) -> None:
        super().__init__()
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.layout.setAlignment(alignment)
        self.lines = {}
        self.setStyleSheet("QLabel{padding:0px;margin:0px}")

    def addLabel(self,key,label,alignment=Qt.AlignmentFlag.AlignLeft):
        self.lines[key] = label
        self.layout.addWidget(self.lines[key])
        self.lines[key].setAlignment(alignment)

    def addLine(self,key,text=None,alignment=Qt.AlignmentFlag.AlignLeft):
        self.lines[key] = QLabel(text)
        self.lines[key].setParent(self) 
        self.layout.addWidget(self.lines[key])
        self.lines[key].setAlignment(alignment)

    def get(self,key):
        self.lines[key]
        return self.lines[key]

    def set(self,key,obj):
        self.lines[key] = obj

    def addStretch(self):
        self.layout.addStretch()

    def setAlignment(self,alignment):
        self.layout.setAlignment(alignment)

    def addSpacerItem(self,height):
        self.layout.addSpacerItem(QSpacerItem(0,height,QSizePolicy.Policy.Expanding,QSizePolicy.Policy.Fixed))