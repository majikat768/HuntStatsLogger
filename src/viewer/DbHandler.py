from PyQt6.QtCore import QObject,pyqtSignal
import time
import sqlite3
import os
from resources import *

running = False

class DbHandler(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(object)

    def __init__(self):
        super().__init__()

        if not tables_exist():
            create_tables()
        self.current_files = get_files()

    def repair_files(self):
        for root,dirs,files in os.walk(jsondir):
            for f in files:
                if '.json' in f:
                    print(f)
                    with open(os.path.join(root,f),'r') as fp:
                        data = json.load(fp)
                    id = generate_checksum(data)
                    data["id"] = id
                    print(id)
                    with open(os.path.join(root,f),'w') as fp:
                        json.dump(data,fp)
                    
        exit()

    def run(self):
        while True:
            if self.file_added():
                log('file added %d' % len(self.current_files))
                f = newest_file()
                self.write_json_to_db(f)
                self.progress.emit("done")
                if settings.value("profileid","-1") == "-1":
                    if settings.value("steam_name"):
                        settings.setValue('profileid',getProfileid(settings.value("steam_name")))

            time.sleep(1)
            if not running:
                print('stopped db handler')
                self.finished.emit()
                break

    def syncDb(self):
        log('syncing database')
        if not tables_exist():
            create_tables()
        files = get_files()
        i = 0
        for f in files:
            i += 1
            self.progress.emit("syncing file %d of %d" % (i, len(files)))
            if '.json' in f:
                ts = f.split("attributes_")[1].split(".json")[0]
                res = execute_query("select timestamp from 'game' where timestamp is %s" % ts)
                if len(res) == 0:
                    self.write_json_to_db(f)

        log('done')
        self.finished.emit()

    def write_json_to_db(self,file):
        log('writing file to db')
        timestamp = file.split("attributes_")[1].split('json')[0]
        with open(file,'r') as f:
            data = json.load(f)
        log('done')

        try:
            data = clean_data(data)
        except:
            data = data
        with open(file,'w') as f:
            json.dump(data,f)
        teams = data.pop("teams")
        entries = data.pop("entries")
        hunters = data.pop("hunters")
        game = data.pop("game")

        conn = sqlite3.connect(db)
        for n in teams:
            self.insert_row(conn,"team",teams[n],timestamp)
        for n in entries:
            self.insert_row(conn,"entry",entries[n],timestamp)
        for n in hunters:
            self.insert_row(conn,"hunter",hunters[n],timestamp)
        self.insert_row(conn,"game",game,timestamp)
        conn.close()

    def insert_row(self,conn, table,row,timestamp):
        row["timestamp"] = timestamp
        cursor = conn.cursor()
        cols = [i for i in row.keys()]
        vals = [row[i] for i in cols]
        query = "insert or ignore into %s (%s) values (%s)" % (table,','.join(cols), (','.join(['?']*len(cols))))
        try:
            cursor.execute(query,(vals))
        except Exception as msg:
            log('insert row')
            log(msg)
            log('query:%s' % query)
            if 'has no column' in str(msg):
                column = str(msg).split(' ')[-1]
                row.pop(column)
                self.insert_row(conn, table,row,timestamp)
            elif 'syntax error' in str(msg):
                problem = str(msg).split("\"")[1]
                for key in row:
                    if problem in key:
                        row.pop(key)
                        break
                self.insert_row(conn, table,row,timestamp)
        conn.commit()



    def file_added(self):
        current_files = get_files()
        if len(current_files) > len(self.current_files):
            self.current_files = current_files
            return True
        return False

def getHuntCount():
    n = execute_query("select count(timestamp) from 'game'")
    n = 0 if n == None else n[0][0]
    return n

def execute_query(query):
    conn = sqlite3.connect(db)
    cursor = conn.cursor()
    try:
        cursor.execute(query)
        return cursor.fetchall()
    except Exception as msg:
        log(msg)
        return []

def get_files():
    allfiles = []
    for root,dirs,files in os.walk(jsondir):
        for file in files:
            allfiles.append(os.path.join(root,file))
    return allfiles

def newest_file():
    t = -1
    prev = None
    for root,dirs,files in os.walk(jsondir):
        for f in files:
            if os.stat(os.path.join(root,f)).st_mtime > t:
               prev = os.path.join(root,f)
               t = os.stat(prev).st_mtime
    return prev

def record_exists(timestamp):
    pass

def isQuickPlay(timestamp):
    qp = execute_query("select MissionBagIsQuickPlay from 'game' where timestamp is %d" % timestamp)
    return qp[0][0]

def GetTeams(timestamp):
    tVals = execute_query("select * from 'team' where timestamp is %s" % timestamp)
    tCols = execute_query("pragma table_info('team')")
    teams = []
    for team in tVals:
        teams.append({tCols[i][1] : team[i] for i in range(len(tCols))})
    return teams

def GetHunter(name,ts):
    hVals = execute_query("select * from 'hunter' where blood_line_name is '%s' and timestamp is '%s'" % (name,ts))[0]
    hCols = execute_query("pragma table_info('hunter')")
    hunter = { hCols[i][1] : hVals[i] for i in range(len(hCols))}
    return hunter

def GetHunters(timestamp):
    hVals = execute_query("select * from 'hunter' where timestamp is %s" % timestamp)
    hCols = execute_query("pragma table_info('hunter')")
    hunters = []
    for hunter in hVals:
        hunters.append({hCols[i][1] : hunter[i] for i in range(len(hCols))})
    return hunters

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

def getTeamKills(timestamp):
    teamKills = execute_query("select sum(amount) from 'entry' where category is 'accolade_players_killed' and timestamp is %d" % timestamp)[0][0]
    if teamKills is None:   return 0
    return teamKills

def getProfileid(name):
    pid = execute_query("select profileid from 'hunter' where blood_line_name is '%s' limit 1" % name)
    if len(pid) > 0:
        return -1 if pid[0][0] == None else pid[0][0]
    else:
        return -1

def GetMmr(pid):
    if int(pid) < 0: return 0
    mmr = execute_query("select mmr from 'hunter' where profileid is %s order by timestamp desc limit 1" % pid)
    if len(mmr) > 0:
        return 0 if mmr[0][0] == None else mmr[0][0]
    else:
        return 0

def GetMaxMmr(pid):
    if int(pid) < 0: return 0
    mmr = execute_query("select max(mmr) from 'hunter' where profileid is %s limit 1" % pid)
    if len(mmr) > 0:
        return 0 if mmr[0][0] == None else mmr[0][0]
    else:
        return 0

def tables_exist():
    conn = sqlite3.connect(db)
    cursor = conn.cursor()
    query = "select name from sqlite_master where type = 'table' and name = ? or name = ? or name = ? or name = ?"
    tables = ('game','hunter','entry','team',)
    try:
        cursor.execute(query,tables)
        nTables = len(cursor.fetchall())
        conn.close()
        return nTables == len(tables)
    except Exception as msg:
        log("tables_exist")
        log(msg)
        conn.close()
        return False

def create_tables():
    if tables_exist():  return
    conn = sqlite3.connect(db)
    cursor = conn.cursor()
    cursor.executescript(open(resource_path('assets/schema.sql'),'r').read())
    conn.close()

def GetHunt(ts):
    vals = execute_query("select * from 'game' where timestamp is %d" % ts)[0]
    cols = execute_query("pragma table_info('game')")
    return { cols[i][1] : vals[i] for i in range(len(cols))}

def GetEntries(timestamp):
    vals = execute_query("select * from 'entry' where timestamp is %s" % timestamp) 
    cols = execute_query("pragma table_info('entry')")

    return [ { cols[i][1] : entry[i] for i in range(len(cols)) } for entry in vals]

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
    query = "select blood_line_name, mmr, sum(ispartner), sum(downedme), sum(downedbyme),sum(killedme),sum(killedbyme), count(profileid) as N, profileid from 'hunter' where profileid is not %d group by profileid order by N desc limit %d" % (int(settings.value('profileid','-1')), n)
    cols = ['blood_line_name','mmr','ispartner','downedme','downedbyme','killedme','killedbyme','count','profileid']
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