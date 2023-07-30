from PyQt6.QtWidgets import QMainWindow,QWidget,QVBoxLayout, QHBoxLayout, QGridLayout, QGroupBox, QPushButton, QFileDialog, QSizePolicy, QLineEdit, QComboBox, QCheckBox, QSpacerItem, QApplication, QDialog, QDialogButtonBox
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QIntValidator
from DbHandler import execute_query, GetTotalHuntCount, update_views
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
            pid = execute_query("select profileid from 'hunters' where blood_line_name is '%s' limit 1" % settings.value("steam_name"))
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
        self.initHuntLimit()
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

    def initHuntLimit(self):
        if not settings.value("hunt_limit",False):
            settings.setValue("hunt_limit","25")
        self.huntLimitWidget = QWidget()
        self.huntLimitWidget.layout = QGridLayout()
        self.huntLimitWidget.setLayout(self.huntLimitWidget.layout)

        self.huntLimitLabel = Label("Show only last <b>%s</b> hunts" % (settings.value("hunt_limit","25")))

        self.huntLimitInput = QLineEdit(settings.value("hunt_limit","25"))
        self.huntLimitInput.setValidator(QIntValidator())

        self.maxLimitButton = QPushButton("set max")
        self.maxLimitButton.clicked.connect(lambda : self.huntLimitInput.setText(str(GetTotalHuntCount())))
        self.huntLimitSubmit = QPushButton("OK")
        self.huntLimitSubmit.clicked.connect(self.confirmHighHuntLimit)

        self.huntLimitWidget.layout.addWidget(self.huntLimitLabel,0,0,1,4)
        self.huntLimitWidget.layout.addWidget(self.maxLimitButton,0,3,1,1)
        self.huntLimitWidget.layout.addWidget(self.huntLimitInput,1,0,1,3)
        self.huntLimitWidget.layout.addWidget(self.huntLimitSubmit,1,3,1,1)

        self.main.layout.addWidget(self.huntLimitWidget)

    def initSteamOptions(self):
        self.steamFolderLabel = Label(settings.value("hunt_dir","<i>ex: C:/Steam/steamapps/common/Hunt Showdown</i>"))
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

    def confirmHighHuntLimit(self):
        n = int(self.huntLimitInput.text())
        if n < 200:
            self.setHuntLimit()
            return
        confirmation = QDialog(self)
        confirmation.layout = QVBoxLayout()
        confirmation.setLayout(confirmation.layout)
        confirmation.setFixedWidth(self.width())

        confirmation.setWindowTitle("Are you sure?")

        confirmation.textLabel = Label("Setting the number of hunts to show higher than a few hundred will introduce noticeable lagtime in loading.")
        confirmation.textLabel.setWordWrap(True)

        buttons = QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        confirmation.buttonBox = QDialogButtonBox(buttons)
        confirmation.buttonBox.accepted.connect(lambda : self.okHighHuntLimit(confirmation,n))
        confirmation.buttonBox.rejected.connect(lambda : self.huntLimitInput.setText(settings.value("hunt_limit","-1")))
        confirmation.buttonBox.rejected.connect(confirmation.close)

        confirmation.layout.addWidget(confirmation.textLabel)
        confirmation.layout.addWidget(confirmation.buttonBox)

        confirmation.show()

    def okHighHuntLimit(self,dialog : QDialog,n):
        dialog.setWindowTitle("Hunt Limit Set")
        self.huntLimitInput.setText(str(n))
        self.setHuntLimit()

        dialog.textLabel.setText("Hunt limit set to %d." % n)
        dialog.buttonBox.setVisible(False)
        dialog.okBox = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        dialog.okBox.accepted.connect(dialog.close)
        dialog.layout.addWidget(dialog.okBox)

        pass
        #self.huntLimitInput.setText(count)

    def setHuntLimit(self):
        settings.setValue("hunt_limit",int(self.huntLimitInput.text()))
        self.huntLimitLabel.setText("Show only last <b>%s</b> hunts" % settings.value("hunt_limit","0"))
        self.parent().mainUpdate()

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
                pid = execute_query("select profileid from 'hunters' where blood_line_name is '%s' limit 1" % self.steamNameInput.text())
                pid = -1 if len(pid) == 0 else pid[0][0]
                if pid > 0:
                    settings.setValue("profileid",pid)
                for i in range(10):
                    QApplication.processEvents()
                self.parent().mainUpdate()
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