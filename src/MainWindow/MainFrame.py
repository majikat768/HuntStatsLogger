from PyQt6.QtWidgets import QWidget, QVBoxLayout,QHBoxLayout, QPushButton, QTabWidget
from PyQt6.QtCore import QThread

from MainWindow.Header import Header
from MapWindow.MapWindow import MapWindow
from SettingsWindow import SettingsWindow
from Logger import Logger
from resources import *
from MainWindow.Hunts.Hunts import Hunts
from MainWindow.Hunters import Hunters
from MainWindow.Chart.Chart import Chart 


class MainFrame(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.logger = Logger(self)

        self.settingsWindow = SettingsWindow(self)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.header = Header(self)
        self.layout.addWidget(self.header)
        self.initBody()

        settingsButton = QPushButton("Settings")
        settingsButton.clicked.connect(self.openSettings)

        self.mapWindow = MapWindow(self)
        mapsButton = QPushButton("Maps")
        mapsButton.clicked.connect(self.openMaps)

        self.buttons = QWidget()
        self.buttons.layout = QHBoxLayout()
        self.buttons.setLayout(self.buttons.layout)

        self.buttons.layout.addWidget(mapsButton)
        self.buttons.layout.addWidget(settingsButton)

        self.layout.addWidget(self.buttons)

        self.setStatus("ready.")
        if settings.value("xml_path","") == "":
            pass
            #steamworks_init()

        if(settings.value("xml_path","") != ""):
            self.StartLogger()

        self.update()


    def setStatus(self,msg):
        self.window().setStatus(msg)

    def initBody(self):
        self.tabs = QTabWidget()
        self.huntsTab = Hunts(self)
        self.huntersTab = Hunters(self)
        self.chartTab = Chart(self)
        self.tabs.addTab(self.huntsTab, "Hunts")
        self.tabs.addTab(self.huntersTab, "Hunters")
        self.tabs.addTab(self.chartTab, "Chart")
        self.layout.addWidget(self.tabs)


    def update(self):
        #print('mainframe.update')
        self.header.update()
        self.huntsTab.update()
        self.huntersTab.update()
        self.chartTab.update()
        #self.window().adjustSize()


    def StartLogger(self):
        thread = QThread(parent=self)
        self.logger.moveToThread(thread)
        thread.started.connect(self.logger.run)
        self.logger.finished.connect(thread.quit)
        self.logger.finished.connect(thread.deleteLater)
        self.logger.progress.connect(self.update)

        thread.start()

    def openSettings(self):
        if self.settingsWindow == None:
            self.settingsWindow = SettingsWindow(self)
        if not self.settingsWindow.isVisible():
            self.settingsWindow.show()
        else:
            self.settingsWindow.raise_()

    def openMaps(self):
        if self.mapWindow == None:
            self.mapWindow = MapWindow(self)
        if not self.mapWindow.isVisible():
            self.mapWindow.show()
        else:
            self.mapWindow.raise_()

    def setStatus(self,msg):
        self.window().setStatus(msg)