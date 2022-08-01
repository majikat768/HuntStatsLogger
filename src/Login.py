from PyQt6.QtWidgets import QLineEdit,QLabel,QPushButton,QWidget,QVBoxLayout,QGridLayout,QTabWidget
import boto3
from GroupBox import GroupBox

client_id="5ek9jf37380g23qjbilbuh08hq"

class Login(GroupBox):
    def __init__(self, parent, layout):
        super().__init__(layout)
        self.parent = parent
        self.settings = self.parent.settings
        self.connection = parent.connection
        self.client = parent.client

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
        #self.loginButton.clicked.connect(lambda : self.setLoginStatus("logging in"))
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

        signupButton = QPushButton("Sign Up")
        signupButton.clicked.connect(self.submitSignup)
        self.signupTab.layout.addWidget(signupButton,3,1,1,1)
        self.signupStatus = QLabel()
        self.signupTab.layout.addWidget(self.signupStatus,4,0,1,2)

        self.VerifyWidget = QWidget()
        self.VerifyWidget.layout = QVBoxLayout() 
        self.VerifyWidget.setLayout(self.VerifyWidget.layout) 
        self.VerifyWidget.layout.addWidget(QLabel("Check your email for verification code"))
        self.verifyInput = QLineEdit()
        verifyButton = QPushButton("Verify")
        verifyButton.clicked.connect(self.verify)
        self.VerifyWidget.layout.addWidget(self.verifyInput)
        self.VerifyWidget.layout.addWidget(verifyButton)
        self.VerifyWidget.hide()

        self.signupTab.layout.addWidget(self.VerifyWidget,4,0,1,2)

        self.signupTab.layout.setRowStretch(self.layout.rowCount(),1)

        return self.signupTab

    def setLoginStatus(self,text):
        self.loginStatus.setText(text)

    def setSignupStatus(self,text):
        self.signupStatus.setText(text)

    def submitLogin(self):
        user = self.loginUsernameInput.text()
        passwd = self.loginPasswordInput.text()
        if user == '' or passwd == '':  return
        try:
            response = self.client.login(user,passwd)
            if type(response) == dict and 'AuthenticationResult' in response:
                self.settings.setValue('aws_access_token',response['AuthenticationResult']['AccessToken'])
                self.settings.setValue('aws_id_token',response['AuthenticationResult']['IdToken'])
                self.settings.setValue('aws_refresh_token',response['AuthenticationResult']['RefreshToken'])
                self.settings.setValue('aws_username',response['AuthenticationResult']['username'])
                self.parent.showLoggedIn(response)
                self.window().close()
        
        except Exception as msg:
            print('something happened')
            print(msg)

    def submitSignup(self):
        user = self.signupUsernameInput.text()
        passwd = self.signupPasswordInput.text()
        email = self.signupEmailInput.text()
        if email == '' or user == '' or passwd == '':  return
        response = self.client.signup(user,email,passwd)
        print(response)
        if type(response) != dict:
            print('exception!')
        else:
            self.VerifyWidget.show()

        

    def verify(self):
        client = boto3.client("cognito-idp",region_name="us-west-2")
        response = client.confirm_sign_up(
            ClientId=client_id,
            Username=self.signupUsernameInput.text(),
            ConfirmationCode=self.verifyInput.text()
        )
        self.VerifyWidget.hide()
