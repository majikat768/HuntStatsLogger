import os
import boto3
from PyQt6.QtCore import QObject,pyqtSignal,QThread
from resources import *

def set_id():
    log('setting aws user id')
    if settings.value('aws_access_token','') == '':    return False
    client = boto3.client("cognito-idp",region_name="us-west-2")
    try:
        response = client.get_user(
            AccessToken=settings.value('aws_access_token')
        )
        for e in response["UserAttributes"]:
            if e['Name'] == 'sub':
                settings.setValue("aws_sub",e['Value'])
                break
        log('done')
    except Exception as msg:
        log(str(msg))
        try:
            refresh_token()
            set_id()
        except Exception as msg2:
            log(str(msg2))

def getTokens():
    try:
        client = boto3.client('cognito-identity','us-west-2')
        response = client.get_id(
            IdentityPoolId='us-west-2:%s' % identity_pool_id,
            Logins={'cognito-idp.us-west-2.amazonaws.com/%s' % user_pool_id : settings.value('aws_id_token','none')}
        )
        IdId = response['IdentityId']
        response = client.get_credentials_for_identity(
            IdentityId=IdId,
            Logins={'cognito-idp.us-west-2.amazonaws.com/%s' % user_pool_id : settings.value('aws_id_token','none')}
        )
        accessKey = response['Credentials']['AccessKeyId']
        secretKey = response['Credentials']['SecretKey']
        sessionTok = response['Credentials']['SessionToken']
        return [accessKey,secretKey,sessionTok]
    except Exception as msg:
        log(msg)

def getRemoteObjects(sub,tokens):
    try:
        [accessKey,secretKey,sessionToken] = tokens
        s3 = boto3.resource('s3',
            aws_access_key_id=accessKey,
            aws_secret_access_key=secretKey,
            aws_session_token=sessionToken
        )
        objects = []
        for x in s3.Bucket('huntstatslogger').objects.filter(Prefix='json/%s' % sub):
            objects.append(x)
        return objects
    except Exception as e:
        log(e)
        try:
            tkns = refresh_token()
            return getRemoteObjects(sub,tkns)
        except Exception as msg:
            log(msg)
            return []

def refresh_token():
    if settings.value('aws_refresh_token','') == '':
        return
    log('refreshing token')
    client = boto3.client("cognito-idp",region_name="us-west-2")
    try:
        response = client.initiate_auth(
            ClientId=client_id,
            AuthFlow="REFRESH_TOKEN",
            AuthParameters={
                "REFRESH_TOKEN":settings.value('aws_refresh_token','')
            }
        )
        settings.setValue('aws_access_token',response['AuthenticationResult']['AccessToken'])
        settings.setValue('aws_id_token',response['AuthenticationResult']['IdToken'])
    except client.exceptions.NotAuthorizedException as msg:
        log('refresh_token: not authorized\n%s' % msg)
    except Exception as msg:
        log(msg)

def isLoggedIn():
    return settings.value('aws_access_token','') != ''

def startThread(parent, instance, started=[],finished=[]):
    botoThread = QThread(parent=parent)
    instance.moveToThread(botoThread)
    for s in started:
        botoThread.started.connect(s)
    for f in finished:
        instance.finished.connect(f)
    botoThread.finished.connect(botoThread.quit)
    botoThread.finished.connect(instance.deleteLater)
    botoThread.finished.connect(botoThread.deleteLater)

    botoThread.start()

def getFromS3(key,file,tokens=None):
    if settings.value('aws_id_token','') == '':
        refresh_token()
        if settings.value('aws_id_token','') == '':
            return

    try:
        if tokens == None:
            tokens = getTokens()
        [accessKey,secretKey,sessionToken] = tokens
        
        session = boto3.Session(
            aws_access_key_id=accessKey,
            aws_secret_access_key=secretKey,
            aws_session_token=sessionToken
        )
        s3 = session.client('s3')
        obj = s3.get_object(
            Bucket='huntstatslogger',
            Key=key
        )
        data = json.loads(obj["Body"].read().decode('utf-8'))
        data = clean_data(translateJson(data,os.path.basename(file)))
        if not os.path.exists(os.path.dirname(file)):
            os.makedirs(os.path.dirname(file),exist_ok=True)
        with open(file,'w') as f:
            json.dump(data,f)


        log('got from s3')
        return True
    except Exception as msg1:
        log(msg1)
        try:
            refresh_token()
            log('token updated')
            return getFromS3(key,file,getTokens())
        except Exception as msg2:
            log(msg2)
            return False


def sendToS3(file,key,tokens=None):
    if not settings.value("aws_sub"):   return
    if settings.value('aws_id_token','') == '':
        refresh_token()
        if settings.value('aws_id_token','') == '':
            return

    log('sending %s to s3, key %s ' % (file, key))

    try:
        if tokens == None:
            tokens = getTokens()
        [accessKey,secretKey,sessionToken] = tokens
        
        session = boto3.Session(
            aws_access_key_id=accessKey,
            aws_secret_access_key=secretKey,
            aws_session_token=sessionToken
        )
        s3 = session.client('s3')
        s3.put_object(
            Body=open(file,'r').read(),
            Bucket='huntstatslogger',
            Key=key
        )
        log('sent to s3')
        return True
    except FileNotFoundError as msg:
        log(msg)
        return False
    except Exception as msg1:
        log('not authorized\n%s' % msg1)
        try:
            refresh_token()
            log('token updated')
            sendToS3(file,key,getTokens())
        except Exception as msg2:
            log('still not authorized\n%s' % msg2)
            return False

def ListRemoteFiles():
    pass

class ServerThread(QObject):
    finished = pyqtSignal(object)

    def __init__(self,args = None) -> None:
        super().__init__()
        self.args = args

    def syncFiles(self,tkns=None,localFiles=None,remoteFiles=None):
        log("syncing files with server")
        if not settings.value("aws_sub"):
            log("not logged in.")
            self.finished.emit("done")
            return
        if tkns == None:
            tkns = getTokens()
        if localFiles == None:
            localFiles = getLocalFiles()
        if remoteFiles == None:
            remoteFiles = getRemoteObjects(settings.value("aws_sub",""),tkns)

        if len(localFiles) == len(remoteFiles):
            log("nothing to do.")
            self.finished.emit("done")
            return

        local = {
            f.replace(app_data_path+'\\','').replace('\\','/') : f for f in localFiles
        }

        remote = {
            o.key : os.path.join(app_data_path,o.key.replace('/','\\')) for o in remoteFiles 
        }

        to_get = [k for k in remote.keys() if k not in local.keys() ]
        to_put = [k for k in local.keys() if k not in remote.keys() ]

        log('uploading %d files' % len(to_put))
        log('downloading %d files' % len(to_get))

        for k in to_put:
            sendToS3(local[k],k,tkns)
        for k in to_get:
            getFromS3(k,remote[k])
        self.finished.emit("done")

    def login(self):
        user = self.args['user']
        passwd = self.args['passwd']
        client = boto3.client("cognito-idp",region_name="us-west-2")

        try:
            response = client.initiate_auth(
                ClientId=client_id,
                AuthFlow="USER_PASSWORD_AUTH",
                AuthParameters={
                    "USERNAME":user,"PASSWORD":passwd
                }
            )
            response['username'] = user
            response['login'] = True
            self.finished.emit(response)
        except Exception as msg:
            self.finished.emit(msg)

    def signup(self):
        user = self.args['user']
        email = self.args['email']
        passwd = self.args['passwd']
        client = boto3.client("cognito-idp",region_name="us-west-2")
        try:
            response=client.sign_up(
                ClientId=client_id,
                Username=user,
                Password=passwd,
                UserAttributes=[
                    {"Name":"email","Value":email},
                    {"Name":"preferred_username","Value":user}
                ]
            )
            log('signing up')
            response['sign_up'] = 'success'
            self.finished.emit(response)
        except Exception as msg:
            self.finished.emit(msg)

    def verify(self):
        user = self.args['user']
        code = self.args['code']
        client = boto3.client("cognito-idp",region_name="us-west-2")
        try:
            response = client.confirm_sign_up(
                ClientId=client_id,
                Username=user,
                ConfirmationCode=code
            )
            response['verify'] = 'success'
            self.finished.emit(response)
        except Exception as msg:
            self.finished.emit(msg)
