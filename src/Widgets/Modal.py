from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QPushButton, QSizePolicy
from PyQt6.QtCore import Qt

class Modal(QMainWindow):
    def __init__(self, parent=None,flags=Qt.WindowType.Popup):
        super().__init__(parent,flags)
        self.setObjectName("popup")
        self.body = QWidget()
        self.body.layout = QVBoxLayout()
        self.body.setLayout(self.body.layout)
        self.setCentralWidget(self.body)

        closeBtn = QPushButton("OK")
        closeBtn.setSizePolicy(QSizePolicy.Policy.Fixed,QSizePolicy.Policy.Fixed)
        closeBtn.clicked.connect(self.close)
        closeBtn.clicked.connect(self.deleteLater)
        closeBtn.clicked.connect(lambda : self.setParent(None))
        self.body.layout.addWidget(closeBtn,0,Qt.AlignmentFlag.AlignCenter)

        self.body.layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

    def addWidget(self,widget):
        self.body.layout.insertWidget(self.body.layout.count()-1,widget,0,Qt.AlignmentFlag.AlignCenter)
        self.body.layout.setAlignment(widget,Qt.AlignmentFlag.AlignCenter)
        self.adjustSize()
        self.move(
            int(self.parent().window().pos().x() + self.parent().window().width()/2 - self.width()/2),
            int(self.parent().window().pos().y() + self.parent().window().height()/2 - self.height()/2),
        )