import sqlite3
from resources import *

def tables_exist():
    conn = sqlite3.connect(database)
    cursor = conn.cursor()
    tables = ('games','hunters','entries','teams','accolades','timestamps')
    query = "select name from sqlite_master where type = 'table' and %s" % (" or ".join(["name = ?"] * len(tables)))

    try:
        cursor.execute(query,tables)
        nTables = len(cursor.fetchall())
        conn.close()
        return nTables == len(tables)
    except Exception as e:
        log('tables_exist err')
        log(e)
        conn.close()
        return False

def create_tables():
    log('creating tables')
    conn = sqlite3.connect(database)
    cursor = conn.cursor()
    cursor.executescript(open(resource_path('assets/schema.sql'),'r').read())
    conn.close()


def record_exists(id):
    conn = sqlite3.connect(database)
    cursor = conn.cursor()
    query = "select count(*) from 'games' where game_id is ?"
    res = True
    try:
        cursor.execute(query,[id])
        res = cursor.fetchone() == (1,)
        conn.close()
    except Exception as e:
        log(e)
        conn.close()
    return res

def execute_query(*args):
    query = args[0]
    conn = sqlite3.connect(database)
    cursor = conn.cursor()
    try:
        cursor.execute(query,args[1:])
        return cursor.fetchall()
    except Exception as e:
        log('execute_query err')
        log('requested query: %s' % query)
        log(e)
        return []

def json_to_db(obj):
    log('inserting record into database')
    teams = obj['teams']
    hunters = obj['hunters']
    entries = obj['entries']
    game = obj['game']
    accolades = obj['accolades']
    timestamps = obj['timestamps']

    conn = sqlite3.connect(database)
    for teamnum in teams:
        insert_row(conn, "teams", teams[teamnum])
    for hunternum in hunters:
        insert_row(conn, "hunters", hunters[hunternum])
    for entrynum in entries:
        insert_row(conn, "entries", entries[entrynum])
    for accoladenum in accolades:
        insert_row(conn, "accolades", accolades[accoladenum])
    for timestampnum in timestamps:
        insert_row(conn, "timestamps", timestamps[timestampnum])
    insert_row(conn, 'games', game)
    conn.close()



def add_column(table, column):
    conn = sqlite3.connect(database)
    cursor = conn.cursor()
    query = "alter table %s add column %s" % (table,column)
    log(query)
    try:
        cursor.execute(query)
        conn.commit()
    except Exception as e:
        print('add_column')
        print(e)

def insert_row(conn, table, row):
    cursor = conn.cursor()
    cols = [i for i in row.keys()]
    vals = [row[i] for i in cols]
    query = "insert or ignore into %s (%s) values (%s) " % (table, ','.join(cols), (','.join(['?']*len(cols))))
    try:
        cursor.execute(query, (vals))
        conn.commit()
    except Exception as e:
        if 'syntax error' in str(e):
            print('insert_row')
            print(e)
            problem = str(e).split("\"")[1]
            for key in row:
                if problem in key:
                    row.pop(key)
                    break
            print('\tsyntax error repaired')
            insert_row(conn, table,row)
        elif 'has no column' in str(e):
            if 'MissionBagWasDeathlessUsed' in str(e):
                add_column('games','MissionBagWasDeathlessUsed')
                insert_row(conn, table,row)
            elif 'MissionBagAddNoBloodlineXp' in str(e):
                add_column('games','MissionBagAddNoBloodlineXp')
                insert_row(conn, table, row)
            elif 'MissionBagIsTutorial' in str(e):
                add_column('games','MissionBagIsTutorial')
                insert_row(conn, table, row)
            else:
                log(e)
                log('insert_row; has no column')
        else:
            log(e)
            log('insert_row')

def get_new_mmr():
        newMmr = execute_query("select mmr from 'hunters' where profileid is ? order by timestamp desc limit 1", settings.value("profileid"))
        if len(newMmr) > 0:
            return newMmr[0][0]
        return 0
def get_best_mmr():
        bestMmr = execute_query("select mmr from 'hunters' where profileid is ? order by mmr desc limit 1", settings.value("profileid"))
        if len(bestMmr) > 0:
            return bestMmr[0][0]
        return 0

def get_bounty_data(id):
    pass

def get_kills_data(game_id):
    cols = [
        'mykill',
        'mydeath',
        'teamkill',
        'teamdeath',
        'mmr'
    ]
    query = "select\
        h.downedbyme+h.killedbyme as mykill,\
        h.downedme+h.killedme as mydeath,\
        h.downedbyteammate+h.killedbyteammate as teamkill,\
        h.downedteammate+h.killedteammate as teamdeath,\
        h.mmr\
        from 'hunters' h where (mykill > 0 or mydeath > 0 or teamkill > 0 or teamdeath > 0) and h.game_id = ?"
    vals = execute_query(query,game_id)
    return [
        { cols[i] : v[i] for i in range(len(cols)) } for v in vals
    ]

def get_hunt_timeline(game_id):
    cols = [
        "timestamp",
        "event",
        "blood_line_name"
    ]
    query = "select\
            t.timestamp,\
            t.event,\
            h.blood_line_name\
            from 'timestamps' t\
            inner join 'hunters' h on h.team_num || '_' || h.hunter_num = t.hunter\
            where t.game_id = ? and h.game_id = ?\
            order by t.timestamp asc"
    vals = execute_query(query,game_id,game_id)
    return [ { cols[i] : v[i] for i in range(len(cols))} for v in vals ]

def get_assists_data(game_id):
    query = "select e.amount from 'entries' e where e.category = 'accolade_players_killed_assist' and e.game_id = ?";
    amt = execute_query(query,game_id)
    return 0 if len(amt) == 0 else amt[0][0]

def get_n_hunts(n=-1):
    if n < 0:
        n = execute_query("select count(*) from 'games'")
        if len(n) == 0:
            n = 0
        else:
            n = n[0][0]
    if n <= 0:
        return []
    vals = execute_query("select\
                          g.game_id,\
                          g.MissionBagIsHunterDead as extracted,\
                          g.timestamp as timestamp,\
                          g.MissionBagIsQuickPlay as gametype,\
                          sum(h.killedbyme+h.downedbyme) as kills,\
                          sum(h.killedme+h.downedme) as deaths,\
                          sum(h.killedbyme+h.downedbyme+h.killedbyteammate+h.downedbyteammate) as team_kills,\
                          sum(h.killedme+h.downedme+h.killedteammate+h.downedteammate) as team_deaths,\
                          e.amount as assists\
                          from 'games' g\
                          join 'hunters' h on g.game_id = h.game_id\
                          left join 'entries' e on g.game_id = e.game_id and (e.amount is null or e.category = 'accolade_players_killed_assist')\
                          group by g.game_id order by g.timestamp desc limit %d" % n)
    cols = ["game_id", "extracted","timestamp","game_type","kills","deaths","team_kills","team_deaths", "assists"]
    return [ { cols[i] : hunt[i] for i in range(len(cols)) } for hunt in vals]
 
def get_team_data(game_id):
    vals = execute_query("select * from 'teams' t where t.game_id = ?",game_id)
    cols = execute_query("pragma table_info('teams')")
    return [{cols[i][1] : v[i] for i in range(len(cols))} for v in vals]

def get_hunters_data(game_id):
    vals = execute_query("select * from 'hunters' t where t.game_id = ?",game_id)
    cols = execute_query("pragma table_info('hunters')")
    return [{cols[i][1] : v[i] for i in range(len(cols))} for v in vals]

def get_bounty_data(game_id):
    cols = [
        "game_id",
        "timestamp",
        "butcher",
        "spider",
        "assassin",
        "scrapbeak",
        "IsQuickPlay",
        "IsHunterDead"
        ]
    vals = execute_query("select\
                         game_id,\
                         timestamp,\
                         MissionBagBoss_0,MissionBagBoss_1,MissionBagBoss_2,MissionBagBoss_3,\
                         MissionBagIsQuickPlay,MissionBagIsHunterDead\
                         from 'games' g where g.game_id = ?",game_id)

    return { cols[i] : vals[0][i] for i in range(len(cols))}

def get_pid_from_bloodlinename(blood_line_name):
    id = execute_query("select profileid from 'hunters' where blood_line_name = ? limit 1", blood_line_name)
    if len(id) == 0:
        return -1
    return id[0][0]

def get_entries(game_id):
    vals = execute_query("select * from 'entries' e where e.game_id = ?", game_id)
    cols = execute_query("pragma table_info('entries')")
    return [ { cols[i][1] : entry[i] for i in range(len(cols))} for entry in vals ]

def get_hunter_encounters(profileid):
    return execute_query("select count(*) from 'hunters' where profileid = ?",profileid)

def get_my_team_data(profileids):
    if len(profileids) < 1:
        return
    query = "select h0.game_id, h0.timestamp, h0.blood_line_name, h0.mmr, h0.bountyextracted, h0.teamextraction"
    if len(profileids) > 1:
        query += ",h1.blood_line_name,h1.mmr,h1.bountyextracted,h1.teamextraction"
    if len(profileids) == 3:
        query += ",h2.blood_line_name,h2.mmr,h2.bountyextracted,h2.teamextraction"
    query += ",t.mmr as team_mmr"
    query += " from 'hunters' h0"
    if len(profileids) > 1:
        query += " join 'hunters' h1 on h0.game_id = h1.game_id and h0.team_num = h1.team_num"
    if len(profileids) == 3:
        query += " join 'hunters' h2 on h0.game_id = h2.game_id and h0.team_num = h2.team_num"
    query += " join 'teams' t on h0.team_num = t.team_num and h0.game_id = t.game_id"
    query += " where h0.profileid = ?"
    if len(profileids) > 1:
        query += " and h1.profileid = ?"
    if len(profileids) == 3:
        query += " and h2.profileid = ?"
    query += " order by h0.timestamp desc"

    cols = ["game_id","timestamp","p1_name","p1_mmr","p1_bountyextract","p1_teamextract"]
    if len(profileids) > 1:
        cols = cols + ["p2_name","p2_mmr","p2_bountyextract","p2_teamextract"]
    if len(profileids) == 3:
        cols = cols + ["p3_name","p3_mmr","p3_bountyextract","p3_teamextract"]
    cols += ["team_mmr"]

    vals = []
    if len(profileids) == 1:
        vals = execute_query(query,profileids[0])
    elif len(profileids) == 2:
        vals = execute_query(query,profileids[0],profileids[1])
    elif len(profileids) == 3:
        vals = execute_query(query,profileids[0],profileids[1],profileids[2])
    return [ { cols[i] : v[i] for i in range(len(cols))} for v in vals ]

def get_team_mmr_history():
    vals = execute_query("select t.timestamp, t.mmr from 'teams' t where t.ownteam = 'true' order by t.timestamp asc")
    cols = ["timestamp","mmr"]
    return [ { cols[i] : v[i] for i in range(len(cols))} for v in vals]

def get_mmr_history():
    vals = execute_query("select h.timestamp,\
                         h.mmr, g.MissionBagIsQuickPlay as isQp from 'hunters' h\
                         join 'games' g on h.game_id = g.game_id\
                         where h.profileid = ?\
                         order by h.timestamp asc",
                         settings.value("profileid",""))
    cols = ["timestamp","mmr","isQp"]
    return [ { cols[i] : v[i] for i in range(len(cols))} for v in vals ]

def get_new_mmr_record():
    vals = execute_query("select h.timestamp,\
                         h.mmr, g.MissionBagIsQuickPlay as isQp from 'hunters' h\
                         join 'games' g on h.game_id = g.game_id\
                         where h.profileid = ?\
                         order by h.timestamp desc limit 1",
                         settings.value("profileid",""))
    cols = ["timestamp","mmr","isQp"]
    return [ { cols[i] : v[i] for i in range(len(cols))} for v in vals ]

# thanks @Huakas
def predictNextMmr(currentMmr = None, currentTs = None):
    if not currentMmr:
        currentMmr = get_new_mmr()
    if not currentTs:
        currentTs = execute_query("select timestamp from 'games' order by timestamp desc limit 1")[0][0]
    predictedChange = 0
    your_kills = execute_query("select downedbyme+killedbyme,mmr from 'hunters' where timestamp is ? and (downedbyme > 0 or killedbyme > 0)" , currentTs)
    your_deaths = execute_query("select downedme+killedme,mmr from 'hunters' where timestamp is ? and (downedme > 0 or killedme > 0)" , currentTs)

    for hunter in your_kills:
        kills = hunter[0]
        mmr = hunter[1]
        mmrValue = min(15, (currentMmr - mmr) / 25)
        predictedChange += (15 - mmrValue) * kills
    for hunter in your_deaths:
        deaths = hunter[0]
        mmr = hunter[1]
        mmrValue = max(-15, (currentMmr - mmr) / 25)
        predictedChange += (-15 - mmrValue) * deaths

    return currentMmr + predictedChange


def GetHuntAccolades(id):
    vals = execute_query("select * from 'accolades' where game_id is ?" , id)
    cols = execute_query("pragma table_info('accolades')")
    try:
        return [ { cols[i][1] : entry[i] for i in range(len(cols)) } for entry in vals]

    except Exception as e:
        log('dbhandler.getaccolades')
        log(e)
        return {}

def get_id_from_timestamp(timestamp):
    id = execute_query("select game_id from 'games' where timestamp = ?",timestamp)
    if len(id) == 0:
        return -1
    return id[0][0]