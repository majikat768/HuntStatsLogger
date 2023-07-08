from PyQt6.QtWidgets import QWidget,QGroupBox, QLabel, QVBoxLayout, QScrollArea, QSizePolicy, QApplication,QWidgetItem,QLayoutItem
from PyQt6.QtCore import Qt
from DbHandler import GetMatchTimestamps, GetHunterFromGame
from Widgets.ScrollWidget import ScrollWidget 
from resources import clearLayout

class Timeline(ScrollWidget):
    def __init__(self,parent=None):
        super().__init__()
        self.main.setObjectName("Timeline")

    def update(self,ts):
        clearLayout(self.main.layout)
        self.timestamps = GetMatchTimestamps(ts)
        titleLabel = QLabel("Timeline")
        subtitleLabel = QLabel()
        titleLabel.setStyleSheet("QLabel{font-size:16px;color:#cccc67;}")
        self.addWidget(titleLabel)
        self.addWidget(subtitleLabel)
        self.addWidget(QLabel())
        for e in self.timestamps:
            eventWidget = QWidget()
            eventWidget.layout = QVBoxLayout()
            eventWidget.setLayout(eventWidget.layout)

            timestamp = e['timestamp']
            event = e['event']
            team_num = e['hunter'].split("_")[0]
            hunter_num = e['hunter'].split("_")[1] 
            hunter = GetHunterFromGame(hunter_num,team_num,e['game_id'])
            tsLbl = QLabel(timestamp)
            tsLbl.setStyleSheet("QLabel{font-weight:bold;}")
            eventLbl = QLabel(GetEventText(event,hunter))
            #eventLbl.setWordWrap(True)
            eventWidget.layout.addWidget(tsLbl)
            eventWidget.layout.addWidget(eventLbl)

            lbl = QLabel("%s<br>%s" % (timestamp,GetEventText(event,hunter)))
            #lbl.setWordWrap(True)
            #eventWidget.layout.addWidget(lbl)
            SetEventType(eventWidget,event)
            eventWidget.layout.setSizeConstraint(QVBoxLayout.SizeConstraint.SetMinimumSize)
            eventWidget.setSizePolicy(
            QSizePolicy.Policy.MinimumExpanding,
            QSizePolicy.Policy.Minimum)
            eventWidget.resize(eventWidget.sizeHint())
            self.addWidget(eventWidget)

        if len(self.timestamps) > 0:
            subtitleLabel.setText("Duration: %s" % self.timestamps[-1]['timestamp'])
        self.main.layout.addStretch()
        QApplication.processEvents()

def GetEventText(event,hunter):
    s = None
    if "bounty" in event:
        if event == "bountypickedup":
            s = "%s\npicked up the bounty." 
        elif event == "bountyextracted":
            s = "%s\nextracted with a bounty." 
    elif "downed" in event:
        if event == "downedbyteammate":
            s = "Your teammate\ndowned %s." 
        elif event == "downedbyme":
            s = "You\ndowned %s." 
        if event == "downedteammate":
            s = "%s\ndowned your teammate." 
        elif event == "downedme":
            s = "%s\ndowned you." 
    elif "killed" in event:
        if event == "killedbyteammate":
            s = "Your teammate\nkilled %s." 
        elif event == "killedbyme":
            s = "You\nkilled %s." 
        if event == "killedteammate":
            s = "%s\nkilled your teammate." 
        elif event == "killedme":
            s = "%s\nkilled you." 
    if s == None:
        return event
    return s % hunter

def SetEventType(widget,event):
    if "bounty" in event:
        widget.setObjectName("BountyEventWidget")
        #for i in range(widget.layout.count()):
        #    widget.layout.itemAt(i).setAlignment(Qt.AlignmentFlag.AlignCenter|Qt.AlignmentFlag.AlignTop)
    elif "byme" in event or "byteammate" in event:
        widget.setObjectName("KilledByEventWidget")
    elif "me" in event or "teammate" in event:
        widget.setObjectName("KilledEventWidget")
        for i in range(widget.layout.count()):
            widget.layout.itemAt(i).widget().setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTop)
            widget.layout.itemAt(i).widget().adjustSize()


    else:
        widget.setObjectName("BountyEventWidget")
    widget.adjustSize()