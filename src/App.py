from datetime import datetime
import os,sys
from Mainframe import MainFrame
from PyQt6.QtCore import QThread,QSettings,QStandardPaths
from PyQt6.QtWidgets import QMainWindow
import Connection, Logger

'''
detects changes to the Hunt Showdown 'attributes.xml' file.
when change is found, backup new .xml file, also convert team and game data to json format.
when change is found, parse .xml file and create json objects, write json to a file, and write objects to a sql database.
'''

killall = True
def unix_to_datetime(timestamp):
    return datetime.fromtimestamp(timestamp).strftime('%H:%M %m/%d/%y')

def base_path():
    try:
    # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return base_path

def resource_path(relative_path):
    return os.path.join(base_path(), relative_path)


class App(QMainWindow):
    def __init__(self,log=True):
        super().__init__()
        self.resource_path = resource_path
        #self.app_data_path = os.path.join(QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppLocalDataLocation),'hsl_files')
        self.app_data_path = os.path.join(os.getcwd(),'hsl_files')
        if not os.path.exists(self.app_data_path):
            os.makedirs(self.app_data_path)
        #self.settings = QSettings('./settings.ini',QSettings.Format.IniFormat)
        self.settings = QSettings(
            os.path.join(self.app_data_path,'settings.ini'),
            QSettings.Format.IniFormat
        )
        self.log = log 
        self.connection = Connection.Connection(self)
        self.mainFrame = MainFrame(self)
        self.setWindowTitle('Hunt Stats Tracker')

        self.setCentralWidget(self.mainFrame)

        self.StartConnection()

        if(self.log):
            self.logger = Logger.Logger(self)
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