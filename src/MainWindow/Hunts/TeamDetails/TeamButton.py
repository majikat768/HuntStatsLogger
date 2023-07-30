from PyQt6.QtWidgets import QGroupBox, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,QSizePolicy, QPushButton
from PyQt6 import QtGui
from PyQt6.QtCore import QEvent, Qt, QSize
from resources import clearLayout, get_icon, star_path, mmr_to_stars, chevronDownIcon, chevronRightIcon 
from Widgets.Label import Label

icon_size = 16

default_stylesheet = "TeamButton {\
                       font-size:12px;\
                       background: #45000000;\
                       /*border: 1px solid #a9b7c6;*/\
                       border:0px;\
                       border-radius: 4px;\
                        margin:4px;\
                    }\
                    TeamButton:hover {\
                        background: #45cccccc;\
                        border-color: #a9d7d6;\
                    }"
selected_stylesheet = "TeamButton {\
                       font-size:12px;\
                       background-color:#452e383c;\
                       border: 2px solid #66a9b7c6;\
                       margin:4px;\
                       border-radius: 4px;\
                    }\
                    TeamButton:hover {\
                        background: #45cccccc;\
                        border-color: #a9d7d6;\
                    }"
class TeamButton(QPushButton):
    def __init__(self,text=None,parent=None):
        super().__init__(parent=parent)
        self.parent = parent

        self.setObjectName("TeamButton")
        self.layout = QGridLayout()
        self.setLayout(self.layout)
        self.setMouseTracking(True)
        self.setCursor(QtGui.QCursor(Qt.CursorShape.PointingHandCursor))
        #self.setSizePolicy(QSizePolicy.Policy.Fixed,QSizePolicy.Policy.Fixed)
        self.chevronWidget = Label("<img src='%s' height=16 width=16>" % chevronRightIcon)
        self.chevronWidget.setStyleSheet("QLabel{padding-right:16px;}")
        self.layout.addWidget(self.chevronWidget,0,0,1,1)

    def setWidget(self,widget,func):
        self.widget = widget
        self.func = func
    
    def select(self):
        self.setStyleSheet(selected_stylesheet)
        self.chevronWidget.setText("<img src='%s' height=16 width=16>" % chevronDownIcon)
    
    def unselect(self):
        self.setStyleSheet(default_stylesheet)
        self.chevronWidget.setText("<img src='%s' height=16 width=16>" % chevronRightIcon)

    def mousePressEvent(self, e: QtGui.QMouseEvent) -> None:
        self.widget.setVisible(not self.widget.isVisible())
        if self.widget.isVisible():
            self.select()
        else:
            self.unselect()
        return super().mousePressEvent(e)

