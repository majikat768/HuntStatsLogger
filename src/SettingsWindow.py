from PyQt6.QtWidgets import QMainWindow,QWidget,QVBoxLayout, QHBoxLayout, QGridLayout, QGroupBox, QPushButton,QLabel, QFileDialog, QSizePolicy, QLineEdit, QComboBox, QCheckBox, QSpacerItem, QApplication, QDialog
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from DbHandler import execute_query
from resources import *
from Widgets.Modal import Modal

class SettingsWindow(QMainWindow):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        self.setObjectName("SettingsWindow")

        self.main = QWidget()
        self.main.layout = QVBoxLayout()
        self.main.setLayout(self.main.layout)

        self.initUI()
        if int(settings.value("profileid","-1")) < 0 and len(settings.value("steam_name","")) > 0:
            pid = execute_query("select profileid from 'hunters' where blood_line_name is '%s'" % settings.value("steam_name"))
            pid = -1 if len(pid) == 0 else pid[0][0]
            if pid > 0:
                settings.setValue("profileid",pid)

    def initUI(self):
        self.initSteamOptions()
        self.main.layout.addItem(QSpacerItem(0,16,QSizePolicy.Policy.Fixed,QSizePolicy.Policy.Fixed))

        self.miniViewCheck = QCheckBox("Mini Viewer")
        self.miniViewCheck.stateChanged.connect(self.toggleMiniView)
        self.main.layout.addWidget(self.miniViewCheck)

        self.sysTrayCheck = QCheckBox("Minimize to System Tray on exit")
        self.sysTrayCheck.setChecked(settings.value("show_sys_tray","False").lower() == "true")
        self.sysTrayCheck.stateChanged.connect(self.toggleSysTray)
        self.main.layout.addWidget(self.sysTrayCheck)

        self.runGameCheck = QCheckBox("Run Hunt on startup")
        self.runGameCheck.setChecked(settings.value("run_game_on_startup","false").lower() == "true")
        self.runGameCheck.stateChanged.connect(self.toggleRunGame)
        self.main.layout.addWidget(self.runGameCheck)

        self.main.layout.addItem(QSpacerItem(0,16,QSizePolicy.Policy.Fixed,QSizePolicy.Policy.Fixed))
        self.initKdaRange()
        self.initDropdownRange()
        self.main.layout.addItem(QSpacerItem(0,16,QSizePolicy.Policy.Fixed,QSizePolicy.Policy.Fixed))

        open_dir_button = QPushButton(" Open Settings Folder ")
        open_dir_button.setSizePolicy(QSizePolicy.Policy.Minimum,QSizePolicy.Policy.Minimum)
        open_dir_button.clicked.connect(lambda : os.startfile(app_data_path))
        self.main.layout.addWidget(open_dir_button)
        self.main.layout.setAlignment(open_dir_button,Qt.AlignmentFlag.AlignHCenter)

        hunt_dir_button = QPushButton(" Open Hunt Directory ")
        hunt_dir_button.setSizePolicy(QSizePolicy.Policy.Minimum,QSizePolicy.Policy.Minimum)
        hunt_dir_button.clicked.connect(self.open_hunt_dir)
        self.main.layout.addWidget(hunt_dir_button)
        self.main.layout.setAlignment(hunt_dir_button,Qt.AlignmentFlag.AlignHCenter)

        self.setCentralWidget(self.main)

    def open_hunt_dir(self):
        if len(settings.value("hunt_dir","")) > 0:
            os.startfile(settings.value("hunt_dir"))

    def toggleMiniView(self):
        main = self.parent()
        if self.miniViewCheck.isChecked():
            main.window().minify()
        else:
            main.window().maxify()

    def toggleSysTray(self):
        main = self.parent()
        w = main.window()
        if self.sysTrayCheck.isChecked():
            w.showSysTray = True
            settings.setValue("show_sys_tray",True)
        else:
            w.showSysTray = False
            settings.setValue("show_sys_tray",False)

    def toggleRunGame(self):
        if self.runGameCheck.isChecked():
            settings.setValue("run_game_on_startup",True)
        else:
            settings.setValue("run_game_on_startup",False)

    def initKdaRange(self):
        self.KdaRangeLabel = QLabel("Calculate KDA from the last...")
        self.KdaRangeDropBox = QComboBox()
        self.KdaRangeDropBox.addItem("24 hours",86400)
        self.KdaRangeDropBox.addItem("7 days",604800)
        self.KdaRangeDropBox.addItem("30 days",2592000)
        self.KdaRangeDropBox.addItem("1 year",31540000)
        self.KdaRangeDropBox.addItem("All time",-1)
        self.KdaRangeDropBox.activated.connect(self.setKdaRange)
        self.KdaRangeDropBox.activated.connect(self.parent().update)
        if settings.value("kda_range","") == "":
            settings.setValue("kda_range","-1")
        self.KdaRangeDropBox.setCurrentIndex(self.KdaRangeDropBox.findData(settings.value("kda_range","-1")))
        self.main.layout.addWidget(self.KdaRangeLabel)
        self.main.layout.addWidget(self.KdaRangeDropBox)
    
    def initDropdownRange(self):
        self.dropdownRangeLabel = QLabel("Show hunts in dropdown from last...")
        self.dropdownRangeDropBox = QComboBox()
        self.dropdownRangeDropBox.addItem("24 hours",86400)
        self.dropdownRangeDropBox.addItem("7 days",604800)
        self.dropdownRangeDropBox.addItem("30 days",2592000)
        self.dropdownRangeDropBox.addItem("1 year",31540000)
        self.dropdownRangeDropBox.addItem("All time",-1)
        self.dropdownRangeDropBox.activated.connect(self.setDropdownRange)
        self.dropdownRangeDropBox.activated.connect(self.parent().update)
        if settings.value("dropdown_range","") == "":
            settings.setValue("dropdown_range","604800")
        self.dropdownRangeDropBox.setCurrentIndex(self.dropdownRangeDropBox.findData(settings.value("dropdown_range","604800")))
        self.main.layout.addWidget(self.dropdownRangeLabel)
        self.main.layout.addWidget(self.dropdownRangeDropBox)

    def initSteamOptions(self):
        self.steamFolderLabel = QLabel(settings.value("hunt_dir","<i>ex: C:/Steam/steamapps/common/Hunt Showdown</i>"))
        self.steamFolderButton = QPushButton("Select Hunt Installation Directory")
        self.steamFolderButton.setSizePolicy(QSizePolicy.Policy.Fixed,QSizePolicy.Policy.Fixed)
        self.steamFolderButton.clicked.connect(self.SelectFolderDialog)
        self.main.layout.addWidget(self.steamFolderLabel)
        self.main.layout.addWidget(self.steamFolderButton)
        self.main.layout.setAlignment(self.steamFolderButton,Qt.AlignmentFlag.AlignHCenter)

        self.steamName = QWidget()
        self.steamName.layout = QHBoxLayout()
        self.steamName.setLayout(self.steamName.layout)
        self.steamName.setSizePolicy(QSizePolicy.Policy.MinimumExpanding,QSizePolicy.Policy.Expanding)

        self.steamNameInput = QLineEdit(settings.value("steam_name","steam name not set"))
        self.steamNameInput.returnPressed.connect(self.ChangeSteamName)
        self.steamNameInput.setDisabled(True)
        self.steamNameInput.setSizePolicy(QSizePolicy.Policy.MinimumExpanding,QSizePolicy.Policy.Fixed)
        self.steamNameButton = QPushButton("Change Steam Name")
        self.steamNameButton.setSizePolicy(QSizePolicy.Policy.Fixed,QSizePolicy.Policy.Fixed)
        self.steamNameButton.clicked.connect(self.ChangeSteamName)
        self.steamNameButton.clicked.connect(lambda : self.steamNameInput.setFocus())
        self.steamName.layout.addWidget(self.steamNameInput)
        self.steamName.layout.addWidget(self.steamNameButton)
        self.main.layout.addWidget(self.steamName)

    
    def setKdaRange(self):
        settings.setValue("kda_range",self.KdaRangeDropBox.currentData())
    def setDropdownRange(self):
        settings.setValue("dropdown_range",self.dropdownRangeDropBox.currentData())

    '''
    potential bug here:
    one could assume Steam names are not unique,
    so in the case one is in a Hunt with another Hunter of the same name,
    profileid could be incorrect.
    '''
    def ChangeSteamName(self):
        if self.steamNameInput.isEnabled():
            if(len(self.steamNameInput.text()) > 0):
                settings.setValue("steam_name",self.steamNameInput.text())
                log('steam name updated')
                log(settings.value('steam_name'))
                self.steamNameInput.setText(settings.value("steam_name"))
                pid = execute_query("select profileid from 'hunters' where blood_line_name is '%s'" % self.steamNameInput.text())
                pid = -1 if len(pid) == 0 else pid[0][0]
                if pid > 0:
                    settings.setValue("profileid",pid)
                for i in range(10):
                    QApplication.processEvents()
                self.parent().update()
            self.steamNameInput.setDisabled(True)
        else:
            self.steamNameInput.setDisabled(False)
    
    def SelectFolderDialog(self):
        xml_suffix = "user/profiles/default/attributes.xml"
        hunt_dir = QFileDialog.getExistingDirectory(self,"Select folder",settings.value('hunt_dir','.'))
        xml_path = os.path.join(hunt_dir,xml_suffix)
        if not os.path.exists(xml_path):
            log('attributes.xml not found.')
            return
        settings.setValue('hunt_dir',hunt_dir)
        settings.setValue('xml_path',xml_path)
        self.steamFolderLabel.setText(settings.value("hunt_dir"))
        if not self.parent().logger.running:
            self.parent().StartLogger()

    def show(self):
        self.steamFolderLabel.setText(settings.value("hunt_dir"))
        self.steamNameInput.setText(settings.value("steam_name"))
        super().show()