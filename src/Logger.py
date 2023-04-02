from datetime import datetime
import sqlite3
import hashlib
import json
import os
import time
import xmltodict
from PyQt6.QtCore import QObject, pyqtSignal
from resources import *
from DbHandler import *

def file_changed(ts):
    return os.stat(settings.value("xml_path")).st_mtime != ts

def latest_file():
    t = -1
    prev = None
    for root,dirs,files in os.walk(json_dir):
        for f in files:
            if os.stat(os.path.join(root,f)).st_mtime > t:
                t = os.stat(os.path.join(root,f)).st_mtime
                prev = os.path.join(root,f)

    return prev

class Logger(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal()
    def __init__(self,parent):
        self.mainframe = parent
        if not tables_exist():
            create_tables()
        self.running = False
        super().__init__()

    def run(self):
        self.running = True
        last_change = -1
        last_hunt = -1
        self.mainframe.setStatus("Logger started.")

        p = 0
        while True:
            if not os.path.exists(settings.value("xml_path")):
                time.sleep(1)
                continue
            if file_changed(last_change):
                self.mainframe.setStatus("file change detected")
                last_change = os.stat(settings.value("xml_path")).st_mtime
                ts = int(os.stat(settings.value("xml_path")).st_mtime)
                y = datetime.fromtimestamp(ts).strftime('%Y')
                m = datetime.fromtimestamp(ts).strftime('%m')
                d = datetime.fromtimestamp(ts).strftime('%d')

                outfile = os.path.join(json_dir,'/'.join([y,m,d,'attributes_%s.json' % ts]))
                os.makedirs(os.path.dirname(outfile),exist_ok=True)

                try:
                    new_data = build_json_from_xml(ts)
                    if new_data is None:
                        self.progress.emit()
                        return
                    record_exists = execute_query("select * from 'games' where game_id is '%s'" % new_data['game']['game_id'])
                    if len(record_exists) <= 0:
                        log('change detected')
                        self.mainframe.setStatus("writing new record to json file....")
                        with open(outfile,'w') as f:
                            json.dump(new_data,f)

                        #if str(settings.value("sync_files","false")).lower() == "true":
                            #self.mainframe.server.upload_file(file=outfile,file_type="json")

                        self.mainframe.setStatus("writing new record to database....")
                        json_to_db(new_data)
                        last_hunt = last_change
                        log('successfully recorded hunt')
                        self.progress.emit()
                except Exception as e:
                    log('building json error, trying again')
                    log(e)
                    continue

            if last_hunt > 0:
                elapsed = (time.time() - last_hunt)//60
                self.mainframe.setStatus("%d minutes since last Hunt%s" % (elapsed, '.'*p))
            else:
                self.mainframe.setStatus("waiting for new data%s"%('.'*p))

            time.sleep(1)
            p = (p+1)%7

            if not self.running:
                break
        self.finished.emit()

def generate_checksum(obj):
    #print('generating checksum')
    common_data = {
        "MissionBagBoss_0": obj['game']['MissionBagBoss_0'],
        "MissionBagBoss_1": obj['game']['MissionBagBoss_1'],
        "MissionBagBoss_2": obj['game']['MissionBagBoss_2'],
        "MissionBagBoss_3": obj['game']['MissionBagBoss_3'],
        "MissionBagNumTeams": obj['game']['MissionBagNumTeams']
    }

    common_data['teams'] = {}
    common_data['hunters'] = {}

    for teamnum in obj['teams']:
        team = obj['teams'][teamnum]
        common_data['teams'][teamnum] = {
            "handicap": team['handicap'],
            "mmr": team['mmr'],
            "numplayers": team['numplayers']
        }

    for hunternum in obj['hunters']:
        hunter = obj['hunters'][hunternum]
        common_data['hunters'][hunternum] = {
            "blood_line_name":hunter['blood_line_name'],
            "mmr":hunter['mmr'],
            "profileid":hunter['profileid']
        }
    checksum = hashlib.md5(json.dumps(common_data,sort_keys=True).encode('utf-8')).hexdigest()
    return checksum

def clean_data(obj):
    try:
        num_teams = int(obj['game']['MissionBagNumTeams'])
        num_entries = int(obj['game']['MissionBagNumEntries'])
        num_accolades = int(obj['game']['MissionBagNumAccolades'])

        teams = {}
        for teamnum in obj["teams"]:
            if int(teamnum) < num_teams:
                teams[str(teamnum)] = obj['teams'][teamnum]

        entries = {}
        for entrynum in obj['entries']:
            if int(entrynum) < num_entries:
                entries[str(entrynum)] = obj['entries'][entrynum]
            
        accolades = {}
        for accoladenum in obj['accolades']:
            if int(accoladenum) < num_accolades:
                accolades[str(accoladenum)] = obj['accolades'][accoladenum]
        
        hunters = {}
        for id in obj['hunters']:
            teamnum = id.split('_')[0]
            hunternum = id.split('_')[1]
            if int(teamnum) < num_teams and int(hunternum) < int(teams[teamnum]["numplayers"]):
                hunters[id] = obj['hunters'][id]

        new_obj = {
            "teams":teams,
            "hunters":hunters,
            "entries":entries,
            "accolades":accolades,
            "game":obj['game']
        }

        checksum = generate_checksum(new_obj)

        for teamnum in new_obj['teams']:
            new_obj['teams'][teamnum]['game_id'] = checksum
        for hunternum in new_obj['hunters']:
            new_obj['hunters'][hunternum]['game_id'] = checksum
        for entrynum in new_obj['entries']:
            new_obj['entries'][entrynum]['game_id'] = checksum
        for accoladenum in new_obj['accolades']:
            new_obj['accolades'][accoladenum]['game_id'] = checksum
        new_obj['game']['game_id'] = checksum

        return new_obj
    except Exception as e:
        log('clean_data')
        log(e)
        return obj


def build_json_from_xml(ts):
    if debug:
        log('building json')
    with open(settings.value("xml_path"),'r',encoding='utf-8') as xf:
        teams = {}
        hunters = {}
        entries = {}
        accolades = {}
        game = {"timestamp":ts}

        for line in xf:
            try:
                ln = xmltodict.parse(line)
            except:
                continue
            key = ln['Attr']['@name']
            val = ln['Attr']['@value']
            keysplit = key.split("_")
            if "MissionBag" in line and "tooltip" not in key:
                if val == "":
                    val = "-1"
                if "MissionBagPlayer_" in key:
                    team_num = int(keysplit[1])
                    hunter_num = int(keysplit[2])
                    hunter_id = '_'.join(keysplit[1:3])
                    if hunter_id not in hunters:
                        hunters[hunter_id] = {
                            "team_num": team_num,
                            "hunter_num": hunter_num,
                            "timestamp": ts
                        }
                    category = '_'.join(keysplit[3:])
                    if category == 'blood_line_name':
                        val = val.replace('\'','_')
                    hunters[hunter_id][category] = val
                elif "MissionBagTeam_" in key:
                    team_num = keysplit[1]
                    if team_num not in teams:
                        teams[team_num] = {
                            "team_num":team_num,
                            "timestamp":ts
                        }
                    if len(keysplit) > 2:
                        cat = '_'.join(keysplit[2:])
                        teams[team_num][cat] = val
                elif "MissionBagEntry_" in key and '@' not in str(val):
                    entry_num = keysplit[1]
                    if entry_num not in entries:
                        entries[entry_num] = {
                            "entry_num":entry_num,
                            "timestamp":ts
                        }

                    if len(keysplit) > 2:
                        cat = '_'.join(keysplit[2:])
                        entries[entry_num][cat] = val
                elif "Entry_" not in key:
                    game[key] = val
            elif "MissionAccoladeEntry" in line and "header" not in key and "iconPath" not in key:
                accolade_num = keysplit[1]
                if accolade_num not in accolades:
                    accolades[accolade_num] = {
                        "accolade_num":accolade_num,
                        "timestamp":ts
                    }
                if len(keysplit) > 2:
                    cat = '_'.join(keysplit[2:])
                    accolades[accolade_num][cat] = val
            elif "UnlockRank" in line:
                if settings.value("HunterLevel","") != "" and int(val) < int(settings.value("HunterLevel")):
                    log("prestiged")
                settings.setValue("HunterLevel",val)
        #if teams == {} or hunters == {} or entries == {} or accolades == {} or game == {}:
            #return None
        return clean_data({
            "teams":teams,
            "hunters":hunters,
            "entries":entries,
            "accolades":accolades,
            "game":game
        })

def elapsed(ss):
    mm = ss//60
    if mm < 60:
        return "%d minutes since last Hunt" % mm
    else:
        hh = mm//60
        mm = mm % 60
        return "%d hours %d minutes since last Hunt" % (hh, mm)