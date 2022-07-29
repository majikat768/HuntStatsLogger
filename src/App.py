from datetime import datetime
from Mainframe import MainFrame
from PyQt5.QtCore import QThread,QSettings
from PyQt5.QtWidgets import QMainWindow
import Connection, Logger

'''
detects changes to the Hunt Showdown 'attributes.xml' file.
when change is found, backup new .xml file, also convert team and game data to json format.
when change is found, parse .xml file and create json objects, write json to a file, and write objects to a sql database.
'''

killall = True
def unix_to_datetime(timestamp):
    return datetime.fromtimestamp(timestamp).strftime('%H:%M %m/%d/%y')

database = 'huntstats.db'

class App(QMainWindow):
    def __init__(self,log=True):
        super().__init__()
        self.log = log 
        self.connection = Connection.Connection()
        self.settings = QSettings('./settings.ini',QSettings.Format.IniFormat)
        self.mainFrame = MainFrame(self)
        self.setWindowTitle('Hunt Stats Tracker')

        self.setCentralWidget(self.mainFrame)

        self.StartConnection()

        if(self.log):
            self.logger = Logger.Logger()
            if self.settings.value('huntDir','') != '':
                print('starting logger')
                self.StartLogger()
        else:
            self.UpdateData()

        self.show()

    def StartConnection(self):
        self.connThread = QThread(parent=self)
        self.connection.moveToThread(self.connThread)
        self.connThread.started.connect(self.connection.run)
        self.connection.finished.connect(self.connThread.quit)
        self.connection.finished.connect(self.connection.deleteLater)
        self.connection.finished.connect(self.connThread.deleteLater)
        self.connection.progress.connect(self.UpdateData)
        self.connThread.start()

    def StartLogger(self):
        if(self.log):
            validPath = self.logger.set_path(self.settings.value('huntDir',''))
            if validPath != 1:
                return
            self.loggerThread = QThread(parent=self)
            self.logger.moveToThread(self.loggerThread)
            self.loggerThread.started.connect(self.logger.run)
            self.logger.finished.connect(self.loggerThread.quit)
            self.logger.finished.connect(self.logger.deleteLater)
            self.logger.finished.connect(self.loggerThread.deleteLater)
            self.logger.progress.connect(self.UpdateData)
            self.loggerThread.start()

    def UpdateData(self):
        print('App:  updating data')
        self.mainFrame.update()