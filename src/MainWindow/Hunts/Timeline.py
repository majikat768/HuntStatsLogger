from PyQt6.QtWidgets import QWidget,QGroupBox, QLabel, QVBoxLayout, QScrollArea, QSizePolicy
from PyQt6.QtCore import Qt
from DbHandler import GetHuntTimestamps, GetHunterFromGame
from resources import clearLayout

class Timeline(QScrollArea):
    def __init__(self,parent=None):
        super().__init__()
        self.setWidgetResizable(True)
        self.main = QWidget()
        self.main.setObjectName("timelineWidget")
        self.main.layout = QVBoxLayout()
        self.main.setLayout(self.main.layout)
        self.setWidget(self.main)
        self.setSizePolicy(QSizePolicy.Policy.Minimum,QSizePolicy.Policy.Minimum)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

    def update(self,ts):
        clearLayout(self.main.layout)
        timestamps = GetHuntTimestamps(ts)
        width = -1
        titleLabel = QLabel()
        titleLabel.setStyleSheet("QLabel{font-size:16px;}")
        self.main.layout.addWidget(titleLabel)
        self.main.layout.addWidget(QLabel())
        for e in timestamps:
            timestamp = e['timestamp']
            event = e['event']
            team_num = e['hunter'].split("_")[0]
            hunter_num = e['hunter'].split("_")[1] 
            hunter = GetHunterFromGame(hunter_num,team_num,e['game_id'])
            tsLbl = QLabel(timestamp)
            tsLbl.setStyleSheet("QLabel{font-weight:bold;}")
            eventLbl = QLabel(GetEventText(event,hunter))
            eventLbl.setWordWrap(True)
            lbl = QLabel("%s<br>%s" % (timestamp,GetEventText(event,hunter)))
            lbl.setWordWrap(True)
            self.main.layout.addWidget(tsLbl)
            self.main.layout.addWidget(eventLbl)
            lbl.setSizePolicy(
            QSizePolicy.Policy.Preferred,
            QSizePolicy.Policy.MinimumExpanding)
            self.main.layout.addWidget(QLabel())
            if lbl.fontMetrics().boundingRect(lbl.text()).width() +32 > width:
                width = lbl.fontMetrics().boundingRect(lbl.text()).width() + 32
        self.main.layout.addStretch()
        if len(timestamps) == 0:
            self.setFixedWidth(0)
        else:
            titleLabel.setText("Duration: %s" % timestamps[-1]['timestamp'])
            self.setFixedWidth(200)

def GetEventText(event,hunter):
    s = None
    if "bounty" in event:
        if event == "bountypickedup":
            s = "%s picked up the bounty." 
        elif event == "bountyextracted":
            s = "%s extracted with a bounty." 
    elif "downed" in event:
        if event == "downedbyteammate":
            s = "%s was downed by your teammate." 
        elif event == "downedbyme":
            s = "%s was downed by you." 
        if event == "downedteammate":
            s = "%s downed your teammate." 
        elif event == "downedme":
            s = "%s downed you." 
    elif "killed" in event:
        if event == "killedbyteammate":
            s = "%s was killed by your teammate." 
        elif event == "killedbyme":
            s = "%s was killed by you." 
        if event == "killedteammate":
            s = "%s killed your teammate." 
        elif event == "killedme":
            s = "%s killed you." 
    if s == None:
        return event
    return s % hunter