from datetime import datetime
from socket import getnameinfo
import sqlite3
import sys
import time
from PyQt5.QtCore import QThread,QSettings,Qt,QSize
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from threading import *
import Logger

'''
detects changes to the Hunt Showdown 'attributes.xml' file.
when change is found, backup new .xml file, also convert team and game data to json format.
when change is found, parse .xml file and create json objects, write json to a file, and write objects to a sql database.
'''

def unix_to_datetime(timestamp):
    return datetime.fromtimestamp(timestamp).strftime('%H:%M %m/%d/%y')

database = 'huntstats.db'

class App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.title = 'Hunt Stats'
        self.titlebar = QWidget()
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.mouseHold = False
        #self.setWindowFlags(Qt.CustomizeWindowHint)
        self.setAttribute(Qt.WA_NoSystemBackground, True)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.x = 64
        self.y = 64
        self.width = 1280 
        self.height = 720
        self.settings = QSettings('majikat768','hunt stats')
        self.xml_path = self.settings.value('xml_path','')
        self.xml_label = QLabel(self.xml_path,self)
        self.thread = QThread();
        self.logger = Logger.Logger();
        if self.xml_path != '':
            self.startLogger()

        self.main_frame = QWidget()
        self.layout = QGridLayout()
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0,0,0,0)

        self.tabs = QTabWidget()
        #self.tabs.setFixedHeight(220)
        self.inputGroup = QGroupBox('Settings')
        self.inputGroup.setObjectName('HuntSettings')
        self.HunterGroup = QGroupBox('Hunter')

        self.GameInfoGroup = QGroupBox('Last Hunt')
        self.GameInfoScrollArea = QScrollArea()
        self.GameInfoStats = QWidget()
        self.GameInfoScrollArea.setWidget(self.GameInfoStats)

        self.usernameInput = QLineEdit(self.settings.value('username',''))
        self.updateUsernameButton = QPushButton('update username')

        self.select_file_button = QPushButton(' Select Hunt installation folder  ',self)
        time.sleep(1)
        self.initUI()
        self.updateLastMatch()
        self.show()

    def mousePressEvent(self, event: QMouseEvent) -> None:
        super().mousePressEvent(event)
        self.offset = event.pos()
        self.start = event.globalPos()
        self.windowsize = self.size()
        self.mouseHold = True

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        super().mouseReleaseEvent(event)
        self.mouseHold = False

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        super().mouseMoveEvent(event)
        if self.mouseHold:
            if self.offset.x() < self.titlebar.width() and self.offset.y() < self.titlebar.height():
                self.move(
                    self.mapToGlobal(event.pos()).x()-self.offset.x(),
                    self.mapToGlobal(event.pos()).y()-self.offset.y()
                )


            pass

    '''
    def paintEvent(self,event=None):
        painter = QPainter(self)
        painter.setOpacity(0.0)
        painter.setBrush(Qt.white)
        painter.setPen(QPen(Qt.white))
        painter.drawRect(self.rect())
    '''

    def initTitleBar(self):
        self.titlebar.layout = QHBoxLayout()
        self.titlebar.setLayout(self.titlebar.layout)
        self.titlebar.setObjectName('TitleBar')

        closeButton = QPushButton('X',self,clicked=self.close)
        closeButton.setObjectName('Exit')
        closeButton.setFixedSize(32,32)
        self.titlebar.layout.addWidget(closeButton,Qt.AlignRight)
        self.titlebar.layout.setAlignment(Qt.AlignRight)
        self.layout.addWidget(self.titlebar)

    def initHunterGroup(self):
        groupLayout = QGridLayout()
        self.HunterGroup.setLayout(groupLayout)
        self.HunterName = QLabel()
        self.HunterName.setObjectName("HunterNameLabel")
        groupLayout.addWidget(self.HunterName,0,0)
        self.StarLabel = QLabel()
        groupLayout.addWidget(self.StarLabel,1,0)
        self.MMRLabel = QLabel()
        groupLayout.addWidget(self.MMRLabel,2,0)

        groupLayout.addWidget(QLabel('High score:'),0,1)
        self.HighestMMRLabel = QLabel()
        groupLayout.addWidget(self.HighestMMRLabel,1,1)
        self.HighestStarLabel = QLabel()
        groupLayout.addWidget(self.HighestStarLabel,2,1)
        self.layout.addWidget(self.HunterGroup)

    def initGameGroup(self):
        groupLayout = QGridLayout()
        self.GameInfoGroup.setLayout(groupLayout)
        self.LastHunt = QLabel()
        self.LastHuntStats = QLabel()
        self.MatchSelection = QComboBox()
        for match in self.get_all_timestamps():
            try:
                self.MatchSelection.addItem(unix_to_datetime(match),match)
            except:
                continue
        print(self.MatchSelection.currentData())
        self.MatchSelection.activated.connect(self.setMatchInfo)
        self.GameInfoScrollArea.layout = QGridLayout(self.GameInfoScrollArea.widget())
        self.GameInfoScrollArea.setWidgetResizable(True)
        self.GameInfoScrollArea.setLayout(self.GameInfoScrollArea.layout)
        self.GameInfoStats.layout = QGridLayout()
        self.GameInfoStats.setLayout(self.GameInfoStats.layout)
        self.GameInfoStats.layout.addWidget(self.LastHunt,0,0)
        self.GameInfoStats.layout.addWidget(self.LastHuntStats,1,0)

        groupLayout.addWidget(self.MatchSelection,0,0,1,2)
        groupLayout.addWidget(self.GameInfoScrollArea,1,0)
        groupLayout.addWidget(self.tabs,1,1)
        self.tabs.setMinimumWidth(600)
        self.tabs.setMinimumHeight(300)
        self.GameInfoScrollArea.setMinimumWidth(300)
        #groupLayout.addWidget(self.tabs,2,0,1,2)

        self.layout.addWidget(self.GameInfoGroup)

    def init_input_group(self):
        groupLayout = QGridLayout()
        self.inputGroup.setLayout(groupLayout)
        groupLayout.addWidget(self.select_file_button,0,0)
        groupLayout.addWidget(self.xml_label,0,1,Qt.AlignRight)
        groupLayout.addWidget(self.usernameInput,2,1)
        groupLayout.addWidget(self.updateUsernameButton,2,0)
        self.layout.addWidget(self.inputGroup)

    def initUI(self):
        self.setWindowTitle(self.title);
        self.setCentralWidget(self.main_frame);
        self.main_frame.setLayout(self.layout)
        self.usernameInput.setPlaceholderText('Enter your Steam username....')
        self.usernameInput.setVisible(False)
        self.usernameInput.setMaximumWidth(256)
        self.usernameInput.returnPressed.connect(self.updateUsername)
        self.updateUsernameButton.clicked.connect(self.updateUsername)
        self.initTitleBar()
        self.initHunterGroup()
        self.initGameGroup()
        self.init_input_group()
        self.setGeometry(self.x,self.y,self.width,self.height)
        #self.setMaximumHeight(400)
        self.select_file_button.clicked.connect(self.SelectXmlFile)

    def get_all_timestamps(self):
        connection = sqlite3.connect(database)
        cursor = connection.cursor();
        query = "select timestamp from 'game' order by timestamp desc"
        try:
            cursor.execute(query)
            return [x[0] for x in cursor.fetchall()]
        except sqlite3.OperationalError as msg:
            'alltime'
            print(msg)
            return []

    def get_last_match_timestamp(self):
        connection = sqlite3.connect(database)
        cursor = connection.cursor();
        query = "select max(timestamp) from 'game'"
        try:
            cursor.execute(query)
            return cursor.fetchone()
        except sqlite3.OperationalError as msg:
            print('last match timestamp')
            print(msg)
            return -1


    def get_own_MMR(self):
        connection = sqlite3.connect(database)
        cursor = connection.cursor();
        query = "select mmr from 'hunter' where timestamp is (select max(timestamp) from 'hunter') and blood_line_name is '%s'" % (self.settings.value('username',''))
        try:
            cursor.execute(query)
        except sqlite3.OperationalError as msg:
            print('get own mmr error')
            return [-1]
        return cursor.fetchone()

    def updateUsername(self):
        if self.usernameInput.isVisible():
            self.usernameInput.setVisible(False)
            self.settings.setValue('username',self.usernameInput.text())
            self.setHunterStats()

        else:
            self.usernameInput.setVisible(True)
            self.usernameInput.setFocus()

    def get_stars(self, mmr):
        return 0 if mmr == -1 else 1 if mmr < 2000 else 2 if mmr < 2300 else 3 if mmr < 2600 else 4 if mmr < 2750 else 5 if mmr < 3000 else 6

    def setHunterStats(self):
        print('settin stats')
        mmr = self.get_own_MMR()
        if mmr == None: mmr = [-1]
        mmr = mmr[0]
        self.settings.setValue('mmr',mmr)
        if mmr > self.settings.value('max_mmr',-1):
            self.settings.setValue('max_mmr',mmr)
        self.HighestMMRLabel.setText('MMR: %d\n' % self.settings.value('max_mmr',-1))

        stars = self.get_stars(mmr)
        self.settings.setValue('stars',stars)
        if stars > self.settings.value('max_stars',-1):
            self.settings.setValue('max_stars',stars)
        self.HighestStarLabel.setPixmap(QPixmap('./assets/icons/_%dstart.png' % stars))

        username = self.settings.value('username','')

        self.HunterName.setText(username.upper())
        self.MMRLabel.setText('MMR: %d' % (mmr))
        self.StarLabel.setPixmap(QPixmap('./assets/icons/_%dstar.png' % stars))
        #self.ownMMR.setText('\nHunter: %s\nMMR: %s\nStars: %s\n' % (username, str(mmr),str(stars)))

    def SelectXmlFile(self):
        options = QFileDialog.Options()
        #options |= QFileDialog.DontUseNativeDialog
        path = QFileDialog.getExistingDirectory(self,"Select steam install directory",self.xml_path,options=options)
        print(path)
        if path != '':
            self.settings.setValue('xml_path',path)
            self.xml_path = self.settings.value('xml_path','')
            self.xml_label.setText(self.xml_path)
            self.startLogger()

    def getAvgKills(self):
        pass


    def getAllHunterData(self,timestamp,cursor):
        try:
            hunters_query = "select * from 'hunter' where timestamp is %s" % timestamp
            cursor.execute(hunters_query)
            hunter_cols = [desc[0] for desc in cursor.description]
            hunter_stats = cursor.fetchall()
            if hunter_stats is None:    return
            allhunters = []
            for hunter in hunter_stats:
                allhunters.append({hunter_cols[i] : hunter[i] for i in range(len(hunter_cols))})
            return allhunters
        except sqlite3.OperationalError as msg:
            print('hunter error')
            print(msg)
            return

    def getGameData(self,timestamp,cursor):
        text = ''
        game_query = "select * from 'game' where timestamp is %s" % timestamp
        try:
            cursor.execute(game_query)
            '''
            the game stats column names you care about:
            ['timestamp',
            'MissionBagBoss_0',     // butcher
            'MissionBagBoss_1',     // spider
            'MissionBagBoss_2',     // assassin
            'MissionBagBoss_3',     // scrapbeak
            'MissionBagIsHunterDead',
            'MissionBagIsQuickPlay',
            'MissionBagNumTeams']
            '''
            game_cols = [desc[0] for desc in cursor.description]
            game_stats = cursor.fetchone()
            if game_stats is None:  return
            game_dict = {game_cols[i] : game_stats[i] for i in range(len(game_cols))}
            return game_dict
        except sqlite3.OperationalError as msg:
            print('game data error')
            print(msg)
        return None

    def isQuickPlay(self,timestamp):
        connection = sqlite3.connect(database)
        cursor = connection.cursor()
        query = "select MissionBagIsQuickPlay from 'game' where timestamp is %s" % timestamp
        try:
            cursor.execute(query)
            qp = cursor.fetchone()
            return -1 if qp is None else qp[0]
        except sqlite3.OperationalError as msg:
            print('isquickplay error')
            print(msg)
            return -1

    def setMatchInfo(self,timestamp):
        timestamp = self.MatchSelection.currentData()
        connection = sqlite3.connect(database)
        cursor = connection.cursor();
        isquickplay = self.isQuickPlay(timestamp)
        print(isquickplay)
        team_query = "select * from 'team' where timestamp is %s" % timestamp
        entry_query = "select * from 'entry' where timestamp is %s" % timestamp
        text = ''

        self.tabs.clear()
        game_dict = self.getGameData(timestamp,cursor)
        if game_dict == None:   return
        print("*")
        print(game_dict)
        #text += str(datetime.fromtimestamp(game_dict['timestamp']).strftime('Logged %H:%M on %m/%d/%y\n'))
        if game_dict['MissionBagIsHunterDead']:
            #text += 'You died.\n'
            pass
        else:
            #text += 'You extracted.\n'
            pass
        text += 'Teams: %d\n' % (game_dict['MissionBagNumTeams'])
        text += 'Mission: '
        text += 'Quickplay\n' if game_dict['MissionBagIsQuickPlay'] else 'Bounty Hunt\n'
        if not isquickplay:
            bounties = []
            if game_dict['MissionBagBoss_0']: bounties.append('Butcher')
            if game_dict['MissionBagBoss_1']: bounties.append('Spider')
            if game_dict['MissionBagBoss_2']: bounties.append('Assassin')
            if game_dict['MissionBagBoss_3']: bounties.append('Scrapbeak')
            text += 'Bounties: ' + ' and '.join(bounties)

        self.LastHunt.setText(text)
        text = '<html>'
        try:
            cursor.execute(entry_query)
            entry_cols = [desc[0] for desc in cursor.description]
            entry_stats = cursor.fetchall()
            if entry_stats is None: return
        except sqlite3.OperationalError as msg:
            print('entry error')
            print(msg)
        entries = []
        for entry in entry_stats:
            entries.append({entry_cols[i] : entry[i] for i in range(len(entry_cols))})

        wellsprings_found = 0
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
        assists = 0
        hunterkills = 0
        monsters_killed = {}
        monsterkills = 0
        gold = 0
        revives = 0
        reward = 0
        upgrade_points = 0
        descriptor = {}

        '''
        also to do:  book unlocks? 
        current hunter level / bloodline level?
        currently unable to accurately calculate xp earned,
        or hunt dollars earned.
        has something to do with descriptorType field, i think
        '''
        # accolade_players_killed
        for entry in entries:
            if entry['entry_num'] < game_dict['MissionBagNumEntries']:
                category = entry['category']
                if 'contract' in category:
                    reward += entry['rewardSize']*4
                else:
                    reward += entry['rewardSize']
                if 'reviver' in category:
                    revives += entry['amount']
                if 'found_gold' in category:
                    pass
                if 'hunter_points' in category:
                    upgrade_points += entry['rewardSize']
                if 'bloodbonds' in category:
                    pass
                if 'tokens' in category:
                    pass
                if 'clue' in entry['descriptorName']:
                    if 'quickplay' in entry['descriptorName']:
                        wellsprings_found += 1
                    else:
                        boss = entry['descriptorName'].split(' ')[1]
                        clues_found[boss] += 1
                    pass
                if 'players_killed' in category:
                    if 'assist' in category:
                        assists += entry['amount']
                    else:
                        mm = int(entry['descriptorName'].split(' ')[4])
                        hunters_killed[mm] = entry['amount']
                        hunterkills += entry['amount']
                if 'monsters_killed' in category:
                    monster = entry['descriptorName'].split(' ')[1]
                    if monster not in monsters_killed.keys():
                        monsters_killed[monster] = 0
                    monsters_killed[monster] += entry['amount']
                    monsterkills += entry['amount']
                    pass
        if wellsprings_found > 0:
            text += 'Closed %d rifts' % (4 if wellsprings_found > 4 else wellsprings_found)
            if wellsprings_found >= 4:
                text += ' and activated the wellspring.<br><br>'
            else:
                text += '.<br><br>'
        for boss in clues_found:
            if clues_found[boss] > 0:
                text += 'Found %d of the clues for %s.<br><br>' % (clues_found[boss],boss)
        text += '\n'
        if hunterkills > 0:
            text += 'Team killed %d hunters:<br>' % hunterkills
            kill_line = []
            for mm in hunters_killed:
                if hunters_killed[mm] > 0:
                    #kill_line.append('%dx %d star' % (hunters_killed[mm],mm))
                    kill_line.append('<img src="./assets/icons/_%dstar.png">x%d' % (mm,hunters_killed[mm]))
            text += '<br>'.join(kill_line)
            text += '<br><br>'
        if assists > 0:
            text += '%d assists.<br><br>' % assists;
        if monsterkills > 0:
            text += 'Team killed %d monsters:<br>' % monsterkills
            for monster in monsters_killed.keys():
                text += '%d %s<br>' % (monsters_killed[monster], monster)
            text += '<br>'

        if hunterkills > self.settings.value('max_hunter_kills',-1):
            self.settings.setValue('max_hunter_kills',hunterkills)
        if monsterkills > self.settings.value('max_monster_kills',-1):
            self.settings.setValue('max_monster_kills',monsterkills)
        text += '</html>'
        self.LastHuntStats.setText(text)

        allhunters = self.getAllHunterData(timestamp,cursor)

        try:
            cursor.execute(team_query)
            team_cols = [desc[0] for desc in cursor.description]
            team_stats = cursor.fetchall()
            if team_stats is None:  return
        except sqlite3.OperationalError as msg:
            print('team error')
            print(msg)
        
        teams = []
        for team in team_stats:
            teams.append({team_cols[i] : team[i] for i in range(len(team_cols))})

        for team in teams:
            teamArea = QScrollArea()
            teamTab = QWidget()
            teamTab.setObjectName('teamtab')
            teamArea.setWidget(teamTab)
            hunters = [x for x in allhunters if x['team_num'] == team['team_num']]
            if not isquickplay:
                self.tabs.addTab(teamArea,'Team %d\n(%d hunters)' % (team['team_num'], team['numplayers']))
            else:
                hunter = hunters[0]
                self.tabs.addTab(teamArea,'%s' % hunter['blood_line_name'])
            teamArea.layout = QGridLayout(teamArea.widget())
            teamArea.setWidgetResizable(True)
            teamArea.setLayout(teamArea.layout)
            #teamTab.layout.addWidget(hunterInfo)
            teamInfo = QLabel();
            teamTab.layout = QGridLayout()
            teamTab.setLayout(teamTab.layout)
            #teamArea.layout.addWidget(teamInfo,0,0)
            teamInfo.setText('Team MMR: %d' % (team['mmr']))

            got_bounty = False
            team_extract = False
            for i in range(len(hunters)):
                text = ''
                p = hunters[i]
                hunterGroup = QGroupBox()
                hunterGroup.setObjectName('huntergroup')
                groupLayout = QVBoxLayout()
                hunterGroup.setLayout(groupLayout)
                hunterName = QLabel(p['blood_line_name'])
                hunterMmr = QLabel(str(p['mmr']))
                hunterStars = QLabel()
                hunterStars.setPixmap(QPixmap('./assets/icons/_%dstar.png' % self.get_stars(p['mmr'])))
                hunterInfo = QLabel();
                groupLayout.addWidget(hunterName)
                groupLayout.addWidget(hunterStars)
                groupLayout.addWidget(hunterMmr)
                groupLayout.addWidget(hunterInfo)
                teamTab.layout.addWidget(hunterGroup,1,i)
                #teamArea.layout.addWidget(hunterInfo,1,i,Qt.AlignTop)
                if p['downedme']:
                    text += 'They downed you %d times.\n' % p['downedme']
                if p['downedbyme']:
                    text += 'You downed them %d times.\n' % p['downedbyme']
                if p['killedme']:
                    text += 'They killed you %d times.\n' % p['killedme']
                if p['killedbyme']:
                    text += 'You killed them %d times.\n' % p['killedbyme']
                if p['bountypickedup']:
                    text += 'They picked up the bounty.\n'
                if p['killedbyteammate']:
                    text += 'They were killed by your team.\n'
                if p['killedteammate']:
                    text += 'They killed your teammate.\n'
                if p['hadWellspring']:
                    text += 'They had the wellspring.\n'
                if p['teamextraction']:
                    if p['bountyextracted']:
                        text += 'They extracted with the bounty.\n'
                        got_bounty = True
                    else:
                        text += 'They extracted alive.\n'
                hunterInfo.setText(text) 
            text += '\n\n'
            
    def updateLastMatch(self):
        print('update last match')
        self.MatchSelection.clear()
        for match in self.get_all_timestamps():
            try:
                self.MatchSelection.addItem(
                    '%s - %s' % (unix_to_datetime(match), 'Quick Play' if self.isQuickPlay(match) else 'Bounty Hunt'), match
                )
            except:
                continue
        self.setHunterStats()
        print(self.get_last_match_timestamp())
        self.setMatchInfo(self.get_last_match_timestamp())

    def startLogger(self):
        self.logger.set_path(self.xml_path)
        self.logger.moveToThread(self.thread)
        self.thread.started.connect(self.logger.run)
        self.logger.finished.connect(self.thread.quit)
        self.logger.finished.connect(self.logger.deleteLater)
        self.logger.progress.connect(self.updateLastMatch)
        self.logger.finished.connect(self.thread.deleteLater)
        self.thread.start()

if __name__ == '__main__':
    app = QApplication(sys.argv)

    QFontDatabase.addApplicationFont('./assets/crimsontext/CrimsonText-Regular.ttf')
    app.setStyleSheet(open('stylesheet.qss','r').read())

    ex = App()

    app.exec_()
    Logger.killall = True