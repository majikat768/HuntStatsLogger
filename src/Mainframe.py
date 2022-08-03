from PyQt6.QtWidgets import (
    QTabWidget,
    QLabel,
    QWidget,
    QGridLayout,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QMainWindow,
    QSizePolicy,
    QWIDGETSIZE_MAX
)
import HuntsTab, Settings, Hunter, HuntersTab, Chart
from PyQt6.QtCore import Qt
from resources import *
import Logger, Connection
import Client

class MainFrame(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.initUI()
        self.huntDir = settings.value('huntDir','')

        if Client.isLoggedIn():
            aws_sub = settings.value("aws_sub")
            tokens = Client.getTokens()
            local_files = getLocalFiles()
            remote_files = Client.getRemoteFiles(aws_sub,tokens)
            if len(local_files) != len(remote_files):
                self.botoCall = Client.BotoCall()
                Client.startThread(
                    self,self.botoCall,started=[self.botoCall.syncFiles],progress=[],finished=[]
                )
        Connection.syncDb()
        self.update()
        self.logger = Logger.Logger()
        self.connection = Connection.Connection()
        StartConnection(self.connection,self)
        StartLogger(self.logger,self)


    def showLoggedIn(self):
        if Client.isLoggedIn():
            self.loggedInStatus.setText("Logged in as %s" % settings.value('aws_username'))
            self.loggedInStatus.setStyleSheet("QLabel{color:#a9b7c6;}")
        else:
            self.loggedInStatus.setText("Not logged in.")
            self.loggedInStatus.setStyleSheet("QLabel{color:#dd8888;}")

    def initUI(self):
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.hunterBox = Hunter.Hunter(QHBoxLayout(),'Hunter')
        self.hunterBox.setSizePolicy(QSizePolicy.Policy.MinimumExpanding,QSizePolicy.Policy.Fixed)

        self.tabs = QTabWidget();

        self.huntsTab = HuntsTab.HuntsTab(QGridLayout(),'Hunts')
        self.tabs.addTab(self.huntsTab,'\t Hunts\t')

        self.huntersTab = HuntersTab.HuntersTab(QGridLayout(),'Hunters')
        self.tabs.addTab(self.huntersTab,'\tHunters\t')

        self.chartTab = Chart.Chart(QGridLayout(),'Chart')
        self.tabs.addTab(self.chartTab,'\tChart\t')
        self.settingsWindow = self.initSettingsWindow();


        self.layout.addWidget(self.hunterBox)
        self.layout.addWidget(self.tabs)
        self.statusBox = QWidget()
        self.statusBox.layout = QHBoxLayout() 
        self.statusBox.setLayout(self.statusBox.layout) 
        self.settingsButton = QPushButton('Settings')
        self.settingsButton.clicked.connect(self.settingsWindow.show)
        self.settingsButton.setSizePolicy(QSizePolicy.Policy.Expanding,QSizePolicy.Policy.Minimum)
        self.statusBox.layout.addWidget(self.settingsButton)

        self.loggedInStatus = QLabel()
        self.showLoggedIn()

        self.loggedInStatus.setSizePolicy(QSizePolicy.Policy.Minimum,QSizePolicy.Policy.Minimum)
        self.loggedInStatus.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.statusBox.layout.addWidget(self.loggedInStatus)
        self.layout.addWidget(self.statusBox)
        self.layout.addStretch()
        if not valid_xml_path(settings.value('huntDir','')):
            self.hunterBox.hide()
            self.tabs.hide()
            self.settingsButton.setText(' Set Hunt Installation Drive ')


    def initSettingsWindow(self):
        settingsBox = Settings.Settings(self,QVBoxLayout())

        settingsWindow = QMainWindow(self)
        #settingsWindow.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        settingsWindow.setCentralWidget(settingsBox)
        #settingsWindow.setMenuBar(TitleBar.TitleBar(settingsWindow))
        #settingsWindow.menuBar().setFixedHeight(48)
        #settingsWindow.setFixedSize(settingsWindow.sizeHint())
        return settingsWindow;

        
    def update(self):
        print('mainframe: updating')
        self.hunterBox.update()
        self.huntsTab.update()
        self.huntersTab.update()
        self.chartTab.update()

    def HideBoxes(self):
        self.tabs.hide()
        self.window().setMinimumHeight(self.layout.sizeHint().height())
        self.window().setMaximumHeight(self.layout.sizeHint().height())

    def ShowBoxes(self):
        self.tabs.show()
        self.window().setMinimumHeight(0)
        self.window().setMaximumHeight(QWIDGETSIZE_MAX)
        self.window().adjustSize()

    def ToggleBoxes(self):
        if self.tabs.isVisible():
            self.HideBoxes()
        else:
            self.ShowBoxes()