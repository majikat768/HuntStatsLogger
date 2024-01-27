from PyQt6.QtCore import QEvent, QObject, QPropertyAnimation, QSize
from PyQt6.QtGui import QMouseEvent, QResizeEvent
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QSizePolicy, QGroupBox, QPushButton
from PyQt6 import QtCore, QtGui
from DbHandler import get_team_data, get_hunters_data, get_hunter_encounters, get_all_names
from resources import tab, stars_pixmap, mmr_to_stars, get_icon, settings, resource_path
from Widgets.Label import Label
from Widgets.ToggleSwitch import AnimatedToggle

class TeamsWidget(QGroupBox):
    def __init__(self, game_id, parent: QWidget | None = None):
        super().__init__(parent)
        self.game_id = game_id
        self.data = {}
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.layout.setSpacing(16)

        self.setTitle("Teams")

        self.setSizePolicy(QSizePolicy.Policy.Expanding,QSizePolicy.Policy.Minimum)
        self.layout.setContentsMargins(4,6,4,4)
        self.teamsWidgets = []

    def init(self):
        if(len(self.data) == 0):
            self.data['teams'] = get_team_data(self.game_id)
            self.data['hunters'] = sorted(get_hunters_data(self.game_id),key=lambda x : x['team_num'])

            hunter_num = 0
            own_team_inserted = False
            avgMmr = 0
            for team in self.data['teams']:
                carried_bounty = False
                killed_us = False
                killed_them = False
                team_num = team['team_num']
                team['hunters'] = []
                for i in range(hunter_num,hunter_num+team['numplayers']):
                    hunter = self.data['hunters'][i]
                    if(hunter['bountypickedup'] > 0):
                        carried_bounty = True
                    if(hunter['killedbyme'] > 0 or hunter['killedbyteammate'] > 0):
                        killed_them = True
                    if(hunter['killedme'] > 0 or hunter['killedteammate'] > 0):
                        killed_us = True
                    team['hunters'].append(hunter)
                team['hunters'] = sorted(team['hunters'],key=lambda x : x['mmr']*-1)
                hunter_num = i+1
                if(team['ownteam'] == 'true'):
                    tmW = TeamWidget(team,carried_bounty,killed_us,killed_them,parent=self)
                    self.teamsWidgets.append(tmW)
                    self.layout.insertWidget(0,tmW)
                    own_team_inserted = True
                elif carried_bounty or killed_them or killed_us:
                    tmW = TeamWidget(team,carried_bounty,killed_us,killed_them,parent=self)
                    self.layout.insertWidget(1 if own_team_inserted else 0,tmW) 
                    self.teamsWidgets.append(tmW)
                else:
                    tmW = TeamWidget(team,carried_bounty,killed_us,killed_them,parent=self)
                    self.layout.addWidget(tmW)
                    self.teamsWidgets.append(tmW)
                avgMmr += team['mmr']
            avgMmr = avgMmr / len(self.data['teams']) if len(self.data['teams']) > 0 else 0
            self.layout.addStretch()
            self.buttons = self.init_buttons(avgMmr)
            self.buttons.move(self.width()-self.buttons.sizeHint().width(),0)
            #self.layout.insertWidget(0,self.buttons)

    def init_buttons(self,avgMmr):
        buttons = QWidget(parent=self)
        buttons.setAttribute(QtCore.Qt.WidgetAttribute.WA_StyledBackground)      
        buttons.setStyleSheet("QWidget{background:transparent;}QPushButton{background:#111;padding:2px 8px;}")
        buttons.layout = QHBoxLayout()
        buttons.setLayout(buttons.layout)
        buttons.layout.setContentsMargins(0,0,0,0)
        #buttons.layout.addWidget(QLabel("Team Avg: %d" % avgMmr),0,0,1,2)
        exBtn = QPushButton("Expand All")
        exBtn.clicked.connect(lambda : self.toggleAllWidgets(True))
        colBtn = QPushButton("Collapse All")
        colBtn.clicked.connect(lambda : self.toggleAllWidgets(False))
        buttons.layout.addWidget(exBtn)
        buttons.layout.addWidget(colBtn)
        buttons.setFixedWidth(buttons.sizeHint().width())
        return buttons

    def toggleAllWidgets(self,state):
        for w in self.teamsWidgets:
            w.setBodyState(state)

    def resizeEvent(self, a0: QResizeEvent) -> None:
        self.buttons.move(self.width()-self.buttons.sizeHint().width(),int(-self.buttons.sizeHint().height()/8))
        return super().resizeEvent(a0)

expandedStyle = "QWidget#TeamHeader{background:transparent;border:none;}\
                    QWidget#TeamHeader::hover {background:#888888;}"
collapsedStyle = "QWidget#TeamHeader{background:#111111;border:1px solid #888;}\
                    QWidget#TeamHeader::hover {background:#888888;}"
class TeamWidget(QWidget):
    def __init__(self, team, carried_bounty, killed_us, killed_them, parent: QWidget | None = None):
        super().__init__(parent)
        self.team = team
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_StyledBackground)      
        self.setObjectName("TeamWidget")
        self.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Fixed
        )
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.layout.setContentsMargins(0,0,0,0)
        self.layout.setSpacing(0)
        carried_bounty = False
        killed_them = False
        killed_us = False

        self.header = self.initHeader(team)
        self.layout.addWidget(self.header)
        self.body = self.initBody(team)
        self.layout.addWidget(self.body)
        self.body.setVisible(True)

        self.collapsed = False 
        self.header.setStyleSheet(expandedStyle)
        self.layout.addStretch()

    def initHeader(self,team):
        header = QWidget()
        header.setObjectName("TeamHeader")
        header.layout = QHBoxLayout()
        header.setLayout(header.layout)
        header.layout.setContentsMargins(8,4,8,4)
        header.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Fixed
        )

        header.layout.addWidget(QLabel(
            ("Trio" if len(team['hunters']) == 3 else "Duo" if len(team['hunters']) == 2 else "Solo")
        ),stretch=1)
        stars = Label()
        stars.setPixmap(stars_pixmap(mmr_to_stars(team['mmr']),h=16))
        stars.setToolTip(str(team['mmr']))
        header.layout.addWidget(stars,stretch=1)
        header.layout.addWidget(QLabel(str(team['mmr'])),stretch=1)
        header.layout.addWidget(QLabel(),stretch=1)
        header.layout.addWidget(QLabel(
            ((" Invite" if team['isinvite'] == 'true' else " Randoms") if len(team['hunters']) > 1 else "")
        ),stretch=1)
        header.installEventFilter(self)
        header.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        return header

    def initBody(self,team):
        body = QWidget()
        #body.setVisible(False)
        body.layout = QGridLayout()
        body.setLayout(body.layout)
        body.layout.setSpacing(0)
        body.layout.setContentsMargins(0,0,0,0)
        body.setBaseSize(body.sizeHint())
        body.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Fixed
        )
        body.setObjectName("HuntersWidget")

        body.anim = QPropertyAnimation(body,b'size')
        body.anim.setDuration(250)
        body.installEventFilter(self)


        for i in range(len(team['hunters'])):
            hunter = team['hunters'][i]
            hunterLabel = Label((hunter['blood_line_name']))
            #hunterLabel.setWordWrap(True)
            body.layout.addWidget(hunterLabel,i,0,1,1)
            stars = Label()
            stars.setPixmap(stars_pixmap(mmr_to_stars(hunter['mmr']),h=12))
            stars.setToolTip(hunter['mmr'])
            body.layout.addWidget(stars,i,2,1,1)
            body.layout.addWidget(QLabel(str(hunter['mmr'])),i,3,1,1)
            encounters = get_hunter_encounters(hunter['profileid'])
            encounters = encounters[0][0] if len(encounters) > 0 else 0
            encLabel = Label(
                ("Seen %dx" % encounters if encounters > 1 and hunter['blood_line_name'] != settings.value("steam_name") else "")
            )
            if(encounters > 1):
                names = get_all_names(hunter['profileid'])
                if(len(names) > 1):
                    print(names)
                    encLabel.setToolTip("Other Names:\n%s" % ('\n'.join(nt[0] for nt in names)))
            body.layout.addWidget(encLabel,i,5,1,1)
            #body.layout.setAlignment(encLabel,QtCore.Qt.AlignmentFlag.AlignRight)
            icons = []
            if hunter['bountypickedup'] > 0:
                tt = '%s carried the bounty.' % hunter['blood_line_name']
                if hunter['bountyextracted'] > 0:
                    tt += '\n%s extracted the bounty.' % hunter['blood_line_name']
                icons.append({
                    'path':resource_path("assets/icons/teams icons/bounty.png"),
                    'tooltip':tt
                    })
            if hunter['downedbyme'] > 0 or hunter['killedbyme'] > 0:
                tt = []
                if hunter['downedbyme'] > 0:
                    tt.append("You downed %s %d times." % (hunter['blood_line_name'],hunter['downedbyme']))
                if hunter['killedbyme'] > 0:
                    tt.append("You killed %s." % (hunter['blood_line_name']))
                icons.append({
                    'path':resource_path("assets/icons/teams icons/killedbyme.png"),
                    'tooltip':'\n'.join(tt)})
                pass
            if hunter['downedbyteammate'] > 0 or hunter['killedbyteammate'] > 0:
                tt = []
                if hunter['downedbyteammate'] > 0:
                    tt.append("Your teammate downed %s %d times." % (hunter['blood_line_name'],hunter['downedbyteammate']))
                if hunter['killedbyteammate'] > 0:
                    tt.append("Your teammate killed %s." % (hunter['blood_line_name']))
                icons.append({
                    'path':resource_path("assets/icons/teams icons/killedbyteammate.png"),
                    'tooltip':'\n'.join(tt)})
                pass
            if hunter['downedme'] > 0 or hunter['killedme'] > 0:
                tt = []
                if hunter['downedme'] > 0:
                    tt.append("%s downed you %d times." % (hunter['blood_line_name'],hunter['downedme']))
                if hunter['killedme'] > 0:
                    tt.append("%s killed you." % (hunter['blood_line_name']))
                icons.append({
                    'path':resource_path("assets/icons/teams icons/killedme.png"),
                    'tooltip':'\n'.join(tt)})
                pass
            if hunter['downedteammate'] > 0 or hunter['killedteammate'] > 0:
                tt = []
                if hunter['downedteammate'] > 0:
                    tt.append("%s downed your teammate %d times." % (hunter['blood_line_name'],hunter['downedteammate']))
                if hunter['killedteammate'] > 0:
                    tt.append("%s killed your teammate." % (hunter['blood_line_name']))
                icons.append({
                    'path':resource_path("assets/icons/teams icons/killedteammate.png"),
                    'tooltip':'\n'.join(tt)})
            iconsWidget = getIconWidget(icons)
            body.layout.addWidget(iconsWidget,i,4,1,1)
 
        body.setMinimumWidth(body.sizeHint().width())
        return body


    def toggleBody(self):
        if(self.collapsed):
            self.body.setVisible(True)
            self.collapsed = False
            self.header.setStyleSheet(expandedStyle)
            #new_size = QSize(self.header.size().width(),self.body.sizeHint().height())
        else:
            self.body.setVisible(False)
            self.collapsed = True
            self.header.setStyleSheet(collapsedStyle)

            #new_size = QSize(self.header.size().width(),0)
        #self.body.anim.setEndValue(new_size)
        #self.body.anim.start()
    def setBodyState(self,state):
        self.body.setVisible(state)
        self.collapsed = not state
        if(state):
            self.header.setStyleSheet(expandedStyle)
        else:
            self.header.setStyleSheet(collapsedStyle)

    def eventFilter(self, a0: QObject, a1: QEvent) -> bool:
        try:
            if a0 == self.header and a1.type() == QEvent.Type.MouseButtonPress:
                self.toggleBody()
            elif self.body.isVisible() and a0 == self.body and a1.type() == QEvent.Type.Resize:
                pass
        except:
            pass
        return super().eventFilter(a0, a1)

def getIconWidget(icons):
    icons_widget = QWidget()
    icons_widget.layout = QHBoxLayout()
    icons_widget.setLayout(icons_widget.layout)
    icons_widget.layout.setSpacing(2)
    icons_widget.layout.setContentsMargins(0,0,0,0)
    icons_widget.setObjectName("TeamsIcons")
    icons_widget.layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft)

    for i in range(len(icons)):
        icon = icons[i]
        w = Label()
        w.setSizePolicy(QSizePolicy.Policy.Fixed,QSizePolicy.Policy.Fixed)
        w.setPixmap(QtGui.QPixmap(icon['path']).scaled(32,32))
        w.setToolTip(icon['tooltip'])
        w.setObjectName("TeamIcon")
        icons_widget.layout.addWidget(w)
    if len(icons) == 0:
        w = Label()
        w.setSizePolicy(QSizePolicy.Policy.Fixed,QSizePolicy.Policy.Fixed)
        w.setPixmap(QtGui.QPixmap(resource_path("assets/icons/blank.png")).scaled(32,32))
        icons_widget.layout.addWidget(w)
    return icons_widget

def trimText(text):
    if len(text) > 16:
        return text[:14] + '...'
    return text