from PyQt6.QtCore import QObject,pyqtSignal
import xmltodict
from datetime import datetime
import os
import json
import time
from resources import *
import Client

'''
def xmltodict(line):
    s = line.split('"')
    key = s[1]
    value = s[3]
    return { key : value }
'''

def data_eq(json1,json2):
    return json1['id'] == json2['id']

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
    progress = pyqtSignal(object)
    xml_path = ''

    def __init__(self):
        QObject.__init__(self)
        jsondir = os.path.join(app_data_path,'json')
        if not os.path.exists(jsondir):
            os.makedirs(jsondir)

    def set_path(self,huntpath):
        log('setting path to %s' % huntpath)
        suffix = 'user/profiles/default/attributes.xml' 
        self.xml_path = os.path.join(huntpath,suffix)
        if not os.path.exists(self.xml_path):
            log('attributes.xml not found.')
            log(self.xml_path)
            return -1
        return 1

    def newest_file(self):
        t = -1
        prev = None
        for root, directories,files in os.walk(jsondir):
            for f in files:
                if os.stat(os.path.join(root,f)).st_mtime > t:
                    t = os.stat(os.path.join(root,f)).st_mtime
                    prev = os.path.join(root,f)
        return prev


    def run(self):
        print('logger.run')
        global killall
        last_change = -1

        while True:
            if self.xml_path == '': continue

            if file_changed(self.xml_path,last_change):
                print('file changed')
                timestamp = int(os.stat(self.xml_path).st_mtime)
                y = datetime.fromtimestamp(timestamp).strftime('%Y')
                m = datetime.fromtimestamp(timestamp).strftime('%m')
                d = datetime.fromtimestamp(timestamp).strftime('%d')

                json_outfile = '/'.join([settings.value('aws_sub','hunterX'),y,m,d,'attributes_%s.json' % timestamp])
                os.makedirs(os.path.join(jsondir,os.path.dirname(json_outfile)),exist_ok=True)
                json_files = os.listdir(jsondir)

                new_data = self.build_json_from_xml(timestamp)
                checksum = generate_checksum(new_data)
                new_data['id'] = checksum

                prev_json = self.newest_file()
                if prev_json == None:
                    with open(os.path.join(jsondir,json_outfile),'w',encoding='utf-8') as outfile:
                        json.dump(new_data,outfile,indent=True,ensure_ascii=True)
                        log('writing new file to %s' % outfile.name)
                    Client.sendToS3(os.path.join(app_data_path,json_outfile))
                else:
                    prev_data = json.load(open(prev_json,'r'))

                    #new_data = json.load(open(json_outfile_wait,'r'))
                    if data_eq(new_data,prev_data):
                        print('identical file found')
                        
                    else:
                        with open(os.path.join(jsondir,json_outfile),'w',encoding='utf-8') as outfile:
                            json.dump(new_data,outfile,indent=True)
                            log('writing new file to %s' % outfile)
                        Client.sendToS3(os.path.join(app_data_path,json_outfile))


                last_change = os.stat(self.xml_path).st_mtime
                log('done')

            time.sleep(1)
            if killall:
                self.finished.emit()
                break

        
    def build_json_from_xml(self,timestamp):
        log('building json object')
        json_obj = {
            "teams":[],
            "entries":[]
        }

        with open(self.xml_path,'r',encoding='utf-8') as xmlfile:
            points = 0
            teams = {}
            hunters = {}
            entries = {}
            game = {"timestamp":timestamp}
            for line in xmlfile:
                if "MissionBag" in line:
                    try:
                        linedict = xmltodict.parse(line)
                    except:
                        continue
                    key = linedict['Attr']['@name']
                    value = parse_value(linedict['Attr']['@value'])
                    if value != '' and 'tooltip' not in key:
                        keysplit = key.split('_')
                        if 'MissionBagPlayer_' in key:
                            team_num = keysplit[1]
                            hunter_num = keysplit[2]
                            hunter_id = '_'.join([team_num,hunter_num])
                            if hunter_id not in hunters:
                                hunters[hunter_id] = {"team_num":team_num,"hunter_num":hunter_num,"timestamp":timestamp}

                            category = '_'.join(keysplit[3:])
                            hunters[hunter_id][category] = value
                        elif 'MissionBagTeam_' in key:
                            team_num = keysplit[1]
                            if team_num not in teams:
                                teams[team_num] = {"team_num":team_num,"timestamp":timestamp}
                            if len(keysplit) > 2:
                                category = '_'.join(keysplit[2:])
                                teams[team_num][category] = value

                        elif 'MissionBagEntry_' in key and '@' not in str(value):
                            entry_num = keysplit[1]
                            if entry_num not in entries:
                                entries[entry_num] = {"entry_num":entry_num,"timestamp":timestamp}
                            if len(keysplit) > 2:
                                category = '_'.join(keysplit[2:])
                                entries[entry_num][category] = value
                        elif 'Entry_' not in key:
                            game[key] = value
                elif "UnlockRank" in line:
                    try:
                       linedict = xmltodict.parse(line)
                    except:
                        continue
                    key = linedict['Attr']['@name'].split('/')[1]
                    value= linedict['Attr']['@value']
                    settings.setValue('HunterLevel',value)
                    game["HunterLevel"] = value
                    #json_obj[key] = value
                elif 'MissionAccoladeEntry_' in line:
                    try:
                       linedict = xmltodict.parse(line)
                    except:
                        continue
                    key = linedict['Attr']['@name']
                    value= parse_value(linedict['Attr']['@value'])
                    if value != '' and 'tooltip' not in key:
                        keysplit = key.split('_')
                        if 'MissionAccoladeEntry_' in key:
                            if "eventPoints" in key:
                                points += int(value)
                                #sql_rows['game']['EventPoints'] = value

            game['EventPoints'] = points
            
            json_obj = {
                "teams":teams,
                "hunters":hunters,
                "entries":entries,
                "game":game,
            }

        return clean_json(json_obj)



