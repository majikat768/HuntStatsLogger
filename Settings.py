from PyQt5.QtWidgets import QPushButton,QLineEdit,QFileDialog, QSizePolicy,QWidget, QVBoxLayout,QComboBox, QLabel
import time
from PyQt5.QtCore import Qt, QSettings
import os
import json
from Connection import Connection, unix_to_datetime
from TitleBar import TitleBar

from GroupBox import GroupBox

class Settings(GroupBox):
    def __init__(self,parent,layout,title=''):
        super().__init__(layout,title)
        self.connection = Connection()
        self.huntDir = ''
        self.parent = parent
        self.settings = QSettings('majikat','HuntStats')
        self.layout = layout
        self.setLayout(self.layout)
        self.layout.setAlignment(Qt.AlignLeft)

        self.huntDirButton = QPushButton('Select Hunt Installation Directory')
        self.huntDirButton.clicked.connect(self.SelectHuntFolder)
        self.huntDirQLabel = QLabel(self.settings.value('huntDir','select Hunt Installation Directory'))
        self.layout.addWidget(self.huntDirButton,0,0)
        self.layout.addWidget(self.huntDirQLabel,0,1)
        self.layout.setRowStretch(0,0)

        self.nameInputButton = QPushButton('Update Steam Name')
        self.nameInput = QLineEdit(self.settings.value('hunterName',''))
        self.nameInput.setPlaceholderText('Enter your Steam username')
        self.nameInput.setVisible(False)
        self.nameQLabel = QLabel(self.settings.value('hunterName',''))
        self.nameInputButton.clicked.connect(self.UpdateHunterName)
        self.nameInput.returnPressed.connect(self.UpdateHunterName)
        self.layout.addWidget(self.nameInputButton,1,0)
        self.layout.addWidget(self.nameQLabel,1,1)
        self.layout.addWidget(self.nameInput,1,1)

        self.layout.addWidget(QLabel('\ndev stuff:'),2,0)
        self.importJsonButton = QPushButton('Import a json file....')
        self.importJsonButton.clicked.connect(self.ImportJson)
        self.layout.addWidget(self.importJsonButton,3,0)

        self.deleteRecordButton = QPushButton('Delete a record....')
        self.deleteRecordButton.clicked.connect(self.DeleteRecordDialog)
        self.layout.addWidget(self.deleteRecordButton,3,1)


        self.layout.setRowStretch(self.layout.rowCount(),1)
        #self.setSizePolicy(QSizePolicy.MinimumExpanding,QSizePolicy.Maximum)
    
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

    def updateMatchSelect(self):
        self.parent.huntHistoryTab.updateMatchSelect()
        self.parent.huntHistoryTab.update()
        self.window.deleteLater()
        self.window.close()

    def ImportJson(self):
        options = QFileDialog.Options()
        #options |= QFileDialog.DontUseNativeDialog
        jsonfile, _ = QFileDialog.getOpenFileName(self,'Select json file',os.getcwd(),options=options)
        timestamp = int(time.time())
        jsonObj = json.load(open(jsonfile,'r'))
        self.parent.parent.logger.write_json_to_sql(jsonObj,timestamp)

    def SelectHuntFolder(self):
        options = QFileDialog.Options()
        #options |= QFileDialog.DontUseNativeDialog
        directory = QFileDialog.getExistingDirectory(self, "Select Hunt Installation Directory",self.huntDir,options=options)
        if directory != '':
            print('directory set')
            self.settings.setValue('huntDir',directory)
            self.huntDirQLabel.setText(self.settings.value('huntDir',''))
            self.parent.StartLogger()
            self.parent.update()

    def UpdateHunterName(self):
        if self.nameInput.isVisible():
            self.settings.setValue('hunterName',self.nameInput.text())
            self.nameQLabel.setText(self.settings.value('hunterName',''))
            self.parent.update()
            self.nameInput.setVisible(False)
            self.nameQLabel.setVisible(True)

        else:
            self.nameQLabel.setVisible(False)
            self.nameInput.setVisible(True)
            self.nameInput.setFocus()