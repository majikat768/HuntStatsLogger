from PyQt5.QtWidgets import QGridLayout, QLabel,QVBoxLayout,QSizePolicy, QComboBox, QScrollArea, QWidget, QTabWidget
from PyQt5.QtCore import QSettings, Qt
from PyQt5 import QtGui
from Connection import MmrToStars, unix_to_datetime
from GroupBox import GroupBox

class HuntHistory(GroupBox):
    def __init__(self,parent,layout,title='') -> None:
        super().__init__(layout,title)
        self.parent = parent
        self.connection = parent.connection
        self.setStyleSheet('QLabel{padding:0px;margin:0px;}')
        self.settings = QSettings('majikat','HuntStats')
        self.layout.setSpacing(4)
        #self.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Maximum)

        self.layout.addWidget(self.MatchSelect(),0,0,1,4)

        self.huntInfoBox = self.HuntInfoBox()
        self.teamInfoBox = self.TeamInfoBox()
        self.layout.addWidget(self.huntInfoBox,1,0,1,1)
        self.layout.addWidget(self.teamInfoBox,1,1,1,3)

        #self.layout.setRowStretch(self.layout.rowCount(),1)
    
    def MatchSelect(self):
        self.matchSelection = QComboBox()
        self.matchSelection.setStyleSheet('QComboBox{padding:8px;}')
        for timestamp in self.connection.GetAllTimestamps():
            self.matchSelection.addItem(
                '%s - %s - %d teams - %d kills - %s' % (
                    unix_to_datetime(timestamp),
                    'Quick Play' if self.connection.IsQuickPlay(timestamp) else 'Bounty Hunt',
                    self.connection.getNTeams(timestamp),
                    self.connection.GetMatchKills(timestamp),
                    'lived' if self.connection.Survived(timestamp) else 'died'
                )
                ,timestamp
            )

        self.matchSelection.activated.connect(self.updateHuntInfo)
        self.matchSelection.activated.connect(self.updateTeamInfo)
        return self.matchSelection
    
    def updateMatchSelect(self):
        self.matchSelection.clear()
        for timestamp in self.connection.GetAllTimestamps():
            self.matchSelection.addItem(
                '%s - %s - %d teams - %d kills - %s' % (
                    unix_to_datetime(timestamp),
                    'Quick Play' if self.connection.IsQuickPlay(timestamp) else 'Bounty Hunt',
                    self.connection.getNTeams(timestamp),
                    self.connection.GetMatchKills(timestamp),
                    'lived' if self.connection.Survived(timestamp) else 'died'
                )
                ,timestamp
            )

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
                    else:
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
                text.append('Found %d of the clues for %s.\t' % (clues_found[boss],boss))
        if len(text) > 0:
            self.cluesFound.setText('\n'.join(text))
        
        if hunterkills > 0:
            self.huntersKilled.setText(
                'Team killed %d hunters:<br> %s' % (hunterkills, '<br>'.join(["%d <img src='./assets/icons/_%dstar.png'>" % (hunters_killed[m], m) for m in hunters_killed if hunters_killed[m] > 0]))
            )
        else:
            self.huntersKilled.setText('')

        self.killsAndAssists.setText('you got %d kills and %d assists.' % (self.connection.GetMyKills(self.matchSelection.currentData()),assists))
        self.myDeaths.setText('you were killed %d times.' % (self.connection.GetMyDeaths(self.matchSelection.currentData())))
        
        if monsterkills > 0:
            self.monstersKilled.setText(
                'Team killed %d monsters:<br> %s' % (monsterkills, '<br>'.join(["%d %s" % (monsters_killed[m], m) for m in monsters_killed if monsters_killed[m] > 0]))
            )
        else:
            self.monstersKilled.setText('')


        self.mission.setText('Mission: %s' % ('Quick Play' if quickplay else 'Bounty Hunt'))
        if quickplay:
            self.bounties.setText('')
        else:
            self.bounties.setText('Bounties: %s' % (' and '.join(self.GetMatchBounties(game))))
        self.teams.setText('Teams: %d' % (game['MissionBagNumTeams']))

    def HuntInfoBox(self):
        self.huntInfoScrollArea = QScrollArea()
        self.huntInfoScrollArea.setWidgetResizable(True)
        self.huntInfoScrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.huntInfo = QWidget()
        self.huntInfo.layout = QVBoxLayout()
        self.huntInfo.setLayout(self.huntInfo.layout)

        self.mission = QLabel('Mission: bounty hunt')
        self.huntInfo.layout.addWidget(self.mission)
        self.bounties = QLabel('Bounties: Assassin and Scrapbeak')
        self.huntInfo.layout.addWidget(self.bounties)
        self.teams = QLabel('Teams: 12')
        self.huntInfo.layout.addWidget(self.teams)
        self.huntInfo.layout.addWidget(QLabel())

        self.cluesFound = QLabel('Found 3 of the clues for butcher\t')
        self.huntInfo.layout.addWidget(self.cluesFound)
        self.huntInfo.layout.addWidget(QLabel())
        self.huntersKilled = QLabel('Team killed 0 hunters')
        self.huntInfo.layout.addWidget(self.huntersKilled)
        self.huntInfo.layout.addWidget(QLabel())
        self.killsAndAssists = QLabel('You got 0 assists and 0 kills.')
        self.huntInfo.layout.addWidget(self.killsAndAssists)
        self.myDeaths = QLabel('You were killed 0 times.')
        self.huntInfo.layout.addWidget(self.myDeaths)
        self.huntInfo.layout.addWidget(QLabel())
        self.monstersKilled = QLabel('Team killed 0 monsters')
        self.huntInfo.layout.addWidget(self.monstersKilled)


        self.huntInfo.layout.addStretch()

        self.huntInfoScrollArea.setWidget(self.huntInfo)

        self.huntInfoScrollArea.setSizePolicy(QSizePolicy.Maximum,QSizePolicy.Expanding)
        return self.huntInfoScrollArea

    def updateTeamInfo(self):
        self.teamTabs.clear()
        teams = self.connection.GetMatchTeams(self.matchSelection.currentData())
        isquickplay = self.connection.IsQuickPlay(self.matchSelection.currentData())
        allhunters = self.connection.GetAllHunterData(self.matchSelection.currentData())
        for team in teams:
            teamInfoScrollArea = QScrollArea()
            teamInfoScrollArea.setWidgetResizable(True)
            teamInfoScrollArea.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Maximum)
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
                name = QLabel(hunter['blood_line_name'])
                mmr = QLabel('%d' % hunter['mmr'])
                stars = QLabel()
                stars.setPixmap(QtGui.QPixmap('./assets/icons/_%dstar.png' % MmrToStars(hunter['mmr'])))
                hunterInfo.layout.addWidget(name)
                hunterInfo.layout.addWidget(mmr)
                hunterInfo.layout.addWidget(stars)
                if hunter['downedme']:
                    hunterInfo.layout.addWidget(QLabel('They downed you %d times.' % hunter['downedme']))
                if hunter['downedbyme']:
                    hunterInfo.layout.addWidget(QLabel('you downed them %d times.' % hunter['downedbyme']))
                if hunter['downedteammate']:
                    hunterInfo.layout.addWidget(QLabel('They downed your teammate %d times.' % hunter['downedteammate']))
                if hunter['downedbyteammate']:
                    hunterInfo.layout.addWidget(QLabel('your teammate downed them %d times.' % hunter['downedbyteammate']))
                if hunter['killedme']:
                    hunterInfo.layout.addWidget(QLabel('They killed you.'))
                if hunter['killedbyme']:
                    hunterInfo.layout.addWidget(QLabel('you killed them.'))
                if hunter['killedteammate']:
                    hunterInfo.layout.addWidget(QLabel('They killed your teammate.'))
                if hunter['killedbyteammate']:
                    hunterInfo.layout.addWidget(QLabel('your teammate killed them.'))
                if hunter['bountypickedup']:
                    got_bounty = True
                    hunterInfo.layout.addWidget(QLabel('they picked up the bounty.'))
                if hunter['hadWellspring']:
                    had_wellspring = True
                    hunterInfo.layout.addWidget(QLabel('they activated the wellspring.'))
                if hunter['bountyextracted']:
                    extracted_bounty = True
                    hunterInfo.layout.addWidget(QLabel('they extracted with the bounty.'))
                if hunter['teamextraction']:
                    team_extract = True
                teamInfo.layout.addWidget(hunterInfo)
                hunterInfo.layout.addStretch()
            if got_bounty:
                if extracted_bounty:
                    teamSubInfo.layout.addWidget(QLabel('They extracted with the bounty.'))
                else:
                    teamSubInfo.layout.addWidget(QLabel('They had the bounty.'))
            if had_wellspring:
                teamSubInfo.layout.addWidget(QLabel('They had the wellspring.'))
            if team_extract and not extracted_bounty:
                teamSubInfo.layout.addWidget(QLabel('They extracted.'))

            #teamInfo.layout.setColumnStretch(teamInfo.layout.columnCount(),1)
            
    def TeamInfoBox(self):
        self.teamTabs = QTabWidget()
        self.teamTabs.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Expanding)
        return self.teamTabs

    def GetMatchBounties(self,game):
        bounties = []
        if game['MissionBagBoss_0']: bounties.append('Butcher')
        if game['MissionBagBoss_1']: bounties.append('Spider')
        if game['MissionBagBoss_2']: bounties.append('Assassin')
        if game['MissionBagBoss_3']: bounties.append('Scrapbeak')
        return bounties