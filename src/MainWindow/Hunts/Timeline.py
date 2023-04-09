from PyQt6.QtWidgets import QWidget,QGroupBox, QLabel, QVBoxLayout, QScrollArea, QSizePolicy, QApplication
from PyQt6.QtCore import Qt
from DbHandler import GetHuntTimestamps, GetHunterFromGame
from resources import clearLayout

class Timeline(QScrollArea):
    def __init__(self,parent=None):
        super().__init__()
        self.setWidgetResizable(True)
        self.main = QWidget()
        self.main.layout = QVBoxLayout()
        self.main.setLayout(self.main.layout)
        self.main.setObjectName("timelineWidget")
        self.setStyleSheet("QScrollArea{padding 4px 24px;}")

        self.setWidget(self.main)

        self.setSizePolicy(QSizePolicy.Policy.Minimum,QSizePolicy.Policy.Expanding)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

    def update(self,ts):
        clearLayout(self.main.layout)
        self.timestamps = GetHuntTimestamps(ts)
        width = -1
        titleLabel = QLabel("Timeline")
        subtitleLabel = QLabel()
        titleLabel.setStyleSheet("QLabel{font-size:16px;color:#cccc67;}")
        self.main.layout.addWidget(titleLabel)
        self.main.layout.addWidget(subtitleLabel)
        self.main.layout.addWidget(QLabel())
        for e in self.timestamps:
            eventWidget = QWidget()
            eventWidget.setObjectName("EventWidget")
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
            eventLbl.setWordWrap(True)
            lbl = QLabel("%s<br>%s" % (timestamp,GetEventText(event,hunter)))
            lbl.setWordWrap(True)
            eventWidget.layout.addWidget(tsLbl)
            eventWidget.layout.addWidget(eventLbl)
            lbl.setSizePolicy(
            QSizePolicy.Policy.Preferred,
            QSizePolicy.Policy.MinimumExpanding)
            #eventWidget.layout.addWidget(QLabel())
            if lbl.fontMetrics().boundingRect(lbl.text()).width() +32 > width:
                width = lbl.fontMetrics().boundingRect(lbl.text()).width() + 32
            if "byme" in event or "byteammate" in event:
                eventWidget.setStyleSheet("#EventWidget{background:#22008800;}")
            elif "me" in event or "teammate" in event:
                eventWidget.setStyleSheet("#EventWidget{background:#22880000;}")
            else:
                eventWidget.setStyleSheet("#EventWidget{background:#22000088;}")

            self.main.layout.addWidget(eventWidget)

        self.main.layout.addStretch()
        if len(self.timestamps) > 0:
            subtitleLabel.setText("Duration: %s" % self.timestamps[-1]['timestamp'])
        QApplication.processEvents()
        self.setMinimumWidth(self.main.layout.sizeHint().width())

def GetEventText(event,hunter):
    s = None
    if "bounty" in event:
        if event == "bountypickedup":
            s = "%s picked up the bounty." 
        elif event == "bountyextracted":
            s = "%s extracted with a bounty." 
    elif "downed" in event:
        if event == "downedbyteammate":
            s = "Your teammate downed %s." 
        elif event == "downedbyme":
            s = "You downed %s." 
        if event == "downedteammate":
            s = "%s downed your teammate." 
        elif event == "downedme":
            s = "%s downed you." 
    elif "killed" in event:
        if event == "killedbyteammate":
            s = "Your teammate killed %s." 
        elif event == "killedbyme":
            s = "You killed %s." 
        if event == "killedteammate":
            s = "%s killed your teammate." 
        elif event == "killedme":
            s = "%s killed you." 
    if s == None:
        return event
    return s % hunter