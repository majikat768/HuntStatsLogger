import hashlib
from pprint import pprint
from datetime import datetime
import sys
from PyQt6.QtCore import QThread
from PyQt6.QtWidgets import QSizePolicy, QSpacerItem
from PyQt6.QtGui import QPixmap
import json
import os
from PyQt6.QtCore import QSettings

app_data_path = os.path.join('.','hsl_files')
if not os.path.exists(app_data_path):
    os.makedirs(app_data_path,exist_ok=True)
db = os.path.join(app_data_path,'huntstats.db')
settings = QSettings(os.path.join(app_data_path,'settings.ini'),QSettings.Format.IniFormat)
logfile = os.path.join(app_data_path,'logs','log.txt')
jsondir = os.path.join(app_data_path,'json')


#aws
client_id="5ek9jf37380g23qjbilbuh08hq"
identity_pool_id='af1647aa-3bf0-42ac-9a2d-9ed6558aadb7'
user_pool_id='us-west-2_NEhNwG197'

hSpacer16 = QSpacerItem(16,1,QSizePolicy.Policy.Fixed,QSizePolicy.Policy.Fixed)
vSpacer16 = QSpacerItem(1,16,QSizePolicy.Policy.Fixed,QSizePolicy.Policy.Fixed)

gameTypes = ["All Hunts", "Bounty Hunt", "Quick Play"] 
def resource_path(relative_path):
    try:
    # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

deadIcon = resource_path('assets/icons/death2.png')
livedIcon = resource_path('assets/icons/lived2.png')
noneIcon = resource_path('assets/icons/none.png')

def star_pixmap(stars):
    return QPixmap(star_path(stars))

def star_path(stars):
    return os.path.join(resource_path('assets/icons'),'_%dstar.png' % stars)

def mmr_to_stars(mmr):
    return 0 if mmr == -1 else 1 if mmr < 2000 else 2 if mmr < 2300 else 3 if mmr < 2600 else 4 if mmr < 2750 else 5 if mmr < 3000 else 6

def unix_to_datetime(timestamp):
    return datetime.fromtimestamp(timestamp).strftime('%H:%M %m/%d/%y')

def isLoggedIn():
    return settings.value('aws_access_token','') != ''

def StartLogger(logger,parent):
    if logger == None:
        return
    log('starting logger')
    if not settings.value("hunt_dir"):
        return
    loggerThread = QThread(parent=parent)
    logger.moveToThread(loggerThread)
    loggerThread.started.connect(logger.run)
    logger.finished.connect(loggerThread.quit)
    logger.finished.connect(logger.deleteLater)
    logger.finished.connect(loggerThread.deleteLater)
    #logger.progress.connect(parent.update)
    loggerThread.start()

def log(msg):
    print(str(msg))
    if not os.path.exists(logfile):
        os.makedirs(os.path.dirname(logfile),exist_ok=True)
    with open(logfile,'a') as lf:
        lf.write(str(msg))
        lf.write('\n')

def translateJson(data,file):
    timestamp = int(file.split("attributes_")[1].split(".json")[0])
    if "teams" in data and "hunters" in data and "entries" in data and "game" in data:
        newdata = {
            "teams": {},
            "hunters": {},
            "entries": {},
            "game": {"timestamp":timestamp} 
        }

        teams = data["teams"]
        hunters = data["hunters"]
        entries = data["entries"]
        game = data["game"]
        for k in teams:
            newdata["teams"][parse_value(k)] = {
                parse_value(k2) : parse_value(teams[k][k2]) for k2 in teams[k] 
            }
            newdata["teams"][parse_value(k)]["timestamp"] = timestamp
        for k in hunters:
            newdata["hunters"][parse_value(k)] = {
                parse_value(k2) : parse_value(hunters[k][k2]) for k2 in hunters[k] 
            }
            newdata["hunters"][parse_value(k)]["timestamp"] = timestamp
        for k in entries:
            newdata["entries"][parse_value(k)] = {
                parse_value(k2) : parse_value(entries[k][k2]) for k2 in entries[k] 
            }
            newdata["entries"][parse_value(k)]["timestamp"] = timestamp
        for k in game:
            newdata["game"][parse_value(k)] = parse_value(game[k])
        newdata["game"]["timestamp"] = timestamp
        return newdata
    elif "teams" in data and "entries" in data and "MissionBagBoss_0" in data:
        hunters = {}
        teams = {}
        entries = {}
        game = {}
        for team in data["teams"]:
            dathunters = team.pop("hunters")
            for hunter in dathunters:
                hunternum = str(hunter["hunter_num"])
                teamnum = str(hunter["team_num"])
                hunter_id = "_".join([hunternum,teamnum])
                hunters[hunter_id] = hunter
            teams[team["team_num"]] = team
        data.pop("teams")
        for entry in data["entries"]:
            entries[entry["entry_num"]] = entry
        data.pop("entries")
        for key in data:
            if key != "id":
                game[key] = data[key]
        newdata = {
            "teams": {},
            "hunters": {},
            "entries": {},
            "game": {} 
        }
        for k in teams:
            newdata["teams"][parse_value(k)] = {
                parse_value(k2) : parse_value(teams[k][k2]) for k2 in teams[k] 
            }
            newdata["teams"][parse_value(k)]["timestamp"] = timestamp
        for k in hunters:
            newdata["hunters"][parse_value(k)] = {
                parse_value(k2) : parse_value(hunters[k][k2]) for k2 in hunters[k] 
            }
            newdata["hunters"][parse_value(k)]["timestamp"] = timestamp
        for k in entries:
            newdata["entries"][parse_value(k)] = {
                parse_value(k2) : parse_value(entries[k][k2]) for k2 in entries[k] 
            }
            newdata["entries"][parse_value(k)]["timestamp"] = timestamp
        for k in game:
            newdata["game"][parse_value(k)] = parse_value(game[k])
        newdata["game"]["timestamp"] = timestamp
        return newdata
    else:
        return data

def parse_value(val):
    if type(val) is int or val.isnumeric():
        return int(val)
    elif val.lower() == 'true':
        return 1
    elif val.lower() == 'false':
        return 0
    else:
        return val

    
def getLocalFiles():
    if not settings.value("aws_sub"):   return
    localfiles = []
    for root,dirs,files in os.walk(os.path.join(jsondir,settings.value("aws_sub"))):
        for f in files:
            localfiles.append(os.path.join(root,f))
    return localfiles

def clean_data(data):
    num_teams = int(data["game"]["MissionBagNumTeams"])
    num_entries = int(data["game"]["MissionBagNumEntries"])

    teams = {}
    if "team" in data:
        data["teams"] = data.pop("team")
    for teamnum in data["teams"]:
        if int(teamnum) < num_teams:
            if 'timestamp' in data["teams"][teamnum]:
                data["teams"][teamnum].pop('timestamp')
            teams[str(teamnum)] = data["teams"][teamnum]
    data["teams"] = teams

    entries = {}
    if "entry" in data:
        data["entries"] = data.pop("entry")
    for entrynum in data["entries"]:
        if int(entrynum) < int(num_entries):
            if 'timestamp' in data["entries"][entrynum]:
                data["entries"][entrynum].pop('timestamp')
            entries[str(entrynum)] = data["entries"][entrynum]
    data["entries"] = entries


    hunters = {}
    if "hunter" in data:
        data["hunters"] = data.pop("hunter")
    for k in data["hunters"]:
        hunter = data["hunters"][k]
        if "0" in hunter.keys():
            team = hunter
            for n in team.keys():
                hunter = team[n]
                teamnum = hunter["team_num"]
                hunternum = hunter["hunter_num"]
                id = '_'.join([teamnum,hunternum])
                if int(teamnum) < num_teams and int(hunternum) < teams[teamnum]["numplayers"]:
                    if 'timestamp' in hunter:
                        hunter.pop('timestamp')
                    hunters[id] = hunter

        else:
            teamnum = str(hunter["team_num"])
            hunternum = str(hunter["hunter_num"])
            id = '_'.join([teamnum,hunternum])

            if int(teamnum) < num_teams and int(hunternum) < teams[teamnum]["numplayers"]:
                if 'timestamp' in hunter:
                    hunter.pop('timestamp')
                hunters[id] = hunter
    data["hunters"] = hunters

    return data

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
    return checksum

