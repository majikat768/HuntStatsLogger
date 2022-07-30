from PyQt6.QtWidgets import (
    QTabWidget,
    QWidget,
    QGridLayout,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QMainWindow,
    QSizePolicy
)
from PyQt6.QtCore import QSettings, QPoint
import HuntsTab, Settings, Hunter, HuntersTab, Chart

killall = False

class MainFrame(QWidget):
    def __init__(self, parent) -> None:
        super().__init__(parent)
        self.parent = parent
        self.resource_path = self.parent.resource_path
        self.connection = parent.connection
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.settings = self.parent.settings
        self.huntDir = self.settings.value('huntDir','')

        self.initUI()

        self.mouseXY = QPoint()

    def initUI(self):
        self.hunterBox = Hunter.Hunter(self,QHBoxLayout(),'Hunter')
        self.layout.addWidget(self.hunterBox)

        self.tabs = QTabWidget();
        self.layout.addWidget(self.tabs)

        self.huntsTab = HuntsTab.HuntsTab(self,QGridLayout(),'Hunts')
        self.tabs.addTab(self.huntsTab,'\t Hunts\t')

        self.huntersTab = HuntersTab.HuntersTab(self, QGridLayout(),'Hunters')
        self.tabs.addTab(self.huntersTab,'\tHunters\t')

        self.chartTab = Chart.Chart(self,QGridLayout(),'Chart')
        self.tabs.addTab(self.chartTab,'\tChart\t')

        self.settingsWindow = self.initSettingsWindow();

        self.settingsButton = QPushButton('Settings')
        self.settingsButton.clicked.connect(self.settingsWindow.show)

        self.layout.addWidget(self.settingsButton)
        self.layout.addStretch()

    def initSettingsWindow(self):
        settingsBox = Settings.Settings(self,QVBoxLayout())

        settingsWindow = QMainWindow()
        #settingsWindow.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        settingsWindow.setCentralWidget(settingsBox)
        #settingsWindow.setMenuBar(TitleBar.TitleBar(settingsWindow))
        #settingsWindow.menuBar().setFixedHeight(48)
        settingsWindow.setFixedSize(settingsWindow.sizeHint())
        return settingsWindow;

        
    def StartLogger(self):
        self.parent.StartLogger()

    def update(self):
        print('mainframe: updating')
        self.hunterBox.update()
        self.huntsTab.update()
        self.huntersTab.update()
        self.chartTab.update()

    def HideBoxes(self):
        self.tabs.hide()
        self.parent.resize(self.parent.width(),self.parent.height()-10)
        print(self.parent.height())

    def ShowBoxes(self):
        self.tabs.show()

    def ToggleBoxes(self):
        if self.tabs.isVisible():
            self.HideBoxes()
        else:
            self.ShowBoxes()