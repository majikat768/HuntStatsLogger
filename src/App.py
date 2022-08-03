import os
from Mainframe import MainFrame
from PyQt6.QtCore import QThread
from PyQt6.QtWidgets import QMainWindow
import Connection, Logger, Client
from resources import *

'''
detects changes to the Hunt Showdown 'attributes.xml' file.
when change is found, backup new .xml file, also convert team and game data to json format.
when change is found, parse .xml file and create json objects, write json to a file, and write objects to a sql database.
'''

killall = True

class App(QMainWindow):
    def __init__(self):
        super().__init__()
        Connection.create_tables(db,resource_path('assets/schema.sql'))
        #self.app_data_path = os.path.join(QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppLocalDataLocation),'hsl_files')
        self.mainFrame = MainFrame()
        self.setWindowTitle('Hunt Stats Tracker')

        self.setCentralWidget(self.mainFrame)

        self.show()