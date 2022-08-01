from PyQt6.QtCore import QObject,pyqtSignal
import xmltodict
from datetime import datetime
import os
import json
import time
import boto3
import hashlib

killall = False
identity_pool_id='af1647aa-3bf0-42ac-9a2d-9ed6558aadb7'
user_pool_id='us-west-2_NEhNwG197'
client_id="5ek9jf37380g23qjbilbuh08hq"

'''
def xmltodict(line):
    s = line.split('"')
    key = s[1]
    value = s[3]
    return { key : value }
'''

def diff(file1,file2):
    with open(file1,'r',encoding='utf-8') as f1:
        with open(file2,'r',encoding='utf-8') as f2:
            return f1.read() != f2.read()

def data_eq(json1,json2):
    eq = json1['id'] == json2['id']
    if not eq:
        return False
    return True

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

    def __init__(self,parent):
        QObject.__init__(self)
        self.parent = parent
        self.json_out_dir = os.path.join(self.parent.app_data_path,'json')
        if not os.path.exists(self.json_out_dir):
            os.makedirs(self.json_out_dir)
        self.settings = self.parent.settings

    def set_path(self,huntpath):
        self.print('setting path to %s' % huntpath)
        suffix = 'user/profiles/default/attributes.xml' 
        self.xml_path = os.path.join(huntpath,suffix)
        if not os.path.exists(self.xml_path):
            self.print('attributes.xml not found.')
            self.print(self.xml_path)
            return -1
        return 1

    def print(self,msg):
        print(msg)
        self.progress.emit(msg)


    def send_to_s3(self,filename):
        if self.settings.value('aws_id_token','') == '':
            return
        print('sending to s3')
        client = boto3.client('cognito-identity','us-west-2')
        try:
            response = client.get_id(
                IdentityPoolId='us-west-2:%s' % identity_pool_id,
                Logins={'cognito-idp.us-west-2.amazonaws.com/%s' % user_pool_id : self.settings.value('aws_id_token','none')}
            )
            IdId = response['IdentityId']
            response = client.get_credentials_for_identity(
                IdentityId=IdId,
                Logins={'cognito-idp.us-west-2.amazonaws.com/%s' % user_pool_id : self.settings.value('aws_id_token','none')}
            )
            accessKey = response['Credentials']['AccessKeyId']
            secretKey = response['Credentials']['SecretKey']
            sessionToken = response['Credentials']['SessionToken']
            
            session = boto3.Session(
                aws_access_key_id=accessKey,
                aws_secret_access_key=secretKey,
                aws_session_token=sessionToken
            )
            s3 = session.client('s3')
            s3.put_object(
                Body=open(os.path.join(self.json_out_dir,filename),'r').read(),
                Bucket='huntstatslogger',
                Key='json/%s' % filename
            )
            print('sent to s3')
        except client.exceptions.NotAuthorizedException as msg1:
            print('not authorized\n%s' % msg1)
            try:
                self.parent.refresh_token()
                print('token updated')
                self.send_to_s3(filename)
            except client.exceptions.NotAuthorizedException as msg2:
                print('still not authorized\n%s' % msg2)
        
    def newest_file(self):
        t = -1
        prev = None
        for root, directories,files in os.walk(self.json_out_dir):
            for f in files:
                if os.stat(os.path.join(root,f)).st_mtime > t:
                    t = os.stat(os.path.join(root,f)).st_mtime
                    prev = os.path.join(root,f)
        return prev


    def run(self):
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

                json_outfile = '/'.join([self.settings.value('aws_username','hunter'),y,m,d,'attributes_%s.json' % timestamp])
                os.makedirs(os.path.join(self.json_out_dir,os.path.dirname(json_outfile)),exist_ok=True)
                json_files = os.listdir(self.json_out_dir)

                new_data = self.build_json_from_xml()
                checksum = self.generate_checksum(new_data)
                new_data['id'] = checksum

                prev_json = self.newest_file()
                if prev_json == None:
                    with open(os.path.join(self.json_out_dir,json_outfile),'w',encoding='utf-8') as outfile:
                        json.dump(new_data,outfile,indent=True,ensure_ascii=True)
                        self.print('writing new file to %s' % outfile)
                    self.send_to_s3(json_outfile)
                else:
                    prev_data = json.load(open(prev_json,'r'))

                    #new_data = json.load(open(json_outfile_wait,'r'))
                    if data_eq(new_data,prev_data):
                        print('identical file found')
                        
                    else:
                        with open(os.path.join(self.json_out_dir,json_outfile),'w',encoding='utf-8') as outfile:
                            json.dump(new_data,outfile,indent=True)
                            self.print('writing new file to %s' % outfile)
                        self.send_to_s3(json_outfile)


                last_change = os.stat(self.xml_path).st_mtime
                self.print('done')

            time.sleep(1)
            if killall:
                self.finished.emit()
                break

        
    def build_json_from_xml(self):
        self.print('building json object')
        json_obj = {
            "teams":[],
            "entries":[]
        }

        with open(self.xml_path,'r',encoding='utf-8') as xmlfile:
            points = 0
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
                            while len(json_obj["teams"]) <= int(team_num):
                                json_obj["teams"].append(
                                    {
                                        "team_num":len(json_obj["teams"]),
                                        "hunters":[]
                                    }
                                )
                            while len(json_obj["teams"][int(team_num)]["hunters"]) <= int(hunter_num):
                                json_obj["teams"][int(team_num)]["hunters"].append({"hunter_num":hunter_num,"team_num":int(team_num)})

                            category = '_'.join(keysplit[3:])
                            json_obj["teams"][int(team_num)]["hunters"][int(hunter_num)][category] = value
                        elif 'MissionBagTeam_' in key:
                            team_num = keysplit[1]
                            while len(json_obj["teams"]) <= int(team_num):
                                json_obj["teams"].append(
                                    {
                                        "team_num":len(json_obj["teams"]),
                                        "hunters":[]
                                    }
                                )
                            if len(keysplit) > 2:
                                category = '_'.join(keysplit[2:])
                                json_obj["teams"][int(team_num)][category] = value

                        elif 'MissionBagEntry_' in key and '@' not in str(value):
                            entry_num = keysplit[1]
                            while len(json_obj["entries"]) <= int(entry_num):
                                json_obj["entries"].append( {"entry_num":len(json_obj["entries"])} )

                            if len(keysplit) > 2:
                                category = '_'.join(keysplit[2:])
                                json_obj['entries'][int(entry_num)][category] = value
                        elif 'Entry_' not in key:
                            json_obj[key] = value
                elif "UnlockRank" in line:
                    try:
                       linedict = xmltodict.parse(line)
                    except:
                        continue
                    key = linedict['Attr']['@name'].split('/')[1]
                    value= linedict['Attr']['@value']
                    self.settings.setValue('HunterLevel',value)
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

            json_obj['EventPoints'] = points
        return self.clean_json(json_obj)

    def generate_checksum(self,data):
        common = {}
        common["MissionBagBoss_0"] = data["MissionBagBoss_0"]
        common["MissionBagBoss_1"] = data["MissionBagBoss_1"]
        common["MissionBagBoss_2"] = data["MissionBagBoss_2"]
        common["MissionBagBoss_3"] = data["MissionBagBoss_3"]
        common["MissionBagNumTeams"] = data["MissionBagNumTeams"]
        common["teams"] = []

        for i in range(len(data["teams"])):
            common["teams"].append({})
            common["teams"][i]["handicap"] = data["teams"][i]["handicap"]
            common["teams"][i]["mmr"] = data["teams"][i]["mmr"]
            common["teams"][i]["numplayers"] = data["teams"][i]["numplayers"]
            common["teams"][i]["hunters"] = []
            for j in range(len(data["teams"][i]["hunters"])):
                common["teams"][i]["hunters"].append({})
                common["teams"][i]["hunters"][j]["blood_line_name"] = data["teams"][i]["hunters"][j]["blood_line_name"] 
                common["teams"][i]["hunters"][j]["mmr"] = data["teams"][i]["hunters"][j]["mmr"] 
                common["teams"][i]["hunters"][j]["profileid"] = data["teams"][i]["hunters"][j]["profileid"] 

        checksum = hashlib.md5(json.dumps(common,sort_keys=True).encode('utf-8')).hexdigest()
        print(checksum)
        return checksum



    def clean_json(self,json_obj):
        num_teams = json_obj["MissionBagNumTeams"]
        num_entries = json_obj["MissionBagNumEntries"]
        json_obj["teams"] = json_obj["teams"][:num_teams]
        json_obj["entries"] = json_obj["entries"][:num_entries]
        hunters_per_team = { team["team_num"] : team["numplayers"] for team in json_obj["teams"] }
        for team in json_obj["teams"]:
            team["hunters"] = team["hunters"][:int(hunters_per_team[team["team_num"]])]
        
        return json_obj