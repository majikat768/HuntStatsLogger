import sqlite3
from datetime import datetime
from PyQt5.QtCore import QSettings 

settings = QSettings('majikat','HuntStats')

def MmrToStars(mmr):
    return 0 if mmr == -1 else 1 if mmr < 2000 else 2 if mmr < 2300 else 3 if mmr < 2600 else 4 if mmr < 2750 else 5 if mmr < 3000 else 6

def unix_to_datetime(timestamp):
    return datetime.fromtimestamp(timestamp).strftime('%H:%M %m/%d/%y')

class Connection():
    def __init__(self) -> None:
        self.db = 'huntstats.db'

    def SetOwnMMR(self):
        connection = sqlite3.connect(self.db)
        cursor = connection.cursor();
        query = "select mmr from 'hunter' where timestamp is (select max(timestamp) from 'hunter') and blood_line_name is '%s'" % (settings.value('hunterName',''))
        try:
            cursor.execute(query)
            mmr = cursor.fetchone()[0]
        except sqlite3.OperationalError as msg:
            print('get own mmr error')
            mmr = -1
        connection.close()
        settings.setValue('mmr',mmr)
    
    def SetTotalHuntCount(self):
        connection = sqlite3.connect(self.db)
        cursor = connection.cursor();
        query = "select count(timestamp) from 'game'"
        try:
            cursor.execute(query)
            huntcount = cursor.fetchone()[0]
        except sqlite3.OperationalError as msg:
            print(msg)
            huntcount = -1
        connection.close()
        settings.setValue('total_hunts',huntcount)

    def SetTotalKills(self):
        connection = sqlite3.connect(self.db)
        cursor = connection.cursor()
        query = "select sum(downedbyme + killedbyme) from 'hunter' where (downedbyme > 0 or killedbyme > 0)"
        try:
            cursor.execute(query)
            kills = cursor.fetchone()[0]
        except sqlite3.OperationalError as msg:
            print('SetMyTotalKills %s' % msg)
            kills = -1
        settings.setValue('total_kills',kills)
    
    def SetTotalDeaths(self):
        connection = sqlite3.connect(self.db)
        cursor = connection.cursor()
        query = "select sum(downedme + killedme) from 'hunter' where (downedme > 0 or killedme > 0)"
        try:
            cursor.execute(query)
            deaths = cursor.fetchone()[0]
        except sqlite3.OperationalError as msg:
            print('SetMyTotalDeaths %s' % msg)
            deaths = -1
        settings.setValue('total_deaths',deaths)
    
    def SetTotalAssists(self):
        connection = sqlite3.connect(self.db)
        cursor = connection.cursor()
        query = "select sum(amount) from 'entry' where category is 'accolade_players_killed_assist'"
        try:
            cursor.execute(query)
            assists = cursor.fetchone()[0]
        except sqlite3.OperationalError as msg:
            print('SetMyTotalAssists %s' % msg)
            assists = -1
        settings.setValue('total_assists',assists)

    def SetKDA(self):
        connection = sqlite3.connect(self.db)
        cursor = connection.cursor()
        killQuery = "select sum(downedbyme + killedbyme) from 'hunter' where (downedbyme > 0 or killedbyme > 0)"
        deathQuery = "select sum(downedme + killedme) from 'hunter' where (downedme > 0 or killedme > 0)"
        assistQuery = "select sum(amount) from 'entry' where category is 'accolade_players_killed_assist'"
        kda = -1.0
        try:
            cursor.execute(killQuery)
            kills = cursor.fetchone()[0]
            cursor.execute(deathQuery)
            deaths = cursor.fetchone()[0]
            cursor.execute(assistQuery)
            assists = cursor.fetchone()[0]
            kda = (kills + assists) / deaths
        except sqlite3.OperationalError as msg:
            print('SetMyTotalAssists %s' % msg)
        settings.setValue('kda',round(kda,3))

    def Survived(self, timestamp):
        connection = sqlite3.connect(self.db)
        cursor = connection.cursor();
        query = "select MissionBagIsHunterDead from 'game' where timestamp is %d" % timestamp
        try:
            cursor.execute(query)
            lived = cursor.fetchone()[0]
        except sqlite3.OperationalError as msg:
            print(msg)
            kills = -1
        connection.close()
        return lived if lived != None else -1

    def GetMatchData(self, timestamp):
        connection = sqlite3.connect(self.db)
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
            return {}

    def GetMatchEntries(self, timestamp):
        connection = sqlite3.connect(self.db)
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
            print('GetMatchData %s' % msg)
            entries = {}
        connection.close()
        return entries 

    def GetAllHunterData(self,timestamp):
        connection = sqlite3.connect(self.db)
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
        connection = sqlite3.connect(self.db)
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
            print('GetMatchData %s' % msg)
            teams = {}
        connection.close()
        return teams 

    def GetMatchKills(self, timestamp):
        connection = sqlite3.connect(self.db)
        cursor = connection.cursor();
        print('getting match kills %d' % timestamp)
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
        connection = sqlite3.connect(self.db)
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
        connection = sqlite3.connect(self.db)
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
