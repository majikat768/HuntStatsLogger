from PyQt6.QtWidgets import QGroupBox, QWidget, QVBoxLayout, QHBoxLayout, QLabel,QSizePolicy, QPushButton
from PyQt6 import QtGui
from PyQt6.QtCore import QEvent, Qt, QSize
from resources import clearLayout, get_icon, star_path, mmr_to_stars

icon_size = 16

class TeamButton(QPushButton):
    def __init__(self,teamMmr,text=None,parent=None):
        super().__init__(parent=parent)
        self.parent = parent

        self.setObjectName("TeamButton")
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.setMouseTracking(True)

        self.title = text
        self.titleLabel = QLabel(self.title)

        self.stars = "<img src='%s'>" % (star_path())*mmr_to_stars(teamMmr)
            
        self.layout.addWidget(self.titleLabel)
        self.layout.addWidget(QLabel(self.stars))
        self.setSizePolicy(QSizePolicy.Policy.Fixed,QSizePolicy.Policy.Fixed)
        self.ownTeam = False
        self.icons = []

    def setWidget(self,widget,func):
        self.widget = widget
        self.func = func
    
    def setIcons(self,icons):
        self.icons = "<img src='%s'>"
        for i in range(len(icons)):
            icons[i] = "<img src='%s' height=%d width=%d>" % (icons[i],icon_size,icon_size)
        lbl = QLabel(''.join(icons))
        lbl.setFixedHeight(icon_size)
        self.layout.addWidget(lbl)
        self.layout.addStretch()
        self.setFixedHeight(int(self.sizeHint().height()*1.5))
        self.setFixedWidth(int(self.sizeHint().width()*2))

    def select(self):
        self.setStyleSheet("\
                           TeamButton {\
                            font-size:12px;\
                            background-color:#452e383c;\
                            border: 2px solid #a9b7c6;\
                            border-radius: 4px;\
                            padding:16px 4px;\
                        }\
                        TeamButton:hover {\
                            background: #45cccccc;\
                            border-color: #a9d7d6;\
                        }\
                    ")
    
    def unselect(self):
        self.setStyleSheet("\
                           TeamButton {\
                            font-size:12px;\
                            background: #45000000;\
                            border: 1px solid #a9b7c6;\
                            border-radius: 4px;\
                            padding:16px 4px;\
                        }\
                        TeamButton:hover {\
                            background: #45cccccc;\
                            border-color: #a9d7d6;\
                        }\
                    ")

    def mousePressEvent(self, e: QtGui.QMouseEvent) -> None:
        self.func(self.widget)
        for b in self.parent.buttons:
            b.unselect()
        self.select()
        return super().mousePressEvent(e)
