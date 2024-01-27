from PyQt6.QtGui import QResizeEvent
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QGridLayout, QLabel,QSizePolicy,QSpacerItem, QScrollArea, QGroupBox, QTableWidget,QTableWidgetItem, QAbstractItemView, QHeaderView, QPushButton
from PyQt6 import QtCore, QtGui
from DbHandler import get_hunt_timeline
from resources import settings, hunter_name

class TimelineWidget(QGroupBox):
    def __init__(self, game_id, parent: QWidget | None = None):
        super().__init__(parent)
        self.game_id = game_id
        self.data = {}
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_StyledBackground)      

        self.main = QWidget()
        self.main.layout = QGridLayout()
        self.main.setLayout(self.main.layout)
        self.main.layout.setSpacing(0)

        #self.scrollarea = QScrollArea()
        #self.main = QWidget()
        #self.scrollarea.setWidgetResizable(True)
        #self.scrollarea.setWidget(self.main)
        #self.main.layout = QVBoxLayout()
        #self.main.setLayout(self.main.layout)
        #self.layout.addWidget(self.scrollarea)

        self.setTitle("TIMELINE")
        self.setSizePolicy(QSizePolicy.Policy.Expanding,QSizePolicy.Policy.Fixed)
        self.layout.setContentsMargins(1,8,1,1)
        self.main.layout.setContentsMargins(1,1,1,1)
        self.main.setSizePolicy(QSizePolicy.Policy.Expanding,QSizePolicy.Policy.Expanding)

        self.hideButton = QPushButton("hide",parent=self)
        self.hideButton.clicked.connect(self.toggleTimeline)
        self.hideButton.setFixedSize(self.hideButton.sizeHint())

    def toggleTimeline(self):
        if self.main.isVisible():
            self.main.setVisible(False)
            self.setTitle("")
            self.hideButton.setText("+")
            self.hideButton.setFixedSize(self.hideButton.sizeHint())
            self.setMaximumWidth(self.hideButton.sizeHint().width())
        else:
            self.main.setVisible(True)
            self.setTitle("Timeline")
            self.hideButton.setText("hide")
            self.hideButton.setFixedSize(self.hideButton.sizeHint())
            self.setMaximumWidth(self.window().sizeHint().width())


    def init(self):
        if len(self.data) == 0:
            self.data = get_hunt_timeline(self.game_id)
            #self.main.setRowCount(len(self.data))
            for i in range(len(self.data)):
                event = self.data[i]
                row = QWidget()
                row.layout = QVBoxLayout()
                row.setLayout(row.layout)
                ts = QLabel(event['timestamp'])
                ts.setObjectName("timestamp")
                [txt,tag, align] = event_text(event)
                ev = QLabel(txt)
                ev.setWordWrap(True)
                ev.setObjectName(tag)
                self.main.layout.addWidget(ts,i+1,0,1,1)
                self.main.layout.addWidget(ev,i+1,1,1,1)
                #row.layout.addWidget(ts)
                #row.layout.addWidget(ev)
                #row.layout.setSpacing(0)
                #row.setObjectName(tag)
                #self.main.layout.addWidget(row)
                #self.layout.setAlignment(row,align)
            self.setMinimumHeight(self.sizeHint().height())
            self.main.layout.setColumnStretch(1,1)
            self.main.layout.setRowStretch(self.main.layout.rowCount(),1)
            self.layout.addWidget(self.main)

    def resizeEvent(self, a0: QResizeEvent) -> None:
        self.hideButton.move(self.width()-self.hideButton.sizeHint().width(),0)
        return super().resizeEvent(a0)

def event_text(event):
    my_name = settings.value("steam_name", "you")
    hunter = hunter_name(event['blood_line_name'])
    e = event['event']
    txt = ""
    tag = ""
    align = QtCore.Qt.AlignmentFlag.AlignRight
    if "bounty" in e:
        action = " got the bounty" if "pickedup" in e else " extracted with the bounty"
        txt = hunter + action
        tag = "BountyEvent"
        align = QtCore.Qt.AlignmentFlag.AlignCenter
    elif "by" in e:
        action = " killed " if "killed" in e else " downed "
        hunter2 = "Your teammate" if "teammate" in e else "You"      # haha
        txt = hunter2 + action + hunter
        tag = "KilledByEvent"
        align = QtCore.Qt.AlignmentFlag.AlignLeft
    else:
        action = " killed " if "killed" in e else " downed "
        hunter2 = "your teammate" if "teammate" in e else "you" # haha
        txt = hunter + action + hunter2
        tag = "KilledEvent"
        align = QtCore.Qt.AlignmentFlag.AlignRight
    return [txt,tag,align]

    if event == 'downedme':
        pass
    elif event == 'downedbyme':
        pass
    elif event == 'downedbyteammate':
        pass