from PyQt5.QtWidgets import QPushButton,QLineEdit,QFileDialog, QSizePolicy,QWidget, QVBoxLayout,QComboBox, QLabel
import time
from PyQt5.QtCore import Qt, QSettings
import os
import json
from Connection import Connection, unix_to_datetime
from GroupBox import GroupBox

settings = QSettings('./settings.ini',QSettings.Format.IniFormat)
class Settings(GroupBox):
    def __init__(self, parent,layout):
        super().__init__(layout)
        self.setStyleSheet('*{margin:4px;padding:4px;}')
        self.parent = parent
        self.connection = Connection()
        self.huntDir = ''
        self.layout = layout
        self.setLayout(self.layout)
        self.layout.setAlignment(Qt.AlignLeft)
        self.layout.setSpacing(0)

        self.layout.addWidget(QLabel('Hunt Installation Directory:'))
        self.huntDirButton = QPushButton('Select Folder')
        self.huntDirButton.clicked.connect(self.SelectHuntFolder)
        self.huntDirQLabel = QLabel(settings.value('huntDir','select Hunt Installation Directory'))
        self.layout.addWidget(self.huntDirQLabel)
        self.layout.addWidget(self.huntDirButton)

        self.layout.addWidget(QLabel())

        self.layout.addWidget(QLabel('Steam username:'))
        self.nameInputButton = QPushButton('Update Steam Name')
        self.nameInput = QLineEdit(settings.value('hunterName',''))
        self.nameInput.setPlaceholderText('Enter your Steam username')
        self.nameInputButton.clicked.connect(self.UpdateHunterName)
        self.nameInput.returnPressed.connect(self.UpdateHunterName)
        self.layout.addWidget(self.nameInput)
        self.layout.addWidget(self.nameInputButton)

        self.layout.addWidget(QLabel())

        self.layout.addWidget(QLabel('\ndev stuff:'))
        importJsonButton = QPushButton('Import a json file....')
        importJsonButton.clicked.connect(self.ImportJson)
        self.layout.addWidget(importJsonButton)

        deleteRecordButton = QPushButton('Delete a record....')
        deleteRecordButton.clicked.connect(self.DeleteRecordDialog)
        self.layout.addWidget(deleteRecordButton)
        self.layout.addStretch()

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
            settings.setValue('huntDir',directory)
            self.huntDirQLabel.setText(settings.value('huntDir',''))
            self.parent.StartLogger()
            self.parent.update()

    def UpdateHunterName(self):
        settings.setValue('hunterName',self.nameInput.text())
        settings.setValue('profileid',self.connection.GetProfileId(self.nameInput.text()))
        self.parent.update()