import json
import time
import os
import sqlite3
from datetime import datetime
from PyQt5.QtCore import QSettings,QObject, pyqtSignal

db = 'huntstats.db'
settings = QSettings('./settings.ini',QSettings.Format.IniFormat)
killall = False

def tables_exist():
    connection = sqlite3.connect(db)
    cursor = connection.cursor()
    query = "select name from sqlite_master where type = 'table' and name = ? or name = ? or name = ? or name = ?"
    tables = ('game','hunter','entry','team',)
    try:
        cursor.execute(query,tables)
        result = True if len(cursor.fetchall()) == 4 else False
    except sqlite3.OperationalError as msg:
        print('tables_exist()')
        print(msg)
        result = False
    connection.close()
    return result

def create_tables():
    print('creating tables')
    connection = sqlite3.connect(db)
    cursor = connection.cursor()
    schemafile = './schema.sql'
    cursor.executescript(open(schemafile,'r').read())
    print(cursor.fetchall())
    '''
    for title in ['game','entry','hunter','team']:
        print(title)
        for c in cursor.execute('pragma table_info(%s)' % title):
            print(c)
        print()
    '''
    connection.close()

def get_num_hunters(rows, team_num):
    for i in rows['team']:
        team = rows['team'][i]
        if team['team_num'] == team_num:
            return team['numplayers']
    return -1

def MmrToStars(mmr):
    return 0 if mmr == -1 else 1 if mmr < 2000 else 2 if mmr < 2300 else 3 if mmr < 2600 else 4 if mmr < 2750 else 5 if mmr < 3000 else 6

def unix_to_datetime(timestamp):
    return datetime.fromtimestamp(timestamp).strftime('%H:%M %m/%d/%y')

class Connection(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(str)
    def __init__(self) -> None:
        QObject.__init__(self)
        if not tables_exist():
            create_tables()
        self.jsondir = os.path.join(os.getcwd(),'json')
        if not os.path.exists(self.jsondir):
            os.makedirs(self.jsondir)
        self.logdir = os.path.join(os.getcwd(),'logs')
        if not os.path.exists(self.logdir):
            os.makedirs(self.logdir)
        self.logfile = os.path.join(self.logdir,'log')
        self.current_files = os.listdir(self.jsondir)
        for file in self.current_files:
            self.write_json_to_sql(os.path.join(self.jsondir,file),log=False)

    def file_added(self):
        current_files = os.listdir(self.jsondir)
        if len(current_files) > len(self.current_files):
            self.current_files = current_files
            print('file added %d' % len(self.current_files))
            return True
        return False

    def NumTimesSeen(self,profileid):
        connection = sqlite3.connect(db)
        cursor = connection.cursor();
        query = "select count(*) from 'hunter' where profileid is ?"
        try:
            cursor.execute(query,(profileid,))
            n = cursor.fetchone()[0]
        except sqlite3.OperationalError as msg:
            self.print(msg)
            n = -1
        connection.close()
        return n;

    def newest_file(self):
        f = os.path.join(
            self.jsondir,max(
                self.current_files,
                key=lambda x : os.stat(os.path.join(self.jsondir,x)).st_mtime
            )
        )
        print(f)
        return f

    def run(self):
        global killall
        while(True):
            time.sleep(1)
            if(self.file_added()):
                self.write_json_to_sql(self.newest_file())
            if killall:
                self.finished.emit()
                break

    def GetMaxMMR(self):
        connection = sqlite3.connect(db)
        cursor = connection.cursor();
        query = "select max(mmr) from 'hunter' where blood_line_name is '%s'" % settings.value('hunterName','')
        try:
            cursor.execute(query)
            mmr = cursor.fetchone()[0]
        except sqlite3.OperationalError as msg:
            self.print(msg)
            mmr = 0
        return 0 if mmr is None else mmr

    def insert_row(self,table, row):
        connection = sqlite3.connect(db)
        cursor = connection.cursor();
        
        columns = [i for i in row.keys()]
        values = [row[i] for i in columns]

        query = "insert or ignore into %s (%s) values (%s)" % (table,','.join(columns), ('?,'*len(columns))[:-1])
        try:
            cursor.execute(query, (values))
            #cursor.executemany(query,(values))
            #print('success.')

        except sqlite3.OperationalError as msg:
            self.print('fail! ' + str(msg))
        connection.commit()
        connection.close()

    def print(self,msg, ping=True):
        print(msg)
        with open(self.logfile,'a') as log:
            log.write(msg)
            log.write('\n')
        if(ping):
            self.progress.emit(msg)

    def write_json_to_sql(self,file,log=True):
        rows = json.load(open(file,'r'))
        timestamp = file[file.index('attributes'):].split('_')[1].split('.')[0]

        if log:
            self.print('writing rows to database from %s' % file,False)
        num_teams = rows['game']['MissionBagNumTeams']
        num_entries = rows['game']['MissionBagNumEntries']
        
        rows['game']['timestamp'] = timestamp
        self.insert_row('game',rows['game'])
        rows['game'].pop('timestamp')

        for i in rows['team']:
            team = rows['team'][i]
            if team['team_num'] < num_teams:
                team['timestamp'] = timestamp
                self.insert_row('team',team)
                team.pop('timestamp')

        for i in rows['entry']:
            entry = rows['entry'][i]
            if entry['entry_num'] < num_entries:
                entry['timestamp'] = timestamp
                self.insert_row('entry',entry)
                entry.pop('timestamp')

        for i in rows['hunter']:
            team = rows['hunter'][i]
            for j in team:
                hunter = team[j]
                if hunter['team_num'] < num_teams and hunter['hunter_num'] < get_num_hunters(rows,hunter['team_num']):
                    hunter['timestamp'] = timestamp
                    self.insert_row('hunter',hunter)
                    hunter.pop('timestamp')
        if log:
            self.print('data written')
        self.GetTotalHuntCount()


    def deleteRecord(self,timestamp):
        connection = sqlite3.connect(db)
        cursor = connection.cursor();
        queries = [
        "delete from 'game' where timestamp is ?", 
        "delete from 'team' where timestamp is ?",
        "delete from 'hunter' where timestamp is ?",
        "delete from 'entry' where timestamp is ?"
        ]

        try:
            for q in queries:
                cursor.execute(q,(timestamp,))
                connection.commit()
        except sqlite3.OperationalError as msg:
            self.print(msg)
        query = "select * from 'game' where 'timestamp' is %s" % timestamp
        cursor.execute(query)
        connection.close()


    def getNTeams(self,timestamp):
        connection = sqlite3.connect(db)
        cursor = connection.cursor();
        query = "select MissionBagNumTeams from 'game' where timestamp is %s" % timestamp;
        try:
            cursor.execute(query)
            numteams = int(cursor.fetchone()[0])
            if numteams is None:
                numteams = 0
        except sqlite3.OperationalError as msg:
            self.print(msg)
            numteams = 0
        connection.close()
        return numteams

    def GetProfileId(self,name):
        print('profile name ',name)
        connection = sqlite3.connect(db)
        cursor = connection.cursor();
        query = "select profileid from 'hunter' where blood_line_name is ?"
        try:
            cursor.execute(query,(name,))
            id = cursor.fetchone()
            print(id)
            id = id[0] if id != None else -1 
        except sqlite3.OperationalError as msg:
            self.print('Connection.GetProfileId()')
            self.print(msg)
            id = -1
        connection.close()
        return id

    def SetOwnMMR(self):
        connection = sqlite3.connect(db)
        cursor = connection.cursor();
        query = "select mmr from 'hunter' where timestamp is (select max(timestamp) from 'hunter') and profileid is '%s'" % (settings.value('profileid',''))
        try:
            cursor.execute(query)
            mmr = cursor.fetchone()
            mmr = -1 if mmr is None else mmr[0]
        except sqlite3.OperationalError as msg:
            self.print('get own mmr error')
            mmr = -1
        connection.close()
        settings.setValue('mmr',mmr)
    
    def GetTotalHuntCount(self):
        connection = sqlite3.connect(db)
        cursor = connection.cursor();
        query = "select count(timestamp) from 'game'"
        try:
            cursor.execute(query)
            huntcount = cursor.fetchone()[0]
        except sqlite3.OperationalError as msg:
            self.print(msg)
            huntcount = -1
        connection.close()
        if huntcount is None:
            huntcount = 0
        settings.setValue('total_hunts',huntcount)
        return huntcount

    def SetTotalKills(self):
        connection = sqlite3.connect(db)
        cursor = connection.cursor()
        query = "select sum(downedbyme + killedbyme) from 'hunter' where (downedbyme > 0 or killedbyme > 0)"
        try:
            cursor.execute(query)
            kills = cursor.fetchone()[0]
        except sqlite3.OperationalError as msg:
            self.print('SetMyTotalKills %s' % msg)
            kills = -1
        if kills is None:
            kills = 0
        settings.setValue('total_kills',kills)
    
    def SetTotalDeaths(self):
        connection = sqlite3.connect(db)
        cursor = connection.cursor()
        query = "select sum(downedme + killedme) from 'hunter' where (downedme > 0 or killedme > 0)"
        try:
            cursor.execute(query)
            deaths = cursor.fetchone()[0]
        except sqlite3.OperationalError as msg:
            self.print('SetMyTotalDeaths %s' % msg)
            deaths = -1
        if deaths is None:
            deaths = 0
        settings.setValue('total_deaths',deaths)
    
    def SetTotalAssists(self):
        connection = sqlite3.connect(db)
        cursor = connection.cursor()
        query = "select sum(amount) from 'entry' where category is 'accolade_players_killed_assist'"
        try:
            cursor.execute(query)
            assists = cursor.fetchone()[0]
        except sqlite3.OperationalError as msg:
            self.print('SetMyTotalAssists %s' % msg)
            assists = -1
        if assists is None:
            assists = 0
        settings.setValue('total_assists',assists)

    def SetKDA(self):
        connection = sqlite3.connect(db)
        cursor = connection.cursor()
        self.SetTotalKills()
        self.SetTotalDeaths()
        self.SetTotalAssists()
        kills = int(settings.value('total_kills',-1))
        deaths = int(settings.value('total_deaths',-1))
        assists = int(settings.value('total_assists',-1))
        kda = -1.0
        if deaths == 0:
            kda = 0
        else:
            kda = (kills + assists) / deaths
        settings.setValue('kda',round(kda,4))

    def Survived(self, timestamp):
        connection = sqlite3.connect(db)
        cursor = connection.cursor();
        query = "select MissionBagIsHunterDead from 'game' where timestamp is %d" % timestamp
        try:
            cursor.execute(query)
            dead = cursor.fetchone()[0]
        except sqlite3.OperationalError as msg:
            print('survived %s' % msg)
            dead = 0
        connection.close()
        return not dead

    def GetMatchData(self, timestamp):
        connection = sqlite3.connect(db)
        cursor = connection.cursor();
        query = "select * from 'game' where timestamp is %s" % timestamp
        try:
            cursor.execute(query)
            game_stats = cursor.fetchone()
            if game_stats is None:
                return {}
            game_cols = [desc[0] for desc in cursor.description]
            game = {game_cols[i] : game_stats[i] for i in range(len(game_cols))}
            return game
        except sqlite3.OperationalError as msg:
            print('GetMatchData %s' % msg)
            print(query)
            return {}

    def GetHunterData(self, name, timestamp):
        connection = sqlite3.connect(db)
        cursor = connection.cursor();
        query = "select * from 'hunter' where blood_line_name is ? and timestamp is ?"
        try:
            cursor.execute(query,(name, timestamp,))
            results = cursor.fetchone()
            if results is None:
                return {}
            cols = [desc[0] for desc in cursor.description]
            hunter = {cols[i] : results[i] for i in range(len(cols))}
        except sqlite3.OperationalError as msg:
            print(msg)
            hunter = {}
        connection.close()
        return hunter

    def GetMatchEntries(self, timestamp):
        connection = sqlite3.connect(db)
        cursor = connection.cursor();
        query = "select * from 'entry' where timestamp is %s" % timestamp
        try:
            cursor.execute(query)
            entry_stats = cursor.fetchall()
            if entry_stats is None:
                return {}
            entries = []
            entry_cols = [desc[0] for desc in cursor.description]
            for entry in entry_stats:
                entries.append({entry_cols[i] : entry[i] for i in range(len(entry_cols))})

        except sqlite3.OperationalError as msg:
            print('GetMatchEntries %s' % msg)
            entries = {}
        connection.close()
        return entries 

    def GetAllHunterData(self,timestamp):
        connection = sqlite3.connect(db)
        cursor = connection.cursor();
        query = "select * from 'hunter' where timestamp is %s" % timestamp
        allhunters = []
        try:
            cursor.execute(query)
            hunter_cols = [desc[0] for desc in cursor.description]
            hunter_stats = cursor.fetchall()
            if hunter_stats is None:
                connection.close()
                return []
            for hunter in hunter_stats:
                allhunters.append({hunter_cols[i] : hunter[i] for i in range(len(hunter_cols))})
            return allhunters
        except sqlite3.OperationalError as msg:
            print('hunter error %s' % msg)
        connection.close()
        return allhunters

    def GetMatchTeams(self, timestamp):
        connection = sqlite3.connect(db)
        cursor = connection.cursor();
        query = "select * from 'team' where timestamp is %s" % timestamp
        try:
            cursor.execute(query)
            team_stats = cursor.fetchall()
            if team_stats is None:
                return {}
            teams = []
            team_cols = [desc[0] for desc in cursor.description]
            for team in team_stats:
                teams.append({team_cols[i] : team[i] for i in range(len(team_cols))})

        except sqlite3.OperationalError as msg:
            print('GetMatchTeams %s' % msg)
            teams = {}
        connection.close()
        return teams 

    def GetMyDeaths(self, timestamp):
        connection = sqlite3.connect(db)
        cursor = connection.cursor();
        query = "select sum(downedme+killedme) from 'hunter' where timestamp is %d" % timestamp
        try:
            cursor.execute(query)
            deaths = cursor.fetchone()[0]
        except sqlite3.OperationalError as msg:
            print(msg)
            deaths = -1
        connection.close()
        return deaths if deaths != None else 0

    def GetMyKills(self, timestamp):
        connection = sqlite3.connect(db)
        cursor = connection.cursor();
        query = "select sum(downedbyme+killedbyme) from 'hunter' where timestamp is %d" % timestamp
        try:
            cursor.execute(query)
            kills = cursor.fetchone()[0]
        except sqlite3.OperationalError as msg:
            print(msg)
            kills = -1
        connection.close()
        return kills if kills != None else 0

    def GetMatchKills(self, timestamp):
        connection = sqlite3.connect(db)
        cursor = connection.cursor();
        query = "select sum(amount) from 'entry' where category is 'accolade_players_killed' and timestamp is %d" % timestamp
        try:
            cursor.execute(query)
            kills = cursor.fetchone()[0]
        except sqlite3.OperationalError as msg:
            print(msg)
            kills = -1
        connection.close()
        return kills if kills != None else 0


    def GetAllTimestamps(self):
        connection = sqlite3.connect(db)
        cursor = connection.cursor();
        query = "select timestamp from 'game' order by timestamp desc"
        try:
            cursor.execute(query)
            timestamps = [x[0] for x in cursor.fetchall()]
        except sqlite3.OperationalError as msg:
            print(msg)
            timestamps = []
        connection.close()
        return timestamps

    def IsQuickPlay(self, timestamp):
        connection = sqlite3.connect(db)
        cursor = connection.cursor()
        query = "select MissionBagIsQuickPlay from 'game' where timestamp is %s" % timestamp
        try:
            cursor.execute(query)
            qp = cursor.fetchone()[0]
        except sqlite3.OperationalError as msg:
            print('isquickplay error')
            print(msg)
            qp = -1
        connection.close()
        return qp
