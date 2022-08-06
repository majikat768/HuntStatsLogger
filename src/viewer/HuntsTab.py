from cmath import polar
from PyQt6.QtWidgets import QTabWidget,QGroupBox,QVBoxLayout,QWidget,QGridLayout,QComboBox,QLabel,QScrollArea,QHBoxLayout,QPushButton,QMainWindow
from PyQt6.QtCore import Qt,QSize, QEvent
from PyQt6.QtGui import QIcon,QPixmap
from util.HunterLabel import HunterLabel
from resources import *
from util.TextArea import TextArea
from viewer import DbHandler 

class HuntsTab(QGroupBox):
    def __init__(self,parent):
        super().__init__(parent)
        self.layout = QGridLayout()
        self.setLayout(self.layout)

        self.matchSelect = QComboBox()
        self.matchSelect.view().setSpacing(4)
        self.matchSelect.setIconSize(QSize(24,24))
        self.matchSelect.setStyleSheet('QComboBox{padding:8px;}')
        
        self.matchSelect.setSizePolicy(QSizePolicy.Policy.MinimumExpanding,QSizePolicy.Policy.Fixed)
        self.matchSelect.activated.connect(self.updateHuntDetails) 
        self.matchSelect.activated.connect(self.updateTeamDetails) 
        self.huntDetails = self.HuntDetails()
        self.teamTabWidget = self.TeamDetails()
        self.teamTabWidget.setSizePolicy(QSizePolicy.Policy.Expanding,QSizePolicy.Policy.MinimumExpanding)

        self.layout.addWidget(self.matchSelect,0,0,1,2)
        self.layout.addWidget(self.huntDetails,1,0,1,1)
        self.layout.addWidget(self.teamTabWidget,1,1,1,1)


    def update(self):
        self.updateMatchSelection()
        self.updateHuntDetails()
        self.updateTeamDetails()

    def HuntDetails(self):
        huntDetails = TextArea()
        huntScroll = QScrollArea()
        huntScroll.setWidgetResizable(True)

        huntDetails.setObjectName("huntDetails")

        details = {}
        huntDetails.addLine('gameType',"No hunts logged.")
        huntDetails.addLine('bosses')
        huntDetails.addLine('teams')
        huntDetails.addSpacerItem(16)
        huntDetails.addLine('eventPts')
        huntDetails.get('eventPts').setObjectName("EventPointsLabel")
        huntDetails.addSpacerItem(16)
        huntDetails.addLine('clues')
        huntDetails.addSpacerItem(16)
        huntDetails.addLine('teamkills')
        huntDetails.addSpacerItem(16)
        huntDetails.addLine('mykills')
        huntDetails.addLine('mydeaths')
        huntDetails.addSpacerItem(16)
        huntDetails.addLine('monsterkills')

        huntDetails.addStretch()
        huntScroll.setWidget(huntDetails)
        huntScroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        huntDetails.setSizePolicy(QSizePolicy.Policy.Fixed,QSizePolicy.Policy.Fixed)

        for k in huntDetails.lines:
            huntDetails.lines[k].setWordWrap(True)
        return huntScroll

    def TeamDetails(self):
        self.teamTabs = []
        self.hunterAreas = {}
        for i in range(12):
            teamScrollArea = QScrollArea()
            teamScrollArea.setWidgetResizable(True)

            teamWidget = QWidget()
            teamWidget.layout = QGridLayout()
            teamWidget.setLayout(teamWidget.layout)

            self.hunterAreas[i] = []

            teamInfo = TextArea()
            teamInfo.setObjectName("TEAMINFO")
            teamInfo.addLine('mmr')
            teamInfo.addLine('bounty')
            for j in range(3):
                hunterInfo = TextArea()
                hunterInfo.addLabel('name',HunterLabel())
                hunterInfo.get('name').setObjectName("blood_line_name")
                stars = QLabel()
                stars.setPixmap(QPixmap(os.path.join(resource_path('assets/icons/'),'_6star.png')))
                hunterInfo.addLabel('stars',stars)
                hunterInfo.addLine('mmr')
                killinfo = QLabel("kills")
                killinfo.hide()
                killinfo.setSizePolicy(QSizePolicy.Policy.Fixed,QSizePolicy.Policy.Fixed)
                killinfo.setObjectName("link")
                killinfo.installEventFilter(self)
                bountyinfo = QLabel("bounties")
                bountyinfo.hide()
                bountyinfo.setObjectName("link")
                bountyinfo.installEventFilter(self)
                bountyinfo.setSizePolicy(QSizePolicy.Policy.Fixed,QSizePolicy.Policy.Fixed)
                hunterInfo.addLabel('kills',killinfo)
                hunterInfo.addLabel('bounties',bountyinfo)
                hunterInfo.addLine('ngames')
                hunterInfo.setFixedWidth(hunterInfo.sizeHint().width())
                hunterInfo.addStretch()
                self.hunterAreas[i].append(hunterInfo)
                teamWidget.layout.addWidget(hunterInfo,1,j,1,1)

            teamWidget.layout.addWidget(teamInfo,0,0,1,3)
            teamWidget.layout.setRowStretch(teamWidget.layout.rowCount(),1)
            teamWidget.layout.setColumnStretch(teamWidget.layout.columnCount(),1)
            teamScrollArea.setWidget(teamWidget)
            self.teamTabs.append(teamScrollArea)


        teamTabsWidget = QTabWidget()
        for tab in self.teamTabs:
            tab = self.teamTabs[i]
            teamTabsWidget.addTab(tab,"Team %d" % i)
        return teamTabsWidget

    def updateTeamDetails(self):
        if self.matchSelect.count() == 0:
            return
        self.teamTabWidget.clear()

        ts = self.matchSelect.currentData()
        gameData = DbHandler.GetHunt(ts)
        teamsData = DbHandler.GetTeams(ts)
        allHuntersData = DbHandler.GetHunters(ts)
        qp = gameData["MissionBagIsQuickPlay"]

        for i in range(len(teamsData)):
            teamScrollArea = self.teamTabs[i]
            teamWidget = teamScrollArea.widget()
            teamArea = teamWidget.layout.itemAtPosition(0,0).widget()
            hunterAreas = self.hunterAreas[i]

            teamData = teamsData[i]
            teamArea.get('mmr').setText("Team MMR: %d" % teamData['mmr'])

            team_num = teamData["team_num"]
            got_bounty = False
            extracted_bounty = False
            had_wellspring = False
            team_extract = False
            kills = 0

            teamHuntersData = [ x for x in allHuntersData if int(x['team_num']) == int(team_num)]

            huntersInfo = QWidget()
            huntersInfo.layout = QHBoxLayout()
            huntersInfo.setLayout(huntersInfo.layout)

            for j in range(3):
                hunterArea = teamWidget.layout.itemAtPosition(1,j).widget()
                if j < len(teamHuntersData):
                    hunterArea.show()

                    hunterData = teamHuntersData[j]

                    hunterArea.get('name').setText(hunterData['blood_line_name'])
                    if hunterData['blood_line_name'] == settings.value("steam_name"):
                        hunterArea.get('name').setStyleSheet('QLabel{color:#cccc67}')
                    hunterArea.get('mmr').setText(str(hunterData['mmr']))
                    hunterArea.get('stars').setPixmap(star_pixmap(mmr_to_stars(hunterData['mmr'])))

                    profileid = hunterData["profileid"]
                    n_games = DbHandler.execute_query("select count(*) from 'hunter' where profileid is %d" % profileid)[0][0]


                    if hunterData['downedme'] or \
                    hunterData['downedbyme'] or \
                    hunterData['downedteammate'] or \
                    hunterData['downedbyteammate'] or \
                    hunterData['killedme'] or \
                    hunterData['killedbyme'] or \
                    hunterData['killedteammate'] or \
                    hunterData['killedbyteammate']:
                        hunterArea.get('kills').show()
                        kills = 1
                    else:
                        hunterArea.get('kills').hide()


                    if hunterData['bountypickedup']:
                        got_bounty = True
                        if hunterData['bountyextracted']:
                            extracted_bounty = True
                        hunterArea.get('bounties').show()
                    else:
                        hunterArea.get('bounties').hide()

                    if hunterData['hadWellspring']:
                        had_wellspring = True

                    if hunterData['teamextraction']:
                        team_extract = True
                    if n_games > 1:
                        hunterArea.get('ngames').setText("%d games" % n_games)
                    else:
                        hunterArea.get('ngames').setText('')

                else:
                    hunterArea.hide()
            huntersInfo.layout.addStretch()
            if got_bounty:
                if extracted_bounty:
                    teamArea.get('bounty').setText("Extracted with the bounty.")
                else:
                    teamArea.get('bounty').setText("Held the bounty.")
            if team_extract and not extracted_bounty:
                teamArea.get('bounty').setText("Extracted alive.")
            if had_wellspring:
                teamArea.get('bounty').setText("Activated the wellspring.")

            if qp:
                if HunterLabel.HideUsers:
                    name = '\tHunter %d\t' % team_num
                else:
                    name = '\t%s\t' % teamHuntersData[0]['blood_line_name']
            else:
                name = "\tTeam %d\t" % team_num
            if teamData['ownteam']:
                icon = livedIcon
            elif kills:
                icon = deadIcon
            else:
                icon = noneIcon 
            self.teamTabWidget.addTab(teamScrollArea,QIcon(icon),name)

    def eventFilter(self, obj, e):
        child = obj.parent().findChild(QWidget,'blood_line_name')
        dataType = obj.text()
        if e.type() == QEvent.Type.Enter:
            if child:
                name = child.text()
                ts = self.matchSelect.currentData()
                hunter = DbHandler.GetHunter(name,ts)
                self.ShowWindow(hunter,dataType)
                self.popup.move(e.globalPosition().x()+self.popup.size().width()/4,e.globalPosition().y()-self.popup.size().height()/4)
                self.setFocus()
        elif e.type() == QEvent.Type.Leave:
            self.popup = None
        return super().eventFilter(obj, e)

    def ShowWindow(self,hunter,data):
        if hunter == {}:    return
        self.popup = QMainWindow()
        self.popup.setStyleSheet('QWidget{border:1px solid red;}QLabel{border:0px;}*{font-size:18px;}')
        self.popup.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.popup.objectName = "popup"
        info = QWidget()
        self.popup.setCentralWidget(info)
        info.layout = QVBoxLayout()
        info.setLayout(info.layout)
        name = hunter['blood_line_name']
        if data == 'kills':
            if hunter['downedme']:
                info.layout.addWidget(QLabel('%s downed you %d times.' % (name, hunter['downedme'])))
            if hunter['downedbyme']:
                info.layout.addWidget(QLabel('you downed %s %d times.' % (name, hunter['downedbyme'])))
            if hunter['downedteammate']:
                info.layout.addWidget(QLabel('%s downed your teammate %d times.' % (name, hunter['downedteammate'])))
            if hunter['downedbyteammate']:
                info.layout.addWidget(QLabel('your teammate downed %s %d times.' % (name, hunter['downedbyteammate'])))
            if hunter['killedme']:
                info.layout.addWidget(QLabel('%s killed you.' % name))
            if hunter['killedbyme']:
                info.layout.addWidget(QLabel('you killed %s.' % name))
            if hunter['killedteammate']:
                info.layout.addWidget(QLabel('%s killed your teammate.' % name))
            if hunter['killedbyteammate']:
                info.layout.addWidget(QLabel('your teammate killed %s.' % name))
        elif data == 'bounties':
            if hunter['bountypickedup']:
                if hunter['bountyextracted']:
                    info.layout.addWidget(QLabel('%s extracted with the bounty.' % name))
                else:
                    info.layout.addWidget(QLabel('%s picked up the bounty.' % name))
        elif data == 'wellspring':
            if hunter['hadWellspring']:
                info.layout.addWidget(QLabel('%s activated the wellspring.' % name))
        self.popup.show()
        self.popup.setMaximumSize(self.popup.sizeHint())
        self.setFocus()

    def updateHuntDetails(self):
        if self.matchSelect.count() == 0:
            return
        ts = self.matchSelect.currentData()
        game = DbHandler.GetHunt(ts)
        entries = DbHandler.GetEntries(ts)
        qp = game['MissionBagIsQuickPlay']
        bounties = GetMatchBounties(game)
        eventPts = game['EventPoints']
        eventPts = 0 if eventPts is None else eventPts
        self.huntDetails.widget().get("gameType").setText("Quick Play" if qp else "Bounty Hunt")
        self.huntDetails.widget().get("bosses").setText("%s %s " % ("Bounties:" if not qp else "", " and ".join(bounties)))
        self.huntDetails.widget().get("teams").setText("%d %s" % (game['MissionBagNumTeams'], "hunters" if qp else "teams"))
        self.huntDetails.widget().get("eventPts").setText("Serpent Moon Points:\n%d" % eventPts)
        if qp:
            rifts_closed = 0
        else:
            clues_found = {
                'assassin': 0,
                'spider': 0,
                'butcher': 0,
                'scrapbeak': 0
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
        hunterkills = 0
        monsters_killed = {}
        monsterkills = 0
        assists = 0
        myKills = DbHandler.GetMyKills(ts)
        for entry in entries:
            if entry['entry_num'] < game['MissionBagNumEntries']:
                cat = entry['category']
                if 'wellsprings_found' in cat:
                    rifts_closed += 1
                if 'clues_found' in cat:
                    clues_found[entry['descriptorName'].split(' ')[1]] += 1
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
        if qp:
            self.huntDetails.widget().get("clues").setText('closed %d rifts.' % rifts_closed)
        else:
            text = []
            for boss in clues_found:
                if clues_found[boss] > 0:
                    text.append('Found %d of the clues for %s.' % (clues_found[boss],boss.capitalize()))
            self.huntDetails.widget().get("clues").setText(
                '\n'.join(text)
            )
 
        if qp:
            self.huntDetails.widget().get("teamkills").setText(
                'Hunter kills: %d<br> %s' % (hunterkills, '<br>'.join(["%dx <img src='%s'>" % (hunters_killed[m], star_path(m)) for m in hunters_killed if hunters_killed[m] > 0]))
            )
            self.huntDetails.widget().get("mykills").setText('%d assists.' % (assists))
        else:
            self.huntDetails.widget().get("teamkills").setText(
                'Team kills: %d<br> %s' % (hunterkills, '<br>'.join(["%dx <img src='%s'>" % (hunters_killed[m], star_path(m)) for m in hunters_killed if hunters_killed[m] > 0]))
            )
            self.huntDetails.widget().get("mykills").setText('%d kills, %d assists' % (myKills,assists))

        self.huntDetails.widget().get("mydeaths").setText('downed %d times' % (DbHandler.GetMyDeaths(self.matchSelect.currentData())))
        
        if monsterkills > 0:
            self.huntDetails.widget().get("monsterkills").setText(
                'Monster kills: %d<br> %s' % (monsterkills, '<br>'.join(["%d %s" % (monsters_killed[m], m) for m in monsters_killed if monsters_killed[m] > 0]))
            )
        else:
            self.huntDetails.widget().get("monsterkills").setText('')
        self.huntDetails.setFixedWidth(self.huntDetails.sizeHint().width()*2)


    def updateMatchSelection(self):
        self.matchSelect.clear()
        timestamps = DbHandler.execute_query("select timestamp from 'game' order by timestamp desc")
        if timestamps is None:  return
        timestamps = [t[0] for t in timestamps]
        for ts in timestamps:
            game = DbHandler.GetHunt(ts)
            qp = game["MissionBagIsQuickPlay"]
            nTeams = game["MissionBagNumTeams"]

            dead = game["MissionBagIsHunterDead"]
            teamKills = DbHandler.getTeamKills(ts)
            line = ' %s - %s - %02d teams - %d kills' % (
                unix_to_datetime(ts),
                'Quick Play ' if qp else 'Bounty Hunt',
                nTeams,
                teamKills
            );
            self.matchSelect.addItem(
                QIcon(deadIcon if dead else livedIcon),
                line,ts
            )

def GetMatchBounties(game):
    bounties = []
    if game['MissionBagBoss_0']: bounties.append('Butcher')
    if game['MissionBagBoss_1']: bounties.append('Spider')
    if game['MissionBagBoss_2']: bounties.append('Assassin')
    if game['MissionBagBoss_3']: bounties.append('Scrapbeak')
    return bounties
