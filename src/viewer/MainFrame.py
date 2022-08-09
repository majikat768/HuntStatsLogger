from PyQt6.QtWidgets import QWidget,QPushButton,QTabWidget,QVBoxLayout
from PyQt6.QtCore import QThread
from settings.SettingsWindow import SettingsWindow
from viewer import DbHandler
from viewer.HeaderBar import HeaderBar
from viewer.HuntersTab import HuntersTab
from viewer.HuntsTab import HuntsTab
from viewer.ChartTab import ChartTab
from resources import *

class MainFrame(QWidget):
    def __init__(self, parent, layout):
        super().__init__(parent)
        self.layout = layout
        self.setLayout(self.layout)

        self.settingsWindow = SettingsWindow()
        self.settingsWindow.viewerMainframe = self

        self.dbHandler = DbHandler.DbHandler()
        self.startDbHandler()

        self.initUI()
        self.update()

    def initUI(self):

        self.headerBar = HeaderBar(self)

        self.body = self.initTabs()


        self.layout.addWidget(self.headerBar)
        self.layout.addWidget(self.body)
        self.settingsButton = self.SettingsButton()
        self.layout.addWidget(self.settingsButton)
        self.layout.addStretch()

    
    def initTabs(self):
        body = QWidget(self)
        body.layout = QVBoxLayout()
        body.setLayout(body.layout)
        tabs = QTabWidget()

        self.huntsTab = HuntsTab(self)
        self.huntersTab = HuntersTab(self)
        self.chartTab = ChartTab(self)
        tabs.addTab(self.huntsTab,"Hunts")
        tabs.addTab(self.huntersTab,"Hunters")
        tabs.addTab(self.chartTab,"Chart")
        body.layout.addWidget(tabs)
        return body

    def SettingsButton(self):
        settingsButton = QPushButton("Settings")
        settingsButton.clicked.connect(self.toggleSettings)
        return settingsButton

    def toggleSettings(self):
        if self.settingsWindow == None:
            self.settingsWindow = SettingsWindow()
            self.settingsWindow.viewerMainframe = self
        if not self.settingsWindow.isVisible():
            self.settingsWindow.show()
        else:
            self.settingsWindow.raise_()

    def startDbHandler(self):
        log('starting db handler')
        dbThread = QThread(parent=self)
        self.dbHandler.moveToThread(dbThread)
        DbHandler.running = True
        dbThread.started.connect(self.dbHandler.run)
        self.dbHandler.finished.connect(dbThread.quit)
        self.dbHandler.finished.connect(self.dbHandler.deleteLater)
        self.dbHandler.finished.connect(dbThread.deleteLater)
        self.dbHandler.progress.connect(self.update)
        dbThread.start()

    def update(self):
        self.headerBar.update()
        self.huntsTab.update()
        self.huntersTab.update() 
        self.chartTab.update()
        #self.setMaximumWidth(self.sizeHint().width())
        self.window().setMaximumSize(self.sizeHint().width()*2,self.sizeHint().height())

