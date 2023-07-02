from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTabWidget
from PyQt6.QtCore import QThread, QPoint
from PyQt6.QtGui import QIcon
import subprocess

from MainWindow.Main.Header import Header
from MapWindow.MapWindow import MapWindow
from SettingsWindow import SettingsWindow
from Logger import Logger
from resources import *
from MainWindow.Main.Body import Body
from MainWindow.Hunts.Hunts import Hunts
from MainWindow.Hunters.Hunters import Hunters
from MainWindow.Chart.Chart import Chart
from MainWindow.TopHunts.TopHunts import TopHunts
from MainWindow.MyTeams.MyTeams import MyTeams
from DbHandler import update_views


class MainFrame(QWidget):
    def __init__(self, parent=None) -> None:
        if debug:
            print("mainframe.__init__")
        super().__init__(parent)
        self.setObjectName("MainFrame")
        self.mousePressed = False
        self.logger = Logger(self)

        self.settingsWindow = SettingsWindow(self)
        self.mapWindow = MapWindow(self)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.layout.setSpacing(0)
        self.setContentsMargins(0,0,0,0)

        self.header = Header(self)
        self.header.setContentsMargins(0,0,0,0)
        self.layout.addWidget(self.header)
        self.initBody()

        self.initButtons()
        self.offset = QPoint()


        self.setStatus("ready.")

        if (settings.value("xml_path", "") != ""):
            self.StartLogger()
        if (settings.value("hunt_dir","") != ""):
            if (settings.value("run_game_on_startup", "false").lower() == "true"
                and "HuntGame.exe" not in subprocess.check_output(['tasklist', '/FI', 'IMAGENAME eq HuntGame.exe']).decode()):
                    launch_hunt()
                    #os.startfile(os.path.join(settings.value("hunt_dir"),"hunt.exe"))
        self.mainUpdate()

    def initButtons(self):
        if debug:
            print("mainframe.initButtons")
        settingsButton = QPushButton("Settings")
        settingsButton.clicked.connect(lambda : self.openWindow(self.settingsWindow))

        mapsButton = QPushButton("Maps")
        mapsButton.clicked.connect(lambda : self.openWindow(self.mapWindow))

        updateButton = QPushButton("Refresh Data")
        updateButton.clicked.connect(self.update)

        startHuntButton = QPushButton("Launch Hunt")
        startHuntButton.clicked.connect(launch_hunt)

        self.buttons = QWidget()
        self.buttons.layout = QHBoxLayout()
        self.buttons.setLayout(self.buttons.layout)

        self.buttons.layout.addWidget(startHuntButton)
        self.buttons.layout.addWidget(mapsButton)
        self.buttons.layout.addWidget(settingsButton)
        self.buttons.layout.addWidget(updateButton)

        self.layout.addWidget(self.buttons)

    def setStatus(self, msg):
        self.window().setStatus(msg)

    def initBody(self):
        if debug:
            print("mainframe.initBody")
        self.tabs = Body(parent=self)
        self.tabs.setContentsMargins(0,0,0,0)
        self.huntsTab = Hunts(parent=self.tabs)
        self.huntersTab = Hunters(parent=self.tabs)
        self.chartTab = Chart(parent=self.tabs)
        self.topHuntsTab = TopHunts(parent=self.tabs)
        self.teamsTab = MyTeams(parent=self.tabs)
        self.tabs.addTab(self.huntsTab, "HUNTS")
        self.tabs.addTab(self.huntersTab, "HUNTERS")
        self.tabs.addTab(self.chartTab, "CHARTS")
        self.tabs.addTab(self.topHuntsTab, "TOP HUNTS")
        self.tabs.addTab(self.teamsTab, "TEAMS")

        self.layout.addWidget(self.tabs.tabBar)
        self.layout.addWidget(self.tabs.stack)

    def mainUpdate(self):
        if debug:
            print('mainframe.update')
        update_views()
        self.header.update()
        self.huntsTab.update()
        self.huntersTab.update()
        self.chartTab.update()
        self.topHuntsTab.update()
        self.teamsTab.update()
        # self.window().adjustSize()

    def StartLogger(self):
        thread = QThread(parent=self)
        self.logger.moveToThread(thread)
        thread.started.connect(self.logger.run)
        self.logger.finished.connect(thread.quit)
        self.logger.finished.connect(thread.deleteLater)
        self.logger.progress.connect(self.mainUpdate)

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

    def openWindow(self,window):
        if not window.isVisible():
            window.show()
        else:
            window.raise_()
    def setStatus(self, msg):
        self.window().setStatus(msg)