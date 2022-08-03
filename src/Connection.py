import json
import Client
import time
import os
import sqlite3
from datetime import datetime
from PyQt6.QtCore import QObject, pyqtSignal
from resources import *

#db = os.path.join(QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppDataLocation),'huntstats.db')
killall = False

def insert_row(table, row,id):
    row['id'] = id
    connection = sqlite3.connect(db)
    cursor = connection.cursor();
    
    columns = [i for i in row.keys()]
    values = [row[i] for i in columns]

    query = "insert or ignore into %s (%s) values (%s)" % (table,','.join(columns), ('?,'*len(columns))[:-1])
    try:
        cursor.execute(query, (values))
        #cursor.executemany(query,(values))
        #log('success.')

    except sqlite3.OperationalError as msg:
        log('operational error\n%s' % str(msg))
        log('query: %s' % query)
        if 'has no column' in str(msg):
            column = str(msg).split(' ')[-1]
            row.pop(column)
            insert_row(table,row,id)
        elif 'syntax error' in str(msg):
            problem = str(msg).split("\"")[1]
            for key in row:
                if problem in key:
                    row.pop(key)
                    break
            insert_row(table,row,id)
            log('everything is fixed, we\'re good.')
    except sqlite3.IntegrityError as msg:
        log('integrity error\n%s'%str(msg))
    connection.commit()
    connection.close()

def syncDb():
    log('syncing db')
    files = getLocalFiles()
    for file in files:
        ts = file.split('attributes_')[1].split('.')[0]
        print(ts)
        exists = execute_query("select timestamp from 'game' where timestamp is %s" % ts) 
        if exists is None or exists == []:
            try:
                write_json_to_sql(file)
            except:
                'wrong format'
                continue
def write_json_to_sql(file):
    log('writing rows to database')
    with open(file,'r') as f:
        data = json.load(f)
    id = data["id"]
    teams = data.pop("teams")
    hunters = data.pop("hunters")
    entries = data.pop("entries")
    game = data.pop("game")

    for n in teams:
        team = teams[n]
        insert_row("team",team,id)
    for n in hunters:
        hunter = hunters[n]
        insert_row("hunter",hunter,id)

    for n in entries:
        entry = entries[n]
        insert_row("entry",entry,id)
    insert_row("game",game,id)

    log('writing rows to database from %s' % file)

def newest_file():
    t = -1
    prev = None
    for root, directories,files in os.walk(jsondir):
        for f in files:
            if os.stat(os.path.join(root,f)).st_mtime > t:
                t = os.stat(os.path.join(root,f)).st_mtime
                prev = os.path.join(root,f)
    return prev

def get_files():
    allfiles = []
    for root, directories,files in os.walk(jsondir):
        for file in files:
            allfiles.append(os.path.join(root,file))
    return allfiles

def GetLatestMmr(profileid):
    connection = sqlite3.connect(db)
    cursor = connection.cursor();
    query = "select max(timestamp) from 'game'"
    try:
        cursor.execute(query)
        ts = cursor.fetchone()[0]
        return GetMmr(ts,profileid)
    except Exception as msg:
        log("Connection.GetLatestMmr()")
        log(str(msg))

def GetMmr(timestamp,profileid):
    connection = sqlite3.connect(db)
    cursor = connection.cursor();
    query = "select mmr from 'hunter' where timestamp is %s and profileid is '%s'" % (str(timestamp),str(profileid))
    try:
        cursor.execute(query)
        mmr = cursor.fetchone()
        mmr = 0 if mmr is None else mmr[0]
    except sqlite3.OperationalError as msg:
        log('Connection.SetOwnMMR()')
        mmr = 0 
    connection.commit()
    connection.close()
    return mmr

def GetBestMmr(pid):
    connection = sqlite3.connect(db)
    cursor = connection.cursor();
    query = "select max(mmr) from 'hunter' where profileid is '%s'" % pid
    try:
        cursor.execute(query)
        mmr = cursor.fetchone()
        mmr = 0 if mmr is None else mmr[0]
    except sqlite3.OperationalError as msg:
        log(msg)
        mmr = 0
    connection.commit()
    connection.close()
    return mmr

def GetMyDeaths(timestamp):
    connection = sqlite3.connect(db)
    cursor = connection.cursor();
    query = "select sum(downedme+killedme) from 'hunter' where timestamp is %d" % timestamp
    try:
        cursor.execute(query)
        deaths = cursor.fetchone()[0]
    except sqlite3.OperationalError as msg:
        log(msg)
        deaths = -1
    connection.close()
    return deaths if deaths != None else 0

def GetMyKills(timestamp):
    connection = sqlite3.connect(db)
    cursor = connection.cursor();
    query = "select sum(downedbyme+killedbyme) from 'hunter' where timestamp is %d" % timestamp
    try:
        cursor.execute(query)
        kills = cursor.fetchone()[0]
    except sqlite3.OperationalError as msg:
        log(msg)
        kills = -1
    connection.close()
    return kills if kills != None else 0
def TopNHunters(n):
    connection = sqlite3.connect(db)
    cursor = connection.cursor();
    query = "select blood_line_name, sum(ispartner), sum(downedme), sum(downedbyme),sum(killedme),sum(killedbyme), count(profileid) as N, profileid from 'hunter' where profileid is not %d group by profileid order by N desc limit %d" % (int(settings.value('profileid','-1')), n)
    cols = ['blood_line_name','ispartner','downedme','downedbyme','killedme','killedbyme','count','profileid']
    try:
        cursor.execute(query)
        vals = cursor.fetchall()
        results = []
        if vals != None:
            for v in vals:
                results.append(
                    {cols[i] : v[i] for i in range(len(cols))}
                )

    except sqlite3.OperationalError as msg:
        log("Connection.TopNHunters()")
        log(msg)
        results = []
    connection.close()
    return results

def GetTopKiller():
    connection = sqlite3.connect(db)
    cursor = connection.cursor();
    query = "select blood_line_name, sum(downedme+killedme) as kills from 'hunter' group by profileid order by kills desc limit 1"
    cols = ['blood_line_name','kills']
    try:
        cursor.execute(query)
        vals = cursor.fetchone()
        if vals != None:
            result = { cols[i] : vals[i] for i in range(len(cols))}
        else:
            result = {}
    except sqlite3.OperationalError as msg:
        log("GetTopKiller()")
        log(msg)
        result = {}
    connection.close()
    return result

def GetTopKilled():
    connection = sqlite3.connect(db)
    cursor = connection.cursor();
    query = "select blood_line_name, sum(downedbyme+killedbyme) as kills from 'hunter' group by profileid order by kills desc limit 1"
    cols = ['blood_line_name','kills']
    try:
        cursor.execute(query)
        vals = cursor.fetchone()
        if vals != None:
            result = { cols[i] : vals[i] for i in range(len(cols))}
        else:
            result = {}
    except sqlite3.OperationalError as msg:
        log("GetTopKiller()")
        log(msg)
        result = {}
    connection.close()
    return result
def execute_query(query):
    connection = sqlite3.connect(db)
    cursor = connection.cursor();
    try:
        cursor.execute(query)
        result = cursor.fetchall()
    except sqlite3.OperationalError as msg:
        log(query)
        log(msg)
        result = None
    connection.close()
    return result

def GetHunt(timestamp):
    gVals = execute_query("select * from 'game' where timestamp is %s" % timestamp)[0]
    gCols = execute_query("pragma table_info('game')")
    return { gCols[i][1] : gVals[i] for i in range(len(gCols)) }

def GetEntries(timestamp):
    eVals = execute_query("select * from 'entry' where timestamp is %s" % timestamp) 
    eCols = execute_query("pragma table_info('entry')")
    entries = []
    for entry in eVals:
        entries.append({eCols[i][1] : entry[i] for i in range(len(eCols))})
    return entries

def GetTeams(timestamp):
    tVals = execute_query("select * from 'team' where timestamp is %s" % timestamp)
    tCols = execute_query("pragma table_info('team')")
    teams = []
    for team in tVals:
        teams.append({tCols[i][1] : team[i] for i in range(len(tCols))})
    return teams

def GetHunters(timestamp):
    hVals = execute_query("select * from 'hunter' where timestamp is %s" % timestamp)
    hCols = execute_query("pragma table_info('hunter')")
    hunters = []
    for hunter in hVals:
        hunters.append({hCols[i][1] : hunter[i] for i in range(len(hCols))})
    return hunters

def GetHunter(name,ts):
    hVals = execute_query("select * from 'hunter' where blood_line_name is '%s' and timestamp is '%s'" % (name,ts))[0]
    hCols = execute_query("pragma table_info('hunter')")
    hunter = { hCols[i][1] : hVals[i] for i in range(len(hCols))}
    return hunter


def tables_exist(db):
    connection = sqlite3.connect(db)
    cursor = connection.cursor()
    query = "select name from sqlite_master where type = 'table' and name = ? or name = ? or name = ? or name = ?"
    tables = ('game','hunter','entry','team',)
    try:
        cursor.execute(query,tables)
        result = True if len(cursor.fetchall()) == 4 else False
    except sqlite3.OperationalError as msg:
        log('tables_exist()')
        log(msg)
        result = False
    connection.close()
    return result

def create_tables(db,schemafile):
    if tables_exist(db):    return
    log('creating tables')
    connection = sqlite3.connect(db)
    cursor = connection.cursor()
    cursor.executescript(open(schemafile,'r').read())
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
        print('connection.init')
        evnt_exists = execute_query("select count(*) from pragma_table_info('game') where name='EventPoints'")
        if evnt_exists == None or evnt_exists[0][0] == 0:
            execute_query("alter table 'game'  add column 'EventPoints' integer")

        self.current_files = get_files()

        '''
        # if file hasn't been written to database, write file.
        for file in self.current_files:
            print(file)
            timestamp = file[file.index('attributes'):].split('_')[1].split('.')[0]
            exists = self.execute_query("select timestamp from 'game' where timestamp = '%s'" % timestamp)
            if exists == []:
                print('writing %s to database' % timestamp)
                self.write_json_to_sql(os.path.join(jsondir,file),log=False)
        '''

    def file_added(self):
        current_files = get_files()
        if len(current_files) > len(self.current_files):
            self.current_files = current_files
            log('file added: %d' % len(self.current_files))
            return True
        return False

    def run(self):
        log("connection.run")
        global killall
        while(True):
            time.sleep(1)
            if(self.file_added()):
                f = newest_file()
                write_json_to_sql(f)
                self.progress.emit("done")
                Client.sendToS3(os.path.join(app_data_path,f))
            if killall:
                self.finished.emit()
                break

    def iNumTimesSeen(self,profileid):
        connection = sqlite3.connect(db)
        cursor = connection.cursor();
        query = "select count(*) from 'hunter' where profileid is ?"
        try:
            cursor.execute(query,(profileid,))
            n = cursor.fetchone()[0]
        except sqlite3.OperationalError as msg:
            log(msg)
            n = -1
        connection.close()
        return n;






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
        except sqlite3.OperationalError as msg:
            log(msg)
        connection.commit()
        connection.close()


    def igetNTeams(self,timestamp):
        connection = sqlite3.connect(db)
        cursor = connection.cursor();
        query = "select MissionBagNumTeams from 'game' where timestamp is %s" % timestamp;
        try:
            cursor.execute(query)
            numteams = int(cursor.fetchone()[0])
            if numteams is None:
                numteams = 0
        except sqlite3.OperationalError as msg:
            log(msg)
            numteams = 0
        connection.close()
        return numteams

    def iGetProfileId(self,name):
        connection = sqlite3.connect(db)
        cursor = connection.cursor();
        query = "select profileid from 'hunter' where blood_line_name is ?"
        try:
            cursor.execute(query,(name,))
            id = cursor.fetchone()
            id = id[0] if id != None else -1 
        except sqlite3.OperationalError as msg:
            log('Connection.GetProfileId()')
            log(msg)
            id = -1
        connection.close()
        return id

    
    def iGetTotalHuntCount(self):
        connection = sqlite3.connect(db)
        cursor = connection.cursor();
        query = "select count(timestamp) from 'game'"
        try:
            cursor.execute(query)
            huntcount = cursor.fetchone()[0]
        except sqlite3.OperationalError as msg:
            log(msg)
            huntcount = -1
        connection.close()
        if huntcount is None:
            huntcount = 0
        self.settings.setValue('total_hunts',huntcount)
        return huntcount

    def iSetTotalKills(self):
        connection = sqlite3.connect(db)
        cursor = connection.cursor()
        query = "select sum(downedbyme + killedbyme) from 'hunter' where (downedbyme > 0 or killedbyme > 0)"
        try:
            cursor.execute(query)
            kills = cursor.fetchone()[0]
        except sqlite3.OperationalError as msg:
            log('SetTotalKills() %s' % msg)
            kills = -1
        if kills is None:
            kills = 0
        self.settings.setValue('total_kills',kills)
    
    def iSetTotalDeaths(self):
        connection = sqlite3.connect(db)
        cursor = connection.cursor()
        query = "select sum(downedme + killedme) from 'hunter' where (downedme > 0 or killedme > 0)"
        try:
            cursor.execute(query)
            deaths = cursor.fetchone()[0]
        except sqlite3.OperationalError as msg:
            log('SetMyTotalDeaths %s' % msg)
            deaths = -1
        if deaths is None:
            deaths = 0
        self.settings.setValue('total_deaths',deaths)
    
    def iSetTotalAssists(self):
        connection = sqlite3.connect(db)
        cursor = connection.cursor()
        query = "select sum(amount) from 'entry' where category is 'accolade_players_killed_assist'"
        try:
            cursor.execute(query)
            assists = cursor.fetchone()[0]
        except sqlite3.OperationalError as msg:
            log('SetMyTotalAssists %s' % msg)
            assists = -1
        if assists is None:
            assists = 0
        self.settings.setValue('total_assists',assists)

    def iSetKDA(self):
        connection = sqlite3.connect(db)
        cursor = connection.cursor()
        self.SetTotalKills()
        self.SetTotalDeaths()
        self.SetTotalAssists()
        kills = int(self.settings.value('total_kills',-1))
        deaths = int(self.settings.value('total_deaths',-1))
        assists = int(self.settings.value('total_assists',-1))
        kda = -1.0
        if deaths == 0:
            kda = 0
        else:
            kda = (kills + assists) / deaths
        self.settings.setValue('kda',round(kda,4))

    def iSurvived(self, timestamp):
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

    def iGetMatchData(self, timestamp):
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

    def iGetHunterData(self, name, timestamp):
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

    def iGetMatchEntries(self, timestamp):
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

    def iGetAllHunterData(self,timestamp):
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

    def iGetMatchTeams(self, timestamp):
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


    def iGetMatchKills(self, timestamp):
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


    def iGetAllTimestamps(self):
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

    def iIsQuickPlay(self, timestamp):
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
