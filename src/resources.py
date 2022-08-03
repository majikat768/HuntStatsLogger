import os,sys
import hashlib
import json
from datetime import datetime
from PyQt6.QtCore import QSettings, QThread

killall = False

app_data_path = os.path.join('.','hsl_files')
if not os.path.exists(app_data_path):
    os.makedirs(app_data_path)

settings  = QSettings(
            os.path.join(app_data_path,'settings.ini'),
            QSettings.Format.IniFormat
        )
#settings = QSettings('./settings.ini',QSettings.Format.IniFormat)

db = os.path.join(app_data_path,'huntstats.db')
jsondir = os.path.join(app_data_path,'json')
if not os.path.exists(jsondir):
    os.makedirs(jsondir)

logdir = os.path.join(app_data_path,'logs')
if not os.path.exists(logdir):
    os.makedirs(logdir)

logfile = os.path.join(logdir,'log.txt')

client_id="5ek9jf37380g23qjbilbuh08hq"
identity_pool_id='af1647aa-3bf0-42ac-9a2d-9ed6558aadb7'
user_pool_id='us-west-2_NEhNwG197'

def resource_path(relative_path):
    try:
    # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def getLocalFiles():
    localfiles = []
    for root,dirs,files in os.walk(jsondir):
        for f in files:
            localfiles.append(os.path.join(root,f))
    return localfiles

def unix_to_datetime(timestamp):
    return datetime.fromtimestamp(timestamp).strftime('%H:%M %m/%d/%y')

def log(msg):
    print(msg)
    with open(logfile,'a') as log:
        log.write(str(msg))
        log.write('\n')

def valid_xml_path(path):
    suffix = 'user/profiles/default/attributes.xml' 
    if not os.path.exists(os.path.join(path,suffix)):
        return False
    return True

def clean_json(json_obj):
    num_teams = int(json_obj["game"]["MissionBagNumTeams"])
    num_entries = int(json_obj["game"]["MissionBagNumEntries"])
    teams = {}
    for teamnum in json_obj["teams"]:
        if int(teamnum) < num_teams:
            teams[teamnum] = json_obj["teams"][teamnum]
    json_obj["teams"] = teams

    entries = {}
    for entrynum in json_obj["entries"]:
        if int(entrynum) < int(num_entries):
            entries[entrynum] = json_obj["entries"][entrynum]
    json_obj["entries"] = entries

    hunters = {}
    for key in json_obj["hunters"]:
        teamnum = key.split('_')[0]
        hunternum = key.split('_')[1]
        hunter = json_obj["hunters"][key]
        if int(teamnum) < num_teams and int(hunternum) < json_obj["teams"][teamnum]["numplayers"]:
            hunters[key] = hunter
    json_obj["hunters"] = hunters

    return json_obj

def generate_checksum(data):
    common = {
        "MissionBagBoss_0" : data["game"]["MissionBagBoss_0"],
        "MissionBagBoss_1" : data["game"]["MissionBagBoss_1"],
        "MissionBagBoss_2" : data["game"]["MissionBagBoss_2"],
        "MissionBagBoss_3" : data["game"]["MissionBagBoss_3"],
        "MissionBagNumTeams" : data["game"]["MissionBagNumTeams"]
    }
    common["teams"] = {}
    common["hunters"] = {}

    for key in data["teams"]:
        team = data["teams"][key]
        common["teams"][key] = {
            "handicap" : team["handicap"],
            "mmr" : team["mmr"],
            "numplayers" : team["numplayers"]
        }

    for key in data["hunters"]:
        hunter = data["hunters"][key]
        common["hunters"][key] = {
            "blood_line_name":hunter["blood_line_name"],
            "mmr":hunter["mmr"],
            "profileid":hunter["profileid"]
        }

    checksum = hashlib.md5(json.dumps(common,sort_keys=True).encode('utf-8')).hexdigest()
    print(checksum)
    return checksum

def translateJson(data):
    print('translating json')
    if "teams" in data and "hunters" in data and "entries" in data and "game" in data and "teams" in data and "id" in data:
        return data

    newdata = {
        "teams":{},
        "entries":{},
        "hunters":{},
        "game":{}
    }
    for team in data["teams"]:
        teamnum = team["team_num"]
        hunters = team["hunters"]
        for hunter in hunters:
            hunter_id = "_".join([str(hunter["team_num"]),str(hunter["hunter_num"])])
            newdata["hunters"][hunter_id] = hunter
        team.pop("hunters")
        newdata["teams"][teamnum] = team
    data.pop("teams")
    
    for entry in data["entries"]:
        newdata["entries"][entry["entry_num"]] = entry
    data.pop("entries")
    newdata["id"] = data.pop("id")
    newdata["game"] = data
    return newdata


def StartConnection(conn,parent):
    print('starting connection')
    connThread = QThread(parent=parent)
    conn.moveToThread(connThread)
    connThread.started.connect(conn.run)
    conn.finished.connect(connThread.quit)
    conn.finished.connect(conn.deleteLater)
    conn.finished.connect(connThread.deleteLater)
    conn.progress.connect(parent.update)
    connThread.start()
    print('runnin',connThread.isRunning())

def StartLogger(logger,parent):
    print('starting logger')
    validPath = logger.set_path(settings.value('huntDir',''))
    if validPath != 1:
        log("not valid path.")
        return
    loggerThread = QThread(parent=parent)
    logger.moveToThread(loggerThread)
    loggerThread.started.connect(logger.run)
    logger.finished.connect(loggerThread.quit)
    logger.finished.connect(logger.deleteLater)
    logger.finished.connect(loggerThread.deleteLater)
    logger.progress.connect(parent.update)
    loggerThread.start()