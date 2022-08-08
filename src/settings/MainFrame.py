import os
from PyQt6.QtWidgets import QWidget,QFileDialog,QPushButton,QLabel,QHBoxLayout,QGroupBox,QVBoxLayout,QSizePolicy,QMainWindow, QInputDialog,QWIDGETSIZE_MAX,QLineEdit,QCheckBox
from PyQt6.QtCore import Qt
from util.HunterLabel import HunterLabel
from settings.LoginWindow import LoginWindow
from resources import *
import Server 
from settings import Logger
from viewer import DbHandler

class MainFrame(QWidget):
    def __init__(self, parent, layout):
        super().__init__(parent)
        self.layout = layout
        self.setLayout(self.layout)

        self.initUI()

    def toggle(self):
        if self.main.isVisible():
            self.main.hide()
            self.window().setMinimumHeight(self.layout.sizeHint().height())
            self.window().setMaximumHeight(self.layout.sizeHint().height()+self.parent().statusBar().height()*2)
            self.parent().adjustSize()
        else:
            self.main.show()
            self.window().setMinimumHeight(0)
            self.window().setMaximumHeight(QWIDGETSIZE_MAX)
            self.parent().adjustSize()

        return

    def initUI(self):
        self.main = QWidget()
        self.main.layout = QVBoxLayout()
        self.main.setLayout(self.main.layout)

        self.huntFolderGroup = self.initSelectHuntDirGroup()

        self.loginGroup = self.initLoginGroup()

        self.startLoggerGroup = self.initLoggerGroup()

        tools = QWidget()
        tools.layout = QVBoxLayout()
        tools.setLayout(tools.layout)

        self.hideUsersToggle = QCheckBox('Hide usernames')
        self.hideUsersToggle.stateChanged.connect(self.ToggleUsers)

        tools.layout.addWidget(self.hideUsersToggle)
        tools.layout.addStretch()

        self.main.layout.addWidget(self.huntFolderGroup)
        self.main.layout.addWidget(QLabel())
        self.main.layout.addWidget(self.startLoggerGroup)
        self.main.layout.addWidget(QLabel())
        self.main.layout.addWidget(self.loginGroup)
        self.main.layout.addWidget(QLabel())

        self.main.layout.addWidget(tools)

        self.layout.addWidget(self.main)
        self.setStatus("Logger not active.")

    def initLoggerGroup(self):
        loggerGroup = QGroupBox("Logger") 
        loggerGroup.setFlat(False)
        loggerGroup.layout = QVBoxLayout()
        loggerGroup.setLayout(loggerGroup.layout)

        self.setSteamNameButton = QPushButton("Set Steam Name")
        self.setSteamNameButton.clicked.connect(self.setUsername)
        self.setSteamNameButton.setSizePolicy(QSizePolicy.Policy.Fixed,QSizePolicy.Policy.Fixed)

        self.loggerLabel = QLabel("Logger not active.")
        self.startLoggerButton = QPushButton("Start Logging")
        if not settings.value('xml_path'):
            self.startLoggerButton.setDisabled(True)
        self.startLoggerButton.setSizePolicy(QSizePolicy.Policy.Maximum,QSizePolicy.Policy.Maximum)
        self.stopLoggerButton = QPushButton("Stop Logging")
        self.startLoggerButton.clicked.connect(self.startLogger)
        self.stopLoggerButton.clicked.connect(self.stopLogger)
        self.stopLoggerButton.setSizePolicy(QSizePolicy.Policy.Maximum,QSizePolicy.Policy.Maximum)
        self.stopLoggerButton.hide()

        loggerGroup.layout.addWidget(self.setSteamNameButton)
        loggerGroup.layout.addWidget(self.loggerLabel)
        loggerGroup.layout.addWidget(self.startLoggerButton)
        loggerGroup.layout.addWidget(self.stopLoggerButton)

        return loggerGroup
    
    def initSelectHuntDirGroup(self):
        huntFolderGroup = QGroupBox("Hunt Install Directory")
        huntFolderGroup.setFlat(False)
        huntFolderGroup.layout = QVBoxLayout()
        huntFolderGroup.setLayout(huntFolderGroup.layout)

        self.huntFolderButton = QPushButton("Select Hunt Installation Directory")
        self.huntFolderButton.clicked.connect(self.SelectHuntFolderDialog)
        self.huntFolderLabel = QLabel()
        self.huntFolderLabel.setStyleSheet("QLabel{font-size:12px;font-family:courier new;}")
        self.huntFolderLabel.setText(settings.value("hunt_dir"))

        if settings.value("xml_path"):
            self.huntFolderLabel.show()
            self.huntFolderButton.setText("Change")
        else:
            self.huntFolderLabel.hide()
            self.huntFolderButton.show()
        self.huntFolderButton.setSizePolicy(QSizePolicy.Policy.Maximum,QSizePolicy.Policy.Maximum)
        huntFolderGroup.layout.addWidget(self.huntFolderLabel)
        huntFolderGroup.layout.addWidget(self.huntFolderButton)
        return huntFolderGroup

    def initLoginGroup(self):
        self.loginWindow = LoginWindow(self)
        loginGroup = QGroupBox("Login")
        loginGroup.setFlat(False)
        loginGroup.layout = QVBoxLayout()
        loginGroup.setLayout(loginGroup.layout)

        self.loginLabel = QLabel()
        self.loginButton = QPushButton("Login / Create User")
        self.loginButton.clicked.connect(self.loginWindow.show)
        self.logoutButton = QPushButton("Logout")
        self.logoutButton.setSizePolicy(QSizePolicy.Policy.Maximum,QSizePolicy.Policy.Maximum)
        self.logoutButton.clicked.connect(self.logout) 
        if not settings.value("xml_path"):
            self.loginButton.setDisabled(True)
        self.logoutButton.hide()
        if isLoggedIn():
            self.loginLabel.setText("Logged in as %s" % settings.value("aws_username"))
            self.loginButton.hide()
            self.logoutButton.show()
        else:
            self.loginLabel.setText("Not logged in.")
            self.loginButton.show()
            self.logoutButton.hide()

        self.syncServerButton = QPushButton("Sync with Server")
        if not isLoggedIn():
            self.syncServerButton.setDisabled(True)
        self.syncServerButton.clicked.connect(self.syncServer)
        self.syncServerButton.setSizePolicy(QSizePolicy.Policy.Fixed,QSizePolicy.Policy.Fixed)

        loginGroup.layout.addWidget(self.loginLabel)
        loginGroup.layout.addWidget(self.loginButton)
        loginGroup.layout.addWidget(self.logoutButton)
        loginGroup.layout.addWidget(self.syncServerButton)

        return loginGroup

    def ToggleUsers(self):
        HunterLabel.HideUsers = not HunterLabel.HideUsers
        HunterLabel.ToggleNames()
        self.parent().viewerMainframe.huntsTab.updateTeamDetails()

    def setStatus(self,text):
        self.parent().setStatus(text)

    def setUsername(self):
        name,_ = QInputDialog.getText(self,"Enter steam name", "Name:",QLineEdit.EchoMode.Normal,settings.value("steam_name"))
        if name != '':
            settings.setValue("steam_name",name)
            log("steam name set to %s" % name)
            settings.setValue('profileid',DbHandler.getProfileid(name))
            self.parent().viewerMainframe.update()

    def syncServer(self):
        if not isLoggedIn():    return
        self.stopLogger()
        self.serverThread = Server.ServerThread()
        Server.startThread(self,self.serverThread,started=[self.serverThread.syncFiles],progress=[self.updateSync],finished=[self.doneSyncing])
        self.syncServerButton.setDisabled(True)
        self.syncServerButton.setText("Syncing files.....")
    
    def doneSyncing(self):
        self.syncServerButton.setDisabled(False)
        self.syncServerButton.setText("Sync with Server")
        self.syncDb()

    def syncDb(self):
        log('syncing db')
        self.dbHandler = DbHandler.DbHandler()
        dbThread = QThread(parent=self)
        self.dbHandler.moveToThread(dbThread)
        DbHandler.running = True
        dbThread.started.connect(self.dbHandler.syncDb)
        self.dbHandler.finished.connect(dbThread.quit)
        self.dbHandler.finished.connect(self.dbHandler.deleteLater)
        self.dbHandler.finished.connect(self.parent().viewerMainframe.update)
        self.dbHandler.progress.connect(self.update)
        dbThread.start()



    def updateSync(self,msg):
        self.syncServerButton.setText(msg)


    def logout(self):
        settings.remove('aws_access_token')
        settings.remove('aws_refresh_token')
        settings.remove('aws_id_token')
        settings.remove('aws_username')
        settings.remove('aws_sub')
        self.loginLabel.setText("Not logged in.")
        self.logoutButton.hide()
        self.loginButton.show()
        self.syncServerButton.setDisabled(True)

    def showLoggedIn(self):
        self.startLoggerButton.setDisabled(False)
        self.loginButton.hide()
        self.logoutButton.show()
        self.loginLabel.setText("Logged in as %s" % settings.value("aws_username"))
        self.setStatus("Ready.")
        self.syncServerButton.setDisabled(False)

    def addWidget(self,widget):
        self.layout.addWidget(widget)

    def SelectHuntFolderDialog(self):
        suffix = 'user/profiles/default/attributes.xml'
        hunt_dir = QFileDialog.getExistingDirectory(self,"Select folder",settings.value('hunt_dir','.'))
        xml_path = os.path.join(hunt_dir,suffix)
        if not os.path.exists(xml_path):
            log("attributes.xml file not found.")
            self.setStatus("attributes.xml not found.")
            return
        settings.setValue('xml_path',xml_path)
        settings.setValue('hunt_dir',hunt_dir)
        log('path set to %s' % xml_path)
        self.huntFolderLabel.setText(hunt_dir)
        self.huntFolderLabel.show()
        self.huntFolderButton.setText("Change")
        self.loginButton.setDisabled(False)
        self.startLoggerButton.setDisabled(False)
        self.window().adjustSize()

    def startLogger(self):
        self.logger = Logger.Logger(self)
        Logger.running = True
        StartLogger(self.logger,self)
        self.startLoggerButton.hide()
        self.stopLoggerButton.show() 
        self.loggerLabel.setText("Logger active.")
        if settings.value("profileid","-1") == "-1":
            if settings.value("steam_name"):
                settings.setValue('profileid',DbHandler.getProfileid(settings.value("steam_name")))
        
    def stopLogger(self):
        Logger.running = False
        self.stopLoggerButton.hide() 
        self.startLoggerButton.show()
        self.loggerLabel.setText("Logger not active.")
