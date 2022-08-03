from PyQt6.QtWidgets import QLineEdit,QLabel,QPushButton,QWidget,QVBoxLayout,QGridLayout,QTabWidget
import boto3
from GroupBox import GroupBox
from resources import *
import Client

class Login(GroupBox):
    def __init__(self, parent, layout):
        super().__init__(layout)
        self.setParent(parent)
        self.settingsWidget = self.parent()
        self.tabs = QTabWidget()
        self.tabs.addTab(self.initLoginTab(),"Login")
        self.tabs.addTab(self.initSignupTab(),"Sign Up")
        self.layout.addWidget(self.tabs)

    def initLoginTab(self):
        self.loginTab = GroupBox(QGridLayout(),"Login")
        self.loginTab.layout.addWidget(QLabel("Username:"),0,0)
        self.loginTab.layout.addWidget(QLabel("Password:"),1,0)
        self.loginUsernameInput = QLineEdit()
        self.loginEmailInput = QLineEdit()
        self.loginPasswordInput = QLineEdit()
        self.loginPasswordInput.setEchoMode(QLineEdit.EchoMode.Password)
        self.loginTab.layout.addWidget(self.loginUsernameInput,0,1)
        self.loginTab.layout.addWidget(self.loginPasswordInput,1,1)

        self.loginButton = QPushButton("Login")
        self.loginButton.clicked.connect(self.submitLogin)
        self.loginTab.layout.addWidget(self.loginButton,2,1,1,1)

        self.loginStatus = QLabel()
        self.loginTab.layout.addWidget(self.loginStatus,3,0,1,2)
        self.loginTab.layout.setRowStretch(self.layout.rowCount(),1)

        return self.loginTab

    def initSignupTab(self):
        self.signupTab = GroupBox(QGridLayout(),"Sign Up")
        self.signupTab.layout.addWidget(QLabel("Username:"),0,0)
        self.signupTab.layout.addWidget(QLabel("Email:"),1,0)
        self.signupTab.layout.addWidget(QLabel("Password:"),2,0)
        self.signupUsernameInput = QLineEdit()
        self.signupEmailInput = QLineEdit()
        self.signupPasswordInput = QLineEdit()
        self.signupPasswordInput.setEchoMode(QLineEdit.EchoMode.Password)
        self.signupTab.layout.addWidget(self.signupUsernameInput,0,1)
        self.signupTab.layout.addWidget(self.signupEmailInput,1,1)
        self.signupTab.layout.addWidget(self.signupPasswordInput,2,1)

        self.signupButton = QPushButton("Sign Up")
        self.signupButton.clicked.connect(self.submitSignup)
        self.signupTab.layout.addWidget(self.signupButton,3,1,1,1)
        self.signupStatus = QLabel()
        self.signupTab.layout.addWidget(self.signupStatus,4,0,1,2)

        self.VerifyWidget = QWidget()
        self.VerifyWidget.layout = QVBoxLayout() 
        self.VerifyWidget.setLayout(self.VerifyWidget.layout) 
        self.verifyInput = QLineEdit()
        verifyButton = QPushButton("Verify")
        verifyButton.clicked.connect(self.verify)
        self.VerifyWidget.layout.addWidget(self.verifyInput)
        self.VerifyWidget.layout.addWidget(verifyButton)
        self.VerifyWidget.hide()

        self.signupTab.layout.addWidget(self.VerifyWidget,5,0,1,2)

        self.signupTab.layout.setRowStretch(self.layout.rowCount(),1)

        return self.signupTab

    def setLoginStatus(self,response):
        if type(response) == dict:
            if 'login' in response and response['login'] == True:
                res = response["AuthenticationResult"]
                settings.setValue("aws_access_token",res["AccessToken"])
                settings.setValue("aws_id_token",res["IdToken"])
                settings.setValue("aws_refresh_token",res["RefreshToken"])
                settings.setValue("aws_username",response["username"])
                Client.set_id()
                self.loginStatus.setText('')
                self.loginButton.setDisabled(False)
                self.settingsWidget.showLoggedIn()
                self.window().close()

                self.botocall = Client.BotoCall()
        else:
            self.loginStatus.setText("Something went wrong.")
            self.loginButton.setDisabled(False)


    def setSignupStatus(self,response):
        print('response',response)
        if response == "signup_success":
            self.signupStatus.setText("Check your email for a confirmation code.")
            self.VerifyWidget.show()
        elif response == "verification_success":
            self.signupStatus.setText("You may now sign in.")
            self.VerifyWidget.hide()
            self.signupButton.setDisabled(False)
        elif type(response) == boto3.client('cognito-idp',region_name="us-west-2").exceptions.UsernameExistsException:
            self.signupStatus.setText("Username already exists")
            self.signupButton.setDisabled(False)
        elif type(response) == boto3.client('cognito-idp',region_name="us-west-2").exceptions.InvalidParameterException:
            self.signupStatus.setText("Invalid username or password")
            self.signupButton.setDisabled(False)
        else:
            self.signupStatus.setText(str(response))
            self.signupButton.setDisabled(False)



    def submitLogin(self):
        user = self.loginUsernameInput.text()
        log('logging in as %s' % user)
        passwd = self.loginPasswordInput.text()
        if user == '' or passwd == '':  return

        self.botocall = Client.BotoCall({'user':user,'passwd':passwd})
        Client.startThread(self,self.botocall,started=[self.botocall.login],progress=[self.setLoginStatus])
        self.loginStatus.setText("Logging in....")
        self.loginButton.setDisabled(True)

    def submitSignup(self):
        user = self.signupUsernameInput.text()
        passwd = self.signupPasswordInput.text()
        email = self.signupEmailInput.text()
        if email == '' or user == '' or passwd == '':  return

        self.botocall = Client.BotoCall({'user':user,'email':email,'passwd':passwd})
        Client.startThread(
            self, self.botocall,
            started=[self.botocall.signup],
            progress=[self.setSignupStatus]
        )
        self.signupStatus.setText("Creating user....")
        self.signupButton.setDisabled(True)


    def verify(self):
        user = self.signupUsernameInput.text()
        code = self.verifyInput.text()
        if user == '' or code == '':    return

        self.botocall = Client.BotoCall({'user':user,'code':code})
        Client.startThread(
            self, self.botocall,
            started=[self.botocall.verify],
            progress=[self.setSignupStatus]
        )

        self.signupStatus.setText("verifying email....")
        self.VerifyWidget.hide()
