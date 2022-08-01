import os
import boto3
from PyQt6.QtCore import QObject,pyqtSignal

client_id="5ek9jf37380g23qjbilbuh08hq"
identity_pool_id='af1647aa-3bf0-42ac-9a2d-9ed6558aadb7'
user_pool_id='us-west-2_NEhNwG197'

class Client(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(object)
    success = pyqtSignal(object)

    def __init__(self, args, parent=None):
        super().__init__(parent)
        self.args = args
        print('client init')

    def refresh_token(self):
        print('refreshing token')
        client = boto3.client("cognito-idp",region_name="us-west-2")
        try:
            response = client.initiate_auth(
                ClientId=client_id,
                AuthFlow="REFRESH_TOKEN",
                AuthParameters={
                    "REFRESH_TOKEN":self.settings.value('aws_refresh_token','')
                }
            )
            self.settings.setValue('aws_access_token',response['AuthenticationResult']['AccessToken'])
            self.settings.setValue('aws_id_token',response['AuthenticationResult']['IdToken'])
        except client.exceptions.NotAuthorizedException as msg:
            print('refresh_token: not authorized\n%s' % msg)
        except client.exceptions.UserNotFoundException as msg:
            print(msg)

    def signup(self):
        self.progress.emit('creating user')
        user = self.args['user']
        passwd = self.args['passwd']
        email = self.args['email']
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
            self.success.emit(response)
        except client.exceptions.InvalidParameterException as msg:
            self.progress.emit("invalid parameter exception")
        except client.exceptions.NotAuthorizedException as msg:
            self.progress.emit("not authorized exception")

    def sendToS3(self,filename):
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
                self.refresh_token()
                print('token updated')
                self.send_to_s3(filename)
            except client.exceptions.NotAuthorizedException as msg2:
                print('still not authorized\n%s' % msg2)

    def login(self):
        self.progress.emit('logging in')
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
            response['AuthenticationResult']['username'] = user
            self.progress.emit('')
            self.success.emit(response)

        except client.exceptions.InvalidParameterException as msg:
            self.progress.emit("invalid parameter exception")
        except client.exceptions.NotAuthorizedException as msg:
            self.progress.emit("not authorized exception")
            #self.progress.emit(str(msg))
        #self.finished.emit()