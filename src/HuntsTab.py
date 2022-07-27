from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QSizePolicy, QComboBox, QScrollArea, QWidget, QTabWidget, QLabel, QMainWindow, QPushButton
from PyQt5.QtCore import QSettings, Qt, QEvent, QSize
from PyQt5 import QtGui
from Connection import MmrToStars, unix_to_datetime
from GroupBox import GroupBox
from HunterLabel import HunterLabel

class HuntsTab(GroupBox):
    def __init__(self,parent,layout,title='') -> None:
        super().__init__(layout,title)
        self.parent = parent
        self.popup = None
        self.connection = parent.connection
        self.settings = QSettings('./settings.ini',QSettings.Format.IniFormat)
        self.layout.setSpacing(4)
        #self.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Maximum)
        if self.layout.__class__.__name__ == 'QGridLayout':
            self.initGridLayout()
        elif self.layout.__class__.__name__ == 'QVBoxLayout':
            self.initVBoxLayout()


        #self.layout.setRowStretch(self.layout.rowCount(),1)
        self.setMouseTracking(True)
    
    def initGridLayout(self):
        self.layout.addWidget(self.MatchSelect(),0,0,1,4)
        self.layout.addWidget(QLabel(),1,0,1,4)
        self.huntInfoBox = self.HuntInfoBox()
        self.teamInfoBox = self.TeamInfoBox()
        self.layout.addWidget(self.huntInfoBox,2,0,1,1)
        self.layout.addWidget(self.teamInfoBox,2,1,1,3)
        self.huntInfoScrollArea.setSizePolicy(QSizePolicy.Maximum,QSizePolicy.Expanding)
        self.teamTabs.setSizePolicy(QSizePolicy.MinimumExpanding,QSizePolicy.Expanding)

    def initVBoxLayout(self):
        self.layout.addWidget(self.MatchSelect())
        #self.layout.addWidget(QLabel(),1,0,1,4)
        self.huntInfoBox = self.HuntInfoBox()
        self.teamInfoBox = self.TeamInfoBox()
        self.layout.addWidget(self.huntInfoBox)
        self.layout.addWidget(self.teamInfoBox)

    def MatchSelect(self):
        self.matchSelection = QComboBox()
        self.matchSelection.view().setSpacing(4)
        self.matchSelection.setIconSize(QSize(32,32))
        self.matchSelection.setStyleSheet('QComboBox{padding:8px;}')
        width = 0
        for timestamp in self.connection.GetAllTimestamps():
            line = '\t%s - %s - %d teams - %d kills' % (
                    unix_to_datetime(timestamp),
                    'Quick Play' if self.connection.IsQuickPlay(timestamp) else 'Bounty Hunt',
                    self.connection.getNTeams(timestamp),
                    self.connection.GetMatchKills(timestamp)
                )
            self.matchSelection.addItem(line,timestamp)
            width = max(width,len(line))

        self.matchSelection.activated.connect(self.updateHuntInfo)
        self.matchSelection.activated.connect(self.updateTeamInfo)
        return self.matchSelection
    
    def updateMatchSelect(self):
        self.matchSelection.clear()
        width = 0
        for timestamp in self.connection.GetAllTimestamps():
            dead = not self.connection.Survived(timestamp)
            line = '\t%s - %s - %d teams - %d kills' % (
                    unix_to_datetime(timestamp),
                    'Quick Play' if self.connection.IsQuickPlay(timestamp) else 'Bounty Hunt',
                    self.connection.getNTeams(timestamp),
                    self.connection.GetMatchKills(timestamp)
                )
            width = max(width,len(line))
            self.matchSelection.addItem(
                QtGui.QIcon('./assets/icons/death2.png' if dead else './assets/icons/lived2.png'),
                line,
                timestamp
            )
        self.matchSelection.adjustSize()


    def update(self):
        self.updateMatchSelect()
        self.updateHuntInfo()
        self.updateTeamInfo()

    def updateHuntInfo(self):
        game = self.connection.GetMatchData(self.matchSelection.currentData())
        if len(game) == 0:  return
        entries = self.connection.GetMatchEntries(self.matchSelection.currentData())
        if len(entries) == 0:  return
        quickplay = game['MissionBagIsQuickPlay']
        rifts_closed = 0
        assists = 0
        hunterkills = 0
        monsterkills = 0
        clues_found = {
            'assassin':0,
            'spider':0,
            'butcher':0,
            'scrapbeak':0
        }
        hunters_killed = {
            0:0,
            1:0,
            2:0,
            3:0,
            4:0,
            5:0,
            6:0
        }
        monsters_killed = {}
        for entry in entries:
            if entry['entry_num'] < game['MissionBagNumEntries']:
                cat = entry['category']
                if 'wellsprings_found' in cat:
                    rifts_closed += 1
                if 'clues_found' in cat:
                    boss = entry['descriptorName'].split(' ')[1]
                    clues_found[boss] += 1
                if 'players_killed' in cat:
                    if 'assist' in cat:
                        assists += entry['amount']
                    elif 'mm rating' in entry['descriptorName']:
                        mm = int(entry['descriptorName'].split(' ')[4])
                        hunters_killed[mm] = entry['amount']
                        hunterkills += entry['amount']
                if 'monsters_killed' in cat:
                    monster = entry['descriptorName'].split(' ')[1]
                    if monster not in monsters_killed.keys():
                        monsters_killed[monster] = 0
                    monsters_killed[monster] += entry['amount']
                    monsterkills += entry['amount']
        self.cluesFound.setText('')
        if rifts_closed > 0:
            self.cluesFound.setText('Closed %d rifts' % rifts_closed)
        text = []
        for boss in clues_found:
            if clues_found[boss] > 0:
                text.append('Found %d of the clues for %s.' % (clues_found[boss],boss.capitalize()))
        self.cluesFound.setText(
            '\n'.join(text)
        )
        
        self.huntersKilled.setText(
            'Hunter kills: %d<br> %s' % (hunterkills, '<br>'.join(["%dx <img src='./assets/icons/_%dstar.png'>" % (hunters_killed[m], m) for m in hunters_killed if hunters_killed[m] > 0]))
        )
        self.killsAndAssists.setText('%d kills, %d assists' % (self.connection.GetMyKills(self.matchSelection.currentData()),assists))

        self.myDeaths.setText('downed %d times' % (self.connection.GetMyDeaths(self.matchSelection.currentData())))
        
        if monsterkills > 0:
            self.monstersKilled.setText(
                'Monster kills: %d<br> %s' % (monsterkills, '<br>'.join(["%d %s" % (monsters_killed[m], m) for m in monsters_killed if monsters_killed[m] > 0]))
            )
        else:
            self.monstersKilled.setText('')


        self.mission.setText('%s' % ('Quick Play' if quickplay else 'Bounty Hunt'))
        if quickplay:
            self.bounties.setText('')
        else:
            self.bounties.setText('%s' % (', '.join(self.GetMatchBounties(game))))
        self.teams.setText('Teams: %d' % (game['MissionBagNumTeams']))
        if game['EventPoints'] != None:
            self.eventPoints.setText('Serpent Moon points: %s' % game['EventPoints'])
        else:
            self.eventPoints.setText('')

    def HuntInfoBox(self):
        self.huntInfoScrollArea = QScrollArea()
        self.huntInfoScrollArea.setWidgetResizable(True)
        self.huntInfoScrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.huntInfo = QWidget()
        self.huntInfo.setObjectName('HuntInfo')
        self.huntInfo.setStyleSheet('QLabel{padding-right:32px;}')
        self.huntInfo.layout = QVBoxLayout()
        self.huntInfo.setLayout(self.huntInfo.layout)

        self.mission = QLabel('Bounty Hunt')
        self.huntInfo.layout.addWidget(self.mission)
        self.bounties = QLabel('Assassin and Scrapbeak')
        self.huntInfo.layout.addWidget(self.bounties)
        self.teams = QLabel('Teams: 12')
        self.eventPoints = QLabel('Serpent Moon Points: 36')
        self.eventPoints.setObjectName('SerpentMoon')
        self.huntInfo.layout.addWidget(self.teams)
        self.huntInfo.layout.addWidget(self.eventPoints)
        self.huntInfo.layout.addWidget(QLabel())

        self.cluesFound = QLabel('Found 3 of the clues for butcher\t')
        self.huntInfo.layout.addWidget(self.cluesFound)
        self.huntInfo.layout.addWidget(QLabel())
        self.huntersKilled = QLabel('Team killed 0 hunters')
        self.huntInfo.layout.addWidget(self.huntersKilled)
        self.huntInfo.layout.addWidget(QLabel())
        self.killsAndAssists = QLabel('0 assists, 0 kills.')
        self.huntInfo.layout.addWidget(self.killsAndAssists)
        self.myDeaths = QLabel('You were killed 0 times.')
        self.huntInfo.layout.addWidget(self.myDeaths)
        self.huntInfo.layout.addWidget(QLabel())
        self.monstersKilled = QLabel('Team killed 0 monsters')
        self.huntInfo.layout.addWidget(self.monstersKilled)


        self.huntInfo.layout.addStretch()

        self.huntInfoScrollArea.setWidget(self.huntInfo)

        self.cluesFound.setWordWrap(True)
        return self.huntInfoScrollArea

    def updateTeamInfo(self):
        self.teamTabs.clear()
        teams = self.connection.GetMatchTeams(self.matchSelection.currentData())
        isquickplay = self.connection.IsQuickPlay(self.matchSelection.currentData())
        allhunters = self.connection.GetAllHunterData(self.matchSelection.currentData())
        for team in teams:
            teamInfoScrollArea = QScrollArea()
            teamInfoScrollArea.setWidgetResizable(True)
            #self.teamInfoScrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
            teamInfo = QWidget()
            teamInfoScrollArea.setWidget(teamInfo)
            teamInfo.layout = QVBoxLayout()
            teamInfo.setLayout(teamInfo.layout)
            teamSubInfo = QWidget()
            teamSubInfo.layout = QVBoxLayout()
            teamSubInfo.setLayout(teamSubInfo.layout)
            teammmr = QLabel('Team MMR: %d' % team['mmr'])
            teamSubInfo.layout.addWidget(teammmr)
            teamInfo.layout.addWidget(teamSubInfo)

            huntersInfo = QWidget()
            huntersInfo.layout = QHBoxLayout()
            huntersInfo.layout.setSpacing(32)
            huntersInfo.setLayout(huntersInfo.layout)
            hunters = [x for x in allhunters if x['team_num'] == team['team_num']]
            if not isquickplay:
                self.teamTabs.addTab(teamInfoScrollArea,'Team %d (%d hunters)' % (team['team_num'], team['numplayers']))
            else:
                hunter = hunters[0]
                self.teamTabs.addTab(teamInfoScrollArea,'%s' % hunter['blood_line_name'])
            
            got_bounty = False
            extracted_bounty = False
            had_wellspring = False
            team_extract = False

            for i in range(len(hunters)):
                hunter = hunters[i]
                hunterInfo = QWidget()
                hunterInfo.layout = QVBoxLayout()
                hunterInfo.setLayout(hunterInfo.layout)
                name = HunterLabel(hunter['blood_line_name'])
                name.setObjectName('name')
                mmr = QLabel('%d' % hunter['mmr'])
                stars = QLabel()
                profileid = hunter['profileid']
                n_games = self.connection.NumTimesSeen(profileid)
                stars.setPixmap(QtGui.QPixmap('./assets/icons/_%dstar.png' % MmrToStars(hunter['mmr'])))
                hunterInfo.layout.addWidget(name)
                hunterInfo.layout.addWidget(mmr)
                hunterInfo.layout.addWidget(stars)

                if hunter['downedme'] or \
                hunter['downedbyme'] or \
                hunter['downedteammate'] or \
                hunter['downedbyteammate'] or \
                hunter['killedme'] or \
                hunter['killedbyme'] or \
                hunter['killedteammate'] or \
                hunter['killedbyteammate']:
                    killinfo = QPushButton('kills')
                    #killinfo.underMouse()
                    killinfo.mousePressEvent = lambda e : self.ShowWindow(hunter,e)
                    killinfo.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
                    killinfo.setObjectName('link')
                    hunterInfo.layout.addWidget(killinfo)
                    killinfo.installEventFilter(self)
                    #killinfo.mousePressEvent = partial(self.ShowWindow,hunter)
                    #hunterInfo.installEventFilter(self)
                if hunter['bountypickedup'] or hunter['bountyextracted']:
                    bountyinfo = QPushButton('bounties')
                    bountyinfo.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed)
                    bountyinfo.setObjectName('link')
                    hunterInfo.layout.addWidget(bountyinfo)
                    bountyinfo.installEventFilter(self)
                if hunter['bountypickedup']:
                    got_bounty = True
                    if hunter['bountyextracted']:
                        extracted_bounty = True
                if hunter['hadWellspring']:
                    had_wellspring = True
                    wellspringinfo = QPushButton('wellspring')
                    wellspringinfo.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed)
                    wellspringinfo.setObjectName('link')
                    hunterInfo.layout.addWidget(wellspringinfo)
                    wellspringinfo.installEventFilter(self)
                if hunter['teamextraction']:
                    team_extract = True
                if n_games > 1:
                    gamesLabel = QLabel("%d games" % n_games)
                    gamesLabel.setFont(QtGui.QFont('Courier New',10))
                    hunterInfo.layout.addWidget(gamesLabel)
                hunterInfo.layout.addStretch()
                huntersInfo.layout.addWidget(hunterInfo)
                #hunterInfo.layout.addStretch()
            huntersInfo.setSizePolicy(QSizePolicy.MinimumExpanding,QSizePolicy.MinimumExpanding)
            huntersInfo.layout.addStretch()
            teamInfo.layout.addWidget(huntersInfo)
            teamInfo.layout.addStretch()
            if got_bounty:
                if extracted_bounty:
                    teamSubInfo.layout.addWidget(QLabel('They extracted with the bounty.'))
                else:
                    teamSubInfo.layout.addWidget(QLabel('They had the bounty.'))
            if team_extract and not extracted_bounty:
                teamSubInfo.layout.addWidget(QLabel('They extracted.'))
            teamInfo.layout.addStretch()

            #teamInfo.layout.setColumnStretch(teamInfo.layout.columnCount(),1)
            teamInfoScrollArea.setSizePolicy(QSizePolicy.MinimumExpanding,QSizePolicy.MinimumExpanding)
        self.teamTabs.setSizePolicy(QSizePolicy.MinimumExpanding,QSizePolicy.MinimumExpanding)
            
    def eventFilter(self, obj, e) -> bool:
        child = obj.parent().findChild(QWidget,'name')
        dataType = obj.text()
        if e.type() == QEvent.Enter:
            if child:
                name = child.text()
                hunter = self.connection.GetHunterData(name,self.matchSelection.currentData())
                self.ShowWindow(hunter,dataType)
                self.popup.move(e.globalX()+self.popup.size().width()/4,e.globalY()-self.popup.size().height()/4)
                self.setFocus()
                #print(name)
        elif e.type() == QEvent.Leave:
            self.popup = None
        return super().eventFilter(obj, e)

    def ShowWindow(self,hunter,data):
        self.popup = QMainWindow()
        self.popup.setStyleSheet('QWidget{border:1px solid red;}QLabel{border:0px;}')
        self.popup.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        #self.popup.setWindowFlags(Qt.FramelessWindowHint | Qt.Popup | Qt.WindowStaysOnTopHint)
        #self.popup.move(self.mouseXY.x() + 100, self.mouseXY.y() + 100)
        info = QWidget()
        self.popup.setCentralWidget(info)
        info.layout = QVBoxLayout()
        info.setLayout(info.layout)

        info.layout.addWidget(QLabel(hunter['blood_line_name']))
        info.layout.addWidget(QLabel())
        if data == 'kills':
            if hunter['downedme']:
                info.layout.addWidget(QLabel('They downed you %d times.' % hunter['downedme']))
            if hunter['downedbyme']:
                info.layout.addWidget(QLabel('you downed them %d times.' % hunter['downedbyme']))
            if hunter['downedteammate']:
                info.layout.addWidget(QLabel('They downed your teammate %d times.' % hunter['downedteammate']))
            if hunter['downedbyteammate']:
                info.layout.addWidget(QLabel('your teammate downed them %d times.' % hunter['downedbyteammate']))
            if hunter['killedme']:
                info.layout.addWidget(QLabel('They killed you.'))
            if hunter['killedbyme']:
                info.layout.addWidget(QLabel('you killed them.'))
            if hunter['killedteammate']:
                info.layout.addWidget(QLabel('They killed your teammate.'))
            if hunter['killedbyteammate']:
                info.layout.addWidget(QLabel('your teammate killed them.'))
        elif data == 'bounties':
            if hunter['bountypickedup']:
                if hunter['bountyextracted']:
                    info.layout.addWidget(QLabel('they extracted with the bounty.'))
                else:
                    info.layout.addWidget(QLabel('they picked up the bounty.'))
        elif data == 'wellspring':
            if hunter['hadWellspring']:
                info.layout.addWidget(QLabel('they activated the wellspring.'))
        info.layout.addStretch()
        self.popup.show()
        self.setFocus()

    def TeamInfoBox(self):
        self.teamTabs = QTabWidget()
        teamInfoScrollArea = QScrollArea()
        teamInfoScrollArea.setWidgetResizable(True)
        #self.teamInfoScrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        teamInfo = QWidget()
        teamInfoScrollArea.setWidget(teamInfo)
        teamInfo.layout = QVBoxLayout()
        teamInfo.setLayout(teamInfo.layout)
        teamSubInfo = QWidget()
        teamSubInfo.layout = QVBoxLayout()
        teamSubInfo.setLayout(teamSubInfo.layout)
        teammmr = QLabel('Team MMR: 0000')
        teamSubInfo.layout.addWidget(teammmr)
        teamInfo.layout.addWidget(teamSubInfo)

        huntersInfo = QWidget()
        huntersInfo.layout = QHBoxLayout()
        huntersInfo.setLayout(huntersInfo.layout)

        for i in range(3):
            hunterInfo = QWidget()
            hunterInfo.layout = QVBoxLayout()
            hunterInfo.setLayout(hunterInfo.layout)
            name = HunterLabel('Hunter %d' % i)
            name.setObjectName('name')
            mmr = QLabel('0000')
            stars = QLabel()
            stars.setPixmap(QtGui.QPixmap('./assets/icons/_4star.png'))
            hunterInfo.layout.addWidget(name)
            hunterInfo.layout.addWidget(mmr)
            hunterInfo.layout.addWidget(stars)

            killinfo = QPushButton('kills')
            killinfo.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
            killinfo.setObjectName('link')
            hunterInfo.layout.addWidget(killinfo)
            bountyinfo = QPushButton('bounties')
            bountyinfo.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed)
            bountyinfo.setObjectName('link')
            hunterInfo.layout.addWidget(bountyinfo)
            gamesLabel = QLabel("0 games") 
            gamesLabel.setFont(QtGui.QFont('Courier New',10))
            hunterInfo.layout.addWidget(gamesLabel)
            hunterInfo.layout.addStretch()
            huntersInfo.layout.addWidget(hunterInfo)
            #hunterInfo.layout.addStretch()
        huntersInfo.setSizePolicy(QSizePolicy.MinimumExpanding,QSizePolicy.MinimumExpanding)
        huntersInfo.layout.addStretch()
        teamInfo.layout.addWidget(huntersInfo)
        teamInfo.layout.addStretch()
        teamSubInfo.layout.addWidget(QLabel('They extracted with the bounty.'))
        teamInfo.layout.addStretch()

        #teamInfo.layout.setColumnStretch(teamInfo.layout.columnCount(),1)
        teamInfoScrollArea.setSizePolicy(QSizePolicy.MinimumExpanding,QSizePolicy.MinimumExpanding)
        self.teamTabs.setSizePolicy(QSizePolicy.MinimumExpanding,QSizePolicy.MinimumExpanding)
        self.teamTabs.addTab(teamInfoScrollArea,'Team 0')
        return self.teamTabs
            
        teamInfoScrollArea = QScrollArea()
        teamInfoScrollArea.setWidgetResizable(True)
        #self.teamInfoScrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        teamInfo = QWidget()
        teamInfoScrollArea.setWidget(teamInfo)
        teamInfo.layout = QHBoxLayout()
        teamInfo.setLayout(teamInfo.layout)
        teamInfo.layout.addWidget(QLabel('Team MMR: 0'))
        teamInfo.layout.addWidget(QLabel())
        for i in range(3):
            teamInfo.layout.addWidget(QLabel('Hunter %d' % i))
            teamInfo.layout.addWidget(QLabel('0'))
            s = QLabel()
            s.setPixmap(QtGui.QPixmap('./assets/icons/_6star.png'))
            teamInfo.layout.addWidget(s)
            killinfo = QPushButton('kill info')
            killinfo.setObjectName('link')
            teamInfo.layout.addWidget(killinfo)
            teamInfo.layout.addWidget(QLabel())
        teamInfo.layout.addStretch()
        #self.teamTabs.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Expanding)
        #teamInfoScrollArea.setSizePolicy(QSizePolicy.MinimumExpanding,QSizePolicy.MinimumExpanding)
        self.teamTabs.addTab(teamInfoScrollArea,'Team N')
        return self.teamTabs

    def GetMatchBounties(self,game):
        bounties = []
        if game['MissionBagBoss_0']: bounties.append('Butcher')
        if game['MissionBagBoss_1']: bounties.append('Spider')
        if game['MissionBagBoss_2']: bounties.append('Assassin')
        if game['MissionBagBoss_3']: bounties.append('Scrapbeak')
        return bounties