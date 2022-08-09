from PyQt6.QtCore import QObject,pyqtSignal
from Server import sendToS3, sendLogToS3
import time
from resources import *
import os
from datetime import datetime
import xmltodict
from util.MainWindow import MainWindow
from util.StatusBar import StatusBar

def file_changed(xml,ts):
    return os.stat(xml).st_mtime != ts

running = False

class Logger(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(object)

    def __init__(self,window):
        super().__init__()
        self.window = window
        self.xml_path = settings.value("xml_path")
        if not os.path.exists(jsondir):
            os.makedirs(jsondir,exist_ok=True)

    def run(self):
        StatusBar.setStatus("Logger activated.")
        last_change = -1
        last_hunt = -1

        p = 0
        while True:
            if self.xml_path == None:
                self.xml_path = settings.value("xml_path")
                continue
            if file_changed(self.xml_path,last_change):
                timestamp = int(os.stat(self.xml_path).st_mtime)
                log('file change detected at %d' % timestamp)
                StatusBar.setStatus('file change detected at %s' % datetime.fromtimestamp(timestamp).strftime('%H:%M'))

                y = datetime.fromtimestamp(timestamp).strftime('%Y')
                m = datetime.fromtimestamp(timestamp).strftime('%m')
                d = datetime.fromtimestamp(timestamp).strftime('%d')

                subdir = settings.value("aws_sub","hunterX")
                outfile = os.path.join(jsondir,'/'.join([subdir,y,m,d,'attributes_%s.json' % timestamp]))
                os.makedirs(os.path.dirname(outfile),exist_ok=True)

                new_data = build_json_from_xml()
                id = generate_checksum(new_data)
                new_data["id"] = id

                prev_json = newest_file()
                if prev_json != None:
                    with open(prev_json,'r') as f:
                        prev_data = json.load(f)
                    if 'id' not in prev_data.keys():
                        prev_id = generate_checksum(prev_data)
                        prev_data['id'] = prev_id
                        with open(prev_json,'w') as f:
                            json.dump(prev_data,f)

                    if prev_data["id"] != id:
                        with open(outfile,'w') as f:
                            log("writing new file to %s" % os.path.basename(f.name))
                            json.dump(new_data,f)
                        StatusBar.setStatus('sending %s to s3' % os.path.basename(outfile))
                        key = outfile.replace(app_data_path+'\\','/').replace('\\','/')
                        sendToS3(outfile,key)
                        sendLogToS3(timestamp)
                        last_hunt = last_change
                    else:
                        log("identical file; continuing.")
                else:
                    with open(outfile,'w') as f:
                        log("writing new file to %s" % os.path.basename(f.name))
                        json.dump(new_data,f)
                    StatusBar.setStatus('sending %s to s3' % os.path.basename(outfile))
                    key = outfile.replace(app_data_path+'\\','/').replace('\\','/')
                    sendToS3(outfile,key)
                    sendLogToS3(timestamp)
                    last_hunt = last_change
                last_change = os.stat(self.xml_path).st_mtime

            time.sleep(1)
            elapsed = int(time.time() - last_hunt)/60
            if last_hunt == -1:
                StatusBar.setStatus("waiting for new data%s"%("."*p))
                p = (p+1)%6

            else:
                StatusBar.setStatus("%d minutes since last Hunt%s" % (elapsed, "."*p))
                p = (p+1)%4
            if not running:
                log('stopped logging')
                break
        StatusBar.setStatus("Hunts are not being logged.", "#ff0000")
        self.finished.emit()



def build_json_from_xml():
    log('building json object')
    with open(settings.value("xml_path"),'r',encoding='utf-8') as xf:
        points = 0
        teams = {}
        hunters = {}
        entries = {}
        game = { }
        for line in xf:
            try:
                l = xmltodict.parse(line)
            except:
                continue
            key = l['Attr']['@name']
            val = parse_value(l['Attr']['@value'])
            if "MissionBag" in line:
                if "tooltip" not in key:
                    if val == "":
                        val = -1
                    keysplit = key.split('_')
                    if 'MissionBagPlayer_' in key:
                        team_num = int(keysplit[1])
                        hunter_num = int(keysplit[2])
                        hunter_id = '_'.join([keysplit[1],keysplit[2]])
                        if hunter_id not in hunters:
                            hunters[hunter_id] = {
                                "team_num":team_num,
                                "hunter_num":hunter_num
                            }
                        category = '_'.join(keysplit[3:])
                        hunters[hunter_id][category] = val
                    elif 'MissionBagTeam_' in key:
                        team_num = keysplit[1]
                        if team_num not in teams:
                            teams[team_num] = {
                                "team_num":team_num
                            }
                        if len(keysplit) > 2:
                            cat = '_'.join(keysplit[2:])
                            teams[team_num][cat] = val
                    elif 'MissionBagEntry_' in key and '@' not in str(val):
                        entry_num = keysplit[1]
                        if entry_num not in entries:
                            entries[entry_num] = {
                                "entry_num":entry_num
                            }
                        if len(keysplit) > 2:
                            cat = '_'.join(keysplit[2:])
                            entries[entry_num][cat] = val
                    elif 'Entry_' not in key:
                        game[key] = val
            elif "UnlockRank" in line:
                settings.setValue('HunterLevel',val)
                game["HunterLevel"] = val
            elif "MissionAccoladeEntry_" in line:
                if "eventPoints" in key:
                    points += int(val)
        game["EventPoints"] = points

        json_obj = clean_data({
            "teams":teams,
            "hunters":hunters,
            "entries":entries,
            "game":game
        })

        return json_obj

def newest_file():
    t = -1
    prev = None
    for root, directories,files in os.walk(os.path.join(jsondir,settings.value("aws_sub","hunterX"))):
        for f in files:
            if os.stat(os.path.join(root,f)).st_mtime > t:
                t = os.stat(os.path.join(root,f)).st_mtime
                prev = os.path.join(root,f)
    return prev
