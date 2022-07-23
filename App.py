from datetime import datetime
from Mainframe import MainFrame
import sys
from PyQt5.QtCore import QThread,QSettings,Qt
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from threading import *
from TitleBar import TitleBar
import Logger

'''
detects changes to the Hunt Showdown 'attributes.xml' file.
when change is found, backup new .xml file, also convert team and game data to json format.
when change is found, parse .xml file and create json objects, write json to a file, and write objects to a sql database.
'''

def unix_to_datetime(timestamp):
    return datetime.fromtimestamp(timestamp).strftime('%H:%M %m/%d/%y')

database = 'huntstats.db'

class App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.settings = QSettings('majikat','HuntStats')
        self.setMenuBar(TitleBar(self))
        self.menuBar().setFixedHeight(48)
        self.mainFrame = MainFrame(self)
        #self.setWindowFlags(Qt.FramelessWindowHint)
        self.setWindowFlags(Qt.CustomizeWindowHint)
        #self.setAttribute(Qt.WA_NoSystemBackground, True)
        #self.setAttribute(Qt.WA_TranslucentBackground, True)

        self.setCentralWidget(self.mainFrame)
        #self.setMaximumSize(self.sizeHint())

        self.logger = Logger.Logger()
        if self.settings.value('huntDir','') != '':
            print('starting logger')
            self.StartLogger()

        self.show()


    def StartLogger(self):
        self.loggerThread = QThread()
        self.logger.set_path(self.settings.value('huntDir',''))
        self.logger.moveToThread(self.loggerThread)
        self.loggerThread.started.connect(self.logger.run)
        self.logger.finished.connect(self.loggerThread.quit)
        self.logger.finished.connect(self.logger.deleteLater)
        self.logger.progress.connect(self.UpdateData)
        self.logger.finished.connect(self.loggerThread.deleteLater)
        self.loggerThread.start()

    def UpdateData(self):
        self.mainFrame.update()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    QFontDatabase.addApplicationFont('./assets/fonts/ubuntu/Ubuntu-R.ttf')
    #app.setStyleSheet(open('./assets/stylesheet.qss','r').read())
    app.setStyleSheet(open('./assets/MaterialDark.qss','r').read())
    ex2 = App()
    #app.setStyleSheet(open('./assets/SpyBot.qss','r').read())
    #app.setStyleSheet(open('./assets/ManjaroMix.qss','r').read())


    app.exec_()
    Logger.killall = True