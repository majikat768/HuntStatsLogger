from PyQt6.QtWidgets import QMainWindow,QWidget,QTabWidget,QGridLayout,QGroupBox,QVBoxLayout,QLabel,QLineEdit,QPushButton
import boto3
from resources import *
import Server

class LoginWindow(QMainWindow):
    def __init__(self,parent):
        super().__init__(parent)
        self.loginWidget = Login(self,QVBoxLayout())
        self.setCentralWidget(self.loginWidget)

class Login(QWidget):
    def __init__(self,parent,layout):
        super().__init__(parent)
        self.setParent(parent)
        self.mainframe = parent.parent()
        self.layout = layout
        self.setLayout(self.layout)

        self.initUI()

    def initUI(self):
        self.tabs = QTabWidget()
        self.tabs.addTab(self.LoginTab(),"Login")
        self.tabs.addTab(self.SignupTab(),"Create User")
        self.layout.addWidget(self.tabs)

    def LoginTab(self):
        self.loginTab = QWidget()
        self.loginTab.layout = QGridLayout()
        self.loginTab.setLayout(self.loginTab.layout)
        self.loginTab.layout.addWidget(QLabel("Username:"),0,0)
        self.loginTab.layout.addWidget(QLabel("Password:"),1,0)
        self.loginUsernameInput = QLineEdit()
        self.loginUsernameInput.setFocus()
        self.loginPasswordInput = QLineEdit()
        self.loginPasswordInput.returnPressed.connect(self.submitLogin)
        self.loginPasswordInput.setEchoMode(QLineEdit.EchoMode.Password)
        self.loginTab.layout.addWidget(self.loginUsernameInput,0,1)
        self.loginTab.layout.addWidget(self.loginPasswordInput,1,1)

        self.loginButton = QPushButton("Login")
        self.loginButton.clicked.connect(self.submitLogin)
        self.loginButton.setAutoDefault(True)
        self.loginTab.layout.addWidget(self.loginButton,2,1,1,1)

        self.loginStatus = QLabel()
        self.loginTab.layout.addWidget(self.loginStatus,3,0,1,2)
        #self.loginTab.layout.setRowStretch(self.loginTab.layout.rowCount(),1)

        return self.loginTab

    def getSignupResponse(self,response):
        if type(response) == dict:
            if 'sign_up' in response and response['sign_up'] == 'success':
                self.signupStatus.setText("Check your email for a confirmation code.")
                self.VerifyWidget.show()
            elif 'verify' in response and response['verify'] == 'success':
                self.signupStatus.setText("You may now sign in.")
                self.VerifyWidget.hide()
        elif type(response) == boto3.client('cognito-idp',region_name="us-west-2").exceptions.UsernameExistsException:
            self.signupStatus.setText("Username already exists")
            self.signupButton.setDisabled(False)
        elif type(response) == boto3.client('cognito-idp',region_name="us-west-2").exceptions.InvalidParameterException:
            self.signupStatus.setText("Invalid username or password")
            self.signupButton.setDisabled(False)
        else:
            self.signupStatus.setText(str(response))
            self.signupButton.setDisabled(False)


    def getLoginResponse(self,response):
        if type(response) == dict:
            if 'login' in response and response['login'] == True:
                res = response['AuthenticationResult']
                settings.setValue("aws_access_token",res["AccessToken"])
                settings.setValue("aws_id_token",res["IdToken"])
                settings.setValue("aws_refresh_token",res["RefreshToken"])
                settings.setValue("aws_username",response["username"])
                Server.set_id()     # should also be a separate thread
                self.loginStatus.setText('')
                self.loginButton.setDisabled(False)
                self.mainframe.showLoggedIn()
                self.window().close()
        elif "NotAuthorizedException" in str(response):
            self.loginStatus.setText("Incorrect username or password")
            self.loginButton.setDisabled(False)
        else:
            self.loginStatus.setText("Something went wrong.")
            self.loginButton.setDisabled(False)

    def submitLogin(self):
        user = self.loginUsernameInput.text()
        passwd = self.loginPasswordInput.text()
        if user == '' or passwd == '':
            return
        self.serverThread = Server.ServerThread(args={'user':user,'passwd':passwd})
        Server.startThread(self,self.serverThread,started=[self.serverThread.login],finished=[self.getLoginResponse])
        self.loginStatus.setText("Logging in....")
        self.loginButton.setDisabled(True)

    def SignupTab(self):
        signupTab = QWidget()
        signupTab.layout = QGridLayout()
        signupTab.setLayout(signupTab.layout)

        signupTab.layout.addWidget(QLabel("Username:"),0,0)
        signupTab.layout.addWidget(QLabel("Email:"),1,0)
        signupTab.layout.addWidget(QLabel("Password:"),2,0)
        self.signupUsernameInput = QLineEdit()
        self.signupEmailInput = QLineEdit()
        self.signupPasswordInput = QLineEdit()
        self.signupPasswordInput.setEchoMode(QLineEdit.EchoMode.Password)
        signupTab.layout.addWidget(self.signupUsernameInput,0,1)
        signupTab.layout.addWidget(self.signupEmailInput,1,1)
        signupTab.layout.addWidget(self.signupPasswordInput,2,1)

        self.signupButton = QPushButton("Create User")
        self.signupButton.clicked.connect(self.submitSignup)
        signupTab.layout.addWidget(self.signupButton,3,1,1,1)
        self.signupStatus = QLabel()
        signupTab.layout.addWidget(self.signupStatus,4,0,1,2)

        self.VerifyWidget = QWidget()
        self.VerifyWidget.layout = QVBoxLayout() 
        self.VerifyWidget.setLayout(self.VerifyWidget.layout) 
        self.verifyInput = QLineEdit()
        verifyButton = QPushButton("Verify")
        verifyButton.clicked.connect(self.verify)
        self.VerifyWidget.layout.addWidget(self.verifyInput)
        self.VerifyWidget.layout.addWidget(verifyButton)
        self.VerifyWidget.hide()

        signupTab.layout.addWidget(self.VerifyWidget,5,0,1,2)

        signupTab.layout.setRowStretch(signupTab.layout.rowCount(),1)

        return signupTab

    def submitSignup(self):
        print('submit.signup')
        user = self.signupUsernameInput.text()
        email = self.signupEmailInput.text()
        passwd = self.signupPasswordInput.text()
        print(user,email,passwd)
        if user == '' or passwd == '' or email == '':
            return
        log('creating user %s' % user)
        self.serverThread = Server.ServerThread(args={'user':user,'email':email,'passwd':passwd})
        Server.startThread(self,self.serverThread,started=[self.serverThread.signup],finished=[self.getSignupResponse])
        self.signupStatus.setText("Creating user....")
        self.signupButton.setDisabled(True)

    def verify(self):
        user = self.signupUsernameInput.text()
        code = self.verifyInput.text()
        if user == '' or code == '':    return

        self.serverThread = Server.ServerThread(args={'user':user,'code':code})
        Server.startThread(self,self.serverThread,started=[self.serverThread.verify],finished=[self.getSignupResponse])
        self.signupStatus.setText("Verifying....")
        self.signupButton.setDisabled(True)