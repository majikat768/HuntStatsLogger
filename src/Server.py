import boto3
import os, json, time
from datetime import datetime
from resources import settings, log_file, aws_app_id
from DbHandler import execute_query
from PyQt6.QtCore import QObject, pyqtSignal, QThread

bucket_name = 'hunt-stats-bucket'
region = "us-west-2"
identity_pool_id = "us-west-2:4f2360fd-9eeb-49f3-9c29-5c50967180fa"
user_pool_id = "us-west-2_kaoUCRjS9"

class Server(QObject):
    finished = pyqtSignal(object)
    progress = pyqtSignal(object)
    def __init__(self,parent=None):
        super().__init__()
        self.mainframe = parent

    def upload_file(self,file=log_file, file_type="logs"):
        if str(settings.value("sync_files","false")).lower() == 'false':
            return
        print("uploading file")
        pid = settings.value("profileid","0")
        obj = os.path.basename(file)

        if file_type == "logs":
            prefix = '/'.join([file_type,pid])
        elif file_type == "json":
            ts = int(obj.split('.')[0].split('_')[1])
            y = datetime.fromtimestamp(ts).strftime("%Y")
            m = datetime.fromtimestamp(ts).strftime("%m")
            d = datetime.fromtimestamp(ts).strftime("%d")
            prefix = '/'.join([file_type,pid,y,m,d])
        else:
            prefix = "etc"

        key = "%s/%s" % (prefix,obj)
        idExpiration = int(settings.value("IdExpiresAt","-1"))
        if idExpiration < time.time() or idExpiration < 0:
            self.login_user()
        secExpiration = int(settings.value("SecretExpiresAt","-1"))
        if secExpiration < time.time() or secExpiration < 0:
            self.set_tokens()
        session = boto3.Session(
            aws_access_key_id=settings.value("AccessKeyId"),
            aws_secret_access_key=settings.value("SecretKey"),
            aws_session_token=settings.value("SessionToken")
        )
        s3 = session.client('s3')

        res = s3.put_object(
            Body=file,
            Bucket=bucket_name,
            Key=key
        )

    def init_user(self):
        print('initializing user')
        if settings.value("steam_name","") == "":
            pid = 0
        elif settings.value("profileid","") == "":
            pid = execute_query("select profileid from 'hunters' where blood_line_name = '%s'" % settings.value("steam_name"))
            pid = 0 if len(pid) == 0 else pid[0][0]
            if pid == 0:
                self.progress.emit({"init":"failed"})
                return
            settings.setValue("profileid",pid)
        else:
            pid = settings.value("profileid")

        client = boto3.client('cognito-idp',region_name=region)
        try:
            res = client.sign_up(
                ClientId=aws_app_id,
                Username=pid,
                Password=pid
            )
            self.progress.emit({"init":"success"})
            return True
        except client.exceptions.UsernameExistsException as e:
            print(e)
            self.progress.emit({"init":"user exists"})
            return False
        except Exception as e:
            print(e)
            self.progress.emit({"init":"failed"})
            return False

    def login_user(self):
        print('logging in')
        if settings.value("steam_name","") == "":
            pid = 0
        elif settings.value("profileid","") == "":
            pid = execute_query("select profileid from 'hunters' where blood_line_name = '%s'" % settings.value("steam_name"))
            pid = 0 if len(pid) == 0 else pid[0][0]
            if pid == 0:
                self.progress.emit({"login":"failed"})
                return
            settings.setValue("profileid",pid)
        else:
            pid = settings.value("profileid")
        
        client = boto3.client('cognito-idp',region_name=region)
        try:
            res = client.initiate_auth(
                ClientId=aws_app_id,
                AuthFlow="USER_PASSWORD_AUTH",
                AuthParameters={
                    "USERNAME":pid,"PASSWORD":pid
                }
            )
            if 'AuthenticationResult' in res:
                auth = res['AuthenticationResult']
                if 'AccessToken' in auth:
                    settings.setValue("AccessToken",auth['AccessToken'])
                if 'RefreshToken' in auth:
                    settings.setValue("RefreshToken",auth['RefreshToken'])
                if 'IdToken' in auth:
                    settings.setValue("IdToken",auth['IdToken'])
                if 'ExpiresIn' in auth:
                    settings.setValue("IdExpiresAt",int(time.time()) + int(auth['ExpiresIn']))
            self.set_tokens()
            print("logged in")
            self.progress.emit({"login":"success"})
            return True
        except Exception as e:
            print(e)
            self.progress.emit({"login":"failed"})
            return False

    def set_tokens(self):
        print("setting tokens")
        client = boto3.client("cognito-identity",region)
        logins={"cognito-idp.%s.amazonaws.com/%s" % (region,user_pool_id) : settings.value("IdToken")}
        res = client.get_id(
            IdentityPoolId=identity_pool_id,
            Logins=logins
        )
        IdId = res['IdentityId']
        res = client.get_credentials_for_identity(
            IdentityId=IdId,
            Logins=logins
        )

        if "Credentials" in res:
            cred = res["Credentials"]
            if "AccessKeyId" in cred:
                settings.setValue("AccessKeyId",cred["AccessKeyId"])
            if "SecretKey" in cred:
                settings.setValue("SecretKey",cred["SecretKey"])
            if "SessionToken" in cred:
                settings.setValue("SessionToken",cred["SessionToken"])
            if "Expiration" in cred:
                settings.setValue("SecretExpiresAt",int(cred["Expiration"].timestamp()))

def startThread(parent,instance,started=[],progress=[],finished=[]):
    print("starting thread")
    instance.parent = None
    thread = QThread(parent=parent)
    instance.moveToThread(thread)
    for s in started:
        thread.started.connect(s)
    for p in progress:
        instance.progress.connect(p)
    for f in finished:
        instance.finished.connect(f)
    thread.finished.connect(thread.quit)
    thread.finished.connect(instance.deleteLater)
    thread.finished.connect(thread.deleteLater)

    thread.start()