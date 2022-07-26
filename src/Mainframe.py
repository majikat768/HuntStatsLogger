from PyQt5.QtWidgets import (
    QTabWidget,
    QWidget,
    QGridLayout,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QMainWindow,
    QSizePolicy
)
from PyQt5.QtCore import QSettings, QPoint, Qt
import HuntsTab, Settings, Hunter, Connection, TitleBar, HuntersTab

killall = False

class MainFrame(QWidget):
    def __init__(self, parent) -> None:
        super().__init__(parent)
        self.parent = parent
        self.connection = Connection.Connection()
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.settings = QSettings('./settings.ini',QSettings.Format.IniFormat)
        self.huntDir = self.settings.value('huntDir','')

        self.initUI()

        self.setSizePolicy(QSizePolicy.MinimumExpanding,QSizePolicy.MinimumExpanding)
        self.mouseXY = QPoint()

    def initUI(self):
        self.hunterBox = Hunter.Hunter(self,QHBoxLayout(),'Hunter')
        self.layout.addWidget(self.hunterBox)

        self.tabs = QTabWidget();
        self.layout.addWidget(self.tabs)

        self.huntsTab = HuntsTab.HuntsTab(self,QGridLayout(),'Hunts')
        self.tabs.addTab(self.huntsTab,'Hunts')

        self.huntersTab = HuntersTab.HuntersTab(self, QGridLayout(),'Hunters')
        self.tabs.addTab(self.huntersTab,'Hunters')

        self.settingsWindow = self.initSettingsWindow();

        self.settingsButton = QPushButton('Settings')
        self.settingsButton.clicked.connect(self.settingsWindow.show)

        self.layout.addWidget(self.settingsButton)

    def initTabs(self):
        tabs = QTabWidget()

    def initSettingsWindow(self):
        settingsBox = Settings.Settings(self,QVBoxLayout())

        settingsWindow = QMainWindow()
        settingsWindow.setWindowFlags(Qt.FramelessWindowHint)
        settingsWindow.setCentralWidget(settingsBox)
        settingsWindow.setMenuBar(TitleBar.TitleBar(settingsWindow))
        settingsWindow.menuBar().setFixedHeight(48)
        settingsWindow.setFixedSize(settingsWindow.sizeHint())
        return settingsWindow;

        
    def StartLogger(self):
        self.parent.StartLogger()

    def update(self):
        print('mainframe: updating')
        self.hunterBox.update()
        self.huntsTab.update()