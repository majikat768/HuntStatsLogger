from re import I
import json
from PyQt6.QtWidgets import QPushButton,QLineEdit,QFileDialog, QWidget, QVBoxLayout,QGridLayout,QComboBox, QLabel,QCheckBox,QMainWindow,QSizePolicy
import Connection
import Client
from PyQt6.QtCore import Qt
import os
from Connection import unix_to_datetime
from GroupBox import GroupBox
from HunterLabel import HunterLabel
from Login import Login
from resources import *
from threading import Thread
from Logger import Logger

class Settings(GroupBox):
    def __init__(self, parent,layout):
        super().__init__(layout)
        self.setParent(parent)
        print(self.parent())
        self.mainframe = self.parent()
        self.layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.setSpacing(20)
        self.setStyleSheet("#box{border: 1px solid #999999;}")
        self.layout.addWidget(self.HuntInstallBox())
        
        self.layout.addWidget(self.initLoginBox())

        self.layout.addWidget(self.SteamNameBox())

        self.layout.addWidget(self.optionsBox())
        self.layout.addWidget(self.devOptionsBox())

    def HuntInstallBox(self):
        box = QWidget()
        box.setObjectName('box')
        box.layout = QGridLayout()
        box.setLayout(box.layout)
        box.layout.addWidget(QLabel('Hunt Installation Directory:'),0,0,1,2)
        self.huntDirButton = QPushButton('Select Folder')
        self.huntDirButton.setSizePolicy(QSizePolicy.Policy.Fixed,QSizePolicy.Policy.Fixed) 
        self.huntDirButton.clicked.connect(self.SelectHuntFolder)
        self.huntDirQLabel = QLabel(settings.value('huntDir','none'))
        self.huntDirQLabel.setStyleSheet("QLabel{font-size:12px;font-family:courier new;}")
        self.huntDirQLabel.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter) 
        box.layout.addWidget(self.huntDirButton,1,0)
        box.layout.addWidget(self.huntDirQLabel,1,1)
        return box

    def SteamNameBox(self):
        box = QWidget()
        box.setObjectName('box')
        box.layout = QGridLayout()
        box.setLayout(box.layout)
        self.nameInputButton = QPushButton('Change Steam Name')
        self.nameInputButton.setSizePolicy(QSizePolicy.Policy.Fixed,QSizePolicy.Policy.Fixed) 
        self.nameInput = QLineEdit(settings.value('hunterName',''))
        self.nameLabel = QLabel(settings.value('hunterName',''))
        self.nameLabel.setStyleSheet("QLabel{font-size:16px;font-family:courier new;}")
        self.nameLabel.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter) 
        self.nameInput.setPlaceholderText('Enter your Steam username')
        self.nameInput.hide()
        self.nameInputButton.clicked.connect(self.UpdateHunterName)
        self.nameInput.returnPressed.connect(self.UpdateHunterName)
        box.layout.addWidget(self.nameInput,0,1,1,1)
        box.layout.addWidget(self.nameLabel,0,1,1,1)
        box.layout.addWidget(self.nameInputButton,0,0,1,1)
        return box

    def optionsBox(self):
        box = QWidget()
        box.setObjectName('box')
        box.layout = QVBoxLayout()
        box.setLayout(box.layout)
        hideUsers = QCheckBox('Hide usernames')
        hideUsers.stateChanged.connect(self.hideUserToggle)
        box.layout.addWidget(hideUsers)

        HeaderOnly = QCheckBox('Show only header bar')
        HeaderOnly.stateChanged.connect(self.HeaderToggle)
        box.layout.addWidget(HeaderOnly)
        return box

    def devOptionsBox(self):
        box = QWidget()
        box.setObjectName('box')
        box.layout = QGridLayout()
        box.setLayout(box.layout)
        box.layout.addWidget(QLabel('dev stuff:'),0,0)
        importJsonButton = QPushButton('Import json files')
        importJsonButton.setSizePolicy(QSizePolicy.Policy.Fixed,QSizePolicy.Policy.Fixed) 
        importJsonButton.clicked.connect(self.ImportJsonThread)
        box.layout.addWidget(importJsonButton,1,0)
        importJsonButton.setDisabled(False)

        deleteRecordButton = QPushButton('Delete a record....')
        deleteRecordButton.setSizePolicy(QSizePolicy.Policy.Fixed,QSizePolicy.Policy.Fixed) 
        deleteRecordButton.clicked.connect(self.DeleteRecordDialog)
        deleteRecordButton.setDisabled(True)
        box.layout.addWidget(deleteRecordButton,1,1)

        return box



    def initLoginBox(self):
        loginBox = QWidget()
        loginBox.setObjectName('box')
        loginBox.layout = QVBoxLayout()
        loginBox.setLayout(loginBox.layout)

        self.loginWindow = self.initLoginWindow()
        self.loginButton = QPushButton("Login / Create Account")
        self.loginButton.clicked.connect(self.loginWindow.show)
        self.loginButton.clicked.connect(self.isLoggedIn)
        self.loginButton.setSizePolicy(QSizePolicy.Policy.Fixed,QSizePolicy.Policy.Fixed)
        self.LoggedIn = QLabel("Logged in as %s" % settings.value('aws_username'))
        loginBox.layout.addWidget(self.LoggedIn)
        self.logoutButton = QPushButton("Logout")
        self.logoutButton.setSizePolicy(QSizePolicy.Policy.Fixed,QSizePolicy.Policy.Fixed)
        self.logoutButton.clicked.connect(self.logout)
        self.syncServerButton = QPushButton("Sync files with server")
        self.syncServerButton.setSizePolicy(QSizePolicy.Policy.Fixed,QSizePolicy.Policy.Fixed)
        self.syncServerButton.clicked.connect(self.syncFilesThread)
        loginBox.layout.addWidget(self.logoutButton)
        loginBox.layout.addWidget(self.syncServerButton)
        loginBox.layout.addWidget(self.loginButton)
        if self.isLoggedIn():
            self.logoutButton.show()
            self.syncServerButton.show()
            self.loginButton.hide()
        else:
            self.LoggedIn.setText("Not logged in.")
            self.logoutButton.hide()
            self.syncServerButton.hide()
            self.loginButton.show()
        return loginBox

    def isLoggedIn(self):
        if settings.value('aws_access_token','') == '':
            return False
        return Client.isLoggedIn()

    def showLoggedIn(self):
        self.LoggedIn.setText("Logged in as %s" % settings.value('aws_username'))
        self.mainframe.showLoggedIn()
        self.logoutButton.show()
        self.syncServerButton.show()
        self.loginButton.hide()

    def logout(self):
        settings.remove('aws_access_token')
        settings.remove('aws_refresh_token')
        settings.remove('aws_id_token')
        settings.remove('aws_username')
        settings.remove('aws_sub')
        self.LoggedIn.setText("Not logged in.")
        self.mainframe.showLoggedIn()
        self.logoutButton.hide()
        self.syncServerButton.hide()
        self.loginButton.show()


    def initLoginWindow(self):
        loginBox = Login(self,QGridLayout())

        loginWindow = QMainWindow(self)
        loginWindow.setWindowFlags(loginWindow.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)
        loginWindow.setCentralWidget(loginBox)
        return loginWindow

    def HeaderToggle(self):
        self.mainframe.ToggleBoxes()

    def hideUserToggle(self):
        HunterLabel.HideUsers = not HunterLabel.HideUsers 
        HunterLabel.ToggleNames()

    def DeleteRecordDialog(self):
        self.window = QWidget()
        self.window.layout = QVBoxLayout()
        self.window.setLayout(self.window.layout)

        select = QComboBox()
        select.setStyleSheet('QComboBox{padding:8px;}')
        for timestamp in self.connection.GetAllTimestamps():
            select.addItem('%s' % unix_to_datetime(timestamp),timestamp)
        button = QPushButton('select a record to delete')
        button.setStyleSheet('QPushButton{padding:8px;}')
        button.clicked.connect(lambda: self.connection.deleteRecord(select.currentData()))
        button.clicked.connect(self.updateMatchSelect)

        
        self.window.layout.addWidget(select)
        self.window.layout.addWidget(button)
        self.window.show()

    def close(self) -> bool:
        self.hide()
        #return super().close()

    def updateMatchSelect(self):
        self.window.deleteLater()
        self.window.close()

    # since I changed how the jsons are formatted,
    # have to add a 'translation' function here before import will work.


    def ImportJson(self):
        directory = QFileDialog.getExistingDirectory(self,"select directory (files must be named as 'attributes_#####.json)",'.')
        files = os.listdir(directory)
        tokens = Client.getTokens()
        for file in files:
            path = os.path.join(directory,file)
            if os.path.isfile(path):
                try:
                    with open(path,'r') as f:
                        data = json.load(f)
                    if 'game' in data.keys() and 'hunter' in data.keys() and 'entry' in data.keys() and 'team' in data.keys(): 
                        data = clean_json(translateJson(data))
                    print(file)
                    timestamp = int(file.split('_')[1].split('.')[0])
                    y = datetime.fromtimestamp(timestamp).strftime('%Y')
                    m = datetime.fromtimestamp(timestamp).strftime('%m')
                    d = datetime.fromtimestamp(timestamp).strftime('%d')
                    outdir = os.path.join(settings.value('aws_sub','hunter'),y,m,d) 
                    os.makedirs(os.path.join(jsondir,outdir),exist_ok=True)
                    outfile = os.path.join(outdir,file)
                    with open(os.path.join(jsondir,outfile),'w') as newfile:
                        json.dump(data,newfile)
                    Connection.write_json_to_sql(os.path.join(jsondir,outfile))
                    Client.sendToS3(outfile.replace("\\","/"),tokens)
                except:
                    continue
        print('files imported')

    def setSyncStatus(self):
        Connection.syncDb()
        self.mainframe.update()
        self.syncServerButton.setText("Sync files with server")
        self.syncServerButton.setDisabled(False)


    def syncFilesThread(self):
        self.botoCall = Client.BotoCall()
        Client.startThread(
            self,self.botoCall,started=[self.botoCall.syncFiles],progress=[],finished=[self.setSyncStatus]
        )
        self.syncServerButton.setText("syncing....")
        self.syncServerButton.setDisabled(True)

    def ImportJsonThread(self):
        thread = Thread(target=self.ImportJson)
        thread.start()

    def SelectHuntFolder(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Hunt Installation Directory",settings.value('huntDir','.'))
        if directory != '':
            print('directory set to %s' % directory)
            settings.setValue('huntDir',directory)
            self.huntDirQLabel.setText(settings.value('huntDir',''))
            StartLogger(self.mainframe.logger,self.mainframe)
            self.mainframe.settingsButton.setText('Settings')
            self.mainframe.hunterBox.show()
            self.mainframe.tabs.show()
            self.mainframe.window().setMinimumWidth(self.layout.sizeHint().width())
            self.mainframe.update()

    def UpdateHunterName(self):
        if not self.nameInput.isVisible():
            self.nameLabel.hide()
            self.nameInput.show()
            self.nameInputButton.setText("Update")
            return
        self.nameInput.hide()
        print('hunter name update')
        settings.setValue('hunterName',self.nameInput.text())
        pid = Connection.execute_query("select profileid from 'hunter' where blood_line_name is '%s' limit 1" % self.nameInput.text())
        while type(pid) is list or type(pid) is tuple:
            if len(pid) == 0:
                pid = -1
                break
            pid = pid[0]
        settings.setValue('profileid',pid)
        self.nameLabel.setText(settings.value('hunterName'))
        self.nameInputButton.setText("Change Steam Name")
        self.nameLabel.show()
        self.mainframe.update()