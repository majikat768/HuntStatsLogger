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

def getRemoteFiles(sub,tokens):
    try:
        [accessKey,secretKey,sessionToken] = tokens
        s3 = boto3.resource('s3',
            aws_access_key_id=accessKey,
            aws_secret_access_key=secretKey,
            aws_session_token=sessionToken
        )
        files = []
        for x in s3.Bucket('huntstatslogger').objects.filter(Prefix='json/%s' % sub):
            files.append(x)
        return files
    except Exception as e:
        log(e)
        try:
            refresh_token()
            return getRemoteFiles(sub)
        except Exception as msg:
            log(msg)

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

def startThread(parent, instance, started=[],finished=[],progress=[]):
    botoThread = QThread(parent=parent)
    instance.moveToThread(botoThread)
    for s in started:
        botoThread.started.connect(s)
    for f in finished:
        instance.finished.connect(f)
    for p in progress:
        instance.progress.connect(p)
    botoThread.finished.connect(botoThread.quit)
    botoThread.finished.connect(instance.deleteLater)
    botoThread.finished.connect(botoThread.deleteLater)

    botoThread.start()

def getFromS3(obj,outputFile,tokens=None):
    log('downloading %s to %s' % (obj.key,outputFile))
    os.makedirs(os.path.dirname(outputFile),exist_ok=True)
    try:
        #[accessKey, secretKey, sessionToken] = tokens
        output=obj.get()['Body']
        dat = json.loads(output.read().decode('utf-8'))
        dat = clean_json(translateJson(dat))
        with open(outputFile,'w') as f:
            json.dump(dat,f)

    except Exception as msg:
        log(msg)

def sendToS3(filename,tokens=None):
    if settings.value('aws_id_token','') == '':
        refresh_token()
        if settings.value('aws_id_token','') == '':
            return
    key = str(filename)
    key = key.replace('hunterX',settings.value("aws_sub","hunterX"))
    key =key.replace(app_data_path+'\\','').replace('\\','/')
    log('sending %s to s3, key %s ' % (filename, key))
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
            Body=open(filename,'r').read(),
            Bucket='huntstatslogger',
            Key=key
        )
        log('sent to s3')
    except FileNotFoundError as msg:
        log(msg)
    except Exception as msg1:
        log('not authorized\n%s' % msg1)
        try:
            refresh_token()
            log('token updated')
            sendToS3(filename,getTokens())
        except Exception as msg2:
            log('still not authorized\n%s' % msg2)



class BotoCall(QObject):
    progress = pyqtSignal(object)
    finished = pyqtSignal()

    def __init__(self,args = None) -> None:
        super().__init__()
        self.args = args

    def syncFiles(self,tkns=None,local=None,remote=None):
        if tkns == None:
            tkns = getTokens()
        if local == None:
            local = getLocalFiles()
        if remote == None:
            remote = getRemoteFiles(settings.value("aws_sub",""),tkns)
        log('syncing files')
        localFileNames = [f.replace(app_data_path+'\\','') for f in local]
        remoteFileNames = [ obj.key.replace('/','\\') for obj in remote]
        to_upload = []
        to_download = []
        for f in localFileNames:
            if f not in remoteFileNames:
                to_upload.append(f)
        for obj in remote:
            if obj.key.replace('/','\\') not in localFileNames:
                to_download.append(obj)
        log('uploading %d files' % len(to_upload))
        log('downloading %d files' % len(to_download))

        for f in to_upload:
            sendToS3(os.path.join(app_data_path,f),tkns)
        for obj in to_download:
            getFromS3(obj,os.path.join(app_data_path,obj.key),tkns)
        self.finished.emit()

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
            self.progress.emit(response)
        except Exception as msg:
            self.progress.emit(msg)
        self.finished.emit()

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
            self.progress.emit("signup_success")
        except Exception as msg:
            self.progress.emit(msg)
        self.finished.emit()

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
            self.progress.emit("verification_success")
        except Exception as msg:
            self.progress.emit(msg)
        self.finished.emit()
