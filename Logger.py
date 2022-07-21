from PyQt5.QtCore import QObject,pyqtSignal
import os
import json
import time
import xmltodict
import sqlite3

killall = False
database = 'huntstats.db'

def tables_exist():
    connection = sqlite3.connect(database)
    cursor = connection.cursor();
    query = "SELECT count(*) FROM sqlite_master WHERE type = 'table'"
    cursor.execute(query)
    return cursor.fetchone()[0]

def tables_empty():
    connection = sqlite3.connect(database)
    cursor = connection.cursor();
    query = "select count(*) from 'game'"
    cursor.execute(query)
    return True if cursor.fetchone()[0] == 0 else False

def create_tables(data):
    print('creating tables')
    connection = sqlite3.connect('huntstats.db')
    cursor = connection.cursor()
    hunter_cols = {'timestamp':'integer', 'team_num':'integer', 'hunter_num':'integer'}
    game_cols = {'timestamp':'integer primary key'}
    team_cols = {'timestamp':'integer', 'team_num':'integer'}
    entry_cols = {'timestamp':'integer','entry_num':'integer'}

    game_dict = data['game']
    for k in game_dict.keys():
        t = type(game_dict[k])
        game_cols[k] = 'integer' if t is int else 'text'

    hunter_dict = data['hunter'][0][0]
    for k in hunter_dict.keys():
        t = type(hunter_dict[k])
        hunter_cols[k] = 'integer' if t is int else 'text'

    team_dict = data['team'][0]
    for k in team_dict.keys():
        t = type(team_dict[k])
        team_cols[k] = 'integer' if t is int else 'text'
    
    entry_dict = data['entry'][0]
    for k in entry_dict.keys():
        t = type(entry_dict[k])
        entry_cols[k] = 'integer' if t is int else 'text'

    team_cols['primary key'] = '(timestamp, team_num)'
    hunter_cols['primary key'] = '(timestamp, team_num, hunter_num)'
    entry_cols['primary key'] = '(timestamp, entry_num)'

    tables = {
        'game':game_cols,
        'team':team_cols,
        'hunter':hunter_cols,
        'entry':entry_cols
    }

    for title in tables:
        query = 'create table if not exists %s (' % title
        for key in tables[title]:
            query += '%s %s, ' % (key, tables[title][key])
        query = query[:-2]
        query += ')'
        cursor.execute(query)
    for title in tables:
        print(title)
        for c in cursor.execute('pragma table_info(%s)' % title):
            print(c)
        print()
    connection.close()

def diff(file1,file2):
    with open(file1,'r',encoding='unicode_escape') as f1:
        with open(file2,'r',encoding='unicode_escape') as f2:
            return f1.read() != f2.read()

def get_num_hunters(sql_rows, team_num):
    for i in sql_rows['team']:
        team = sql_rows['team'][i]
        if team['team_num'] == team_num:
            return team['numplayers']
    return -1

def file_changed(filepath,last_change):
    return os.stat(filepath).st_mtime != last_change

def parse_value(value):
    if value.isnumeric():
        return int(value)
    elif value == 'true' or value == 'false':
        return 1 if value == 'true' else 0
    else:
        return value

class Logger(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(str)
    xml_path = ''
    json_out_dir = os.path.join(os.getcwd(),'json')
    if not os.path.exists(json_out_dir):
        os.makedirs(json_out_dir)

    def __init__(self):
        QObject.__init__(self)


    def set_path(self,huntpath):
        suffix = 'user/profiles/default/attributes.xml' 
        self.xml_path = os.path.join(huntpath,suffix)
        print(self.xml_path)
        if not os.path.exists(self.xml_path):
            self.print('attributes.xml not found.')
            print('attributes.xml not found.')
            exit()

    def print(self,msg):
        print(msg)
        self.progress.emit(msg)


    def run(self):
        last_change = -1
        while True:
            if self.xml_path == '': continue

            if file_changed(self.xml_path,last_change):
                timestamp = int(os.stat(self.xml_path).st_mtime)

                json_outfile = os.path.join(self.json_out_dir,'attributes_'+str(timestamp)+'.json')
                json_outfile_wait = json_outfile + '.2'
                json_files = os.listdir(self.json_out_dir)

                sql_rows = self.build_json_from_xml()
                if not tables_exist():
                    create_tables(sql_rows)

                if len(os.listdir(self.json_out_dir)) == 0:
                    with open(json_outfile,'w',encoding='utf-8') as outfile:
                        json.dump(sql_rows,outfile,indent=True)
                        self.write_json_to_sql(sql_rows,timestamp)
                else:
                    prev_json = os.path.join(self.json_out_dir,max(json_files,key=lambda x : os.stat(os.path.join(self.json_out_dir,x)).st_mtime))
                    with open(json_outfile_wait,'w',encoding='utf-8') as outfile:
                        json.dump(sql_rows,outfile,indent=True)
                    if not diff(prev_json,json_outfile_wait):
                        os.remove(json_outfile_wait)
                    else:
                        os.replace(json_outfile_wait,json_outfile)
                        self.write_json_to_sql(sql_rows,timestamp)
                if tables_empty():
                    self.write_json_to_sql(sql_rows,timestamp)
                time.sleep(1)
                self.print(time.strftime('%m/%d %H:%M:%S\n') + ' waiting for changes....\n')

                last_change = os.stat(self.xml_path).st_mtime

            time.sleep(1)
            if killall: break

        self.finished.emit()

        
    def write_json_to_sql(self,sql_rows,timestamp):
        if not tables_exist():
            create_tables(sql_rows)
            self.print('tables created')
        self.print('writing rows to database')
        num_teams = sql_rows['game']['MissionBagNumTeams']
        num_entries = sql_rows['game']['MissionBagNumEntries']
        
        sql_rows['game']['timestamp'] = timestamp
        self.insert_row('game',sql_rows['game'])
        sql_rows['game'].pop('timestamp')

        for i in sql_rows['team']:
            team = sql_rows['team'][i]
            if team['team_num'] < num_teams:
                team['timestamp'] = timestamp
                self.insert_row('team',team)
                team.pop('timestamp')

        for i in sql_rows['entry']:
            entry = sql_rows['entry'][i]
            if entry['entry_num'] < num_entries:
                entry['timestamp'] = timestamp
                self.insert_row('entry',entry)
                entry.pop('timestamp')

        for i in sql_rows['hunter']:
            team = sql_rows['hunter'][i]
            for j in team:
                hunter = team[j]
                if hunter['team_num'] < num_teams and hunter['hunter_num'] < get_num_hunters(sql_rows,hunter['team_num']):
                    hunter['timestamp'] = timestamp
                    self.insert_row('hunter',hunter)
                    hunter.pop('timestamp')
        self.print('data written')

    def build_json_from_xml(self):
        self.print('building json object')
        sql_rows = {
                    'game' : {},
                    'hunter' : {},
                    'entry' : {},
                    'team' : {}
                }

        with open(self.xml_path,'r',encoding='utf-8') as xmlfile:
            for line in xmlfile:
                if "MissionBag" in line:
                    linedict = xmltodict.parse(line)
                    key = parse_value(linedict['Attr']['@name'])
                    value = parse_value(linedict['Attr']['@value'])
                    if value != '' and 'tooltip' not in key:
                        keysplit = key.split('_')
                        if 'MissionBagPlayer_' in key:
                            team_num = int(keysplit[1])
                            hunter_num = int(keysplit[2])
                            if team_num not in sql_rows['hunter'].keys():
                                sql_rows['hunter'][team_num] = {}
                            if hunter_num not in sql_rows['hunter'][team_num].keys():
                                sql_rows['hunter'][team_num][hunter_num] = {'team_num':team_num,'hunter_num':hunter_num}
                            category = '_'.join(keysplit[3:])
                            sql_rows['hunter'][team_num][hunter_num][category] = value
                        elif 'MissionBagTeam_' in key:
                            team_num = int(keysplit[1])
                            if team_num not in sql_rows['team'].keys():
                                sql_rows['team'][team_num] = {'team_num':team_num}
                            if len(keysplit) > 2:
                                category = '_'.join(keysplit[2:])
                                sql_rows['team'][team_num][category] = value
                        elif 'MissionBagEntry_' in key:
                            entry_num = int(keysplit[1])
                            if entry_num not in sql_rows['entry'].keys():
                                sql_rows['entry'][entry_num] = {'entry_num':entry_num}
                            if len(keysplit) > 2:
                                category = '_'.join(keysplit[2:])
                                sql_rows['entry'][entry_num][category] = value
                        elif 'Entry_' not in key:
                            sql_rows['game'][key] = value
        return sql_rows

    def insert_row(self,table, row):
        #print('inserting data into table %s' % table)
        connection = sqlite3.connect(database)
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

