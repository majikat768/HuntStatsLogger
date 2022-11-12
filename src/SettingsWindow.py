from PyQt6.QtWidgets import QMainWindow,QWidget,QVBoxLayout, QGridLayout, QGroupBox, QPushButton,QLabel, QFileDialog, QSizePolicy, QLineEdit, QComboBox
from PyQt6.QtCore import Qt
from resources import *

class SettingsWindow(QMainWindow):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        self.setObjectName("SettingsWindow")

        self.main = QWidget()
        self.main.layout = QVBoxLayout()
        self.main.setLayout(self.main.layout)

        self.initUI()

    def initUI(self):
        self.steamFolderLabel = QLabel(settings.value("hunt_dir","<i>ex: C:/Steam/steamapps/common/Hunt Showdown</i>"))
        self.steamFolderButton = QPushButton("Select Hunt Installation Directory")
        self.steamFolderButton.clicked.connect(self.SelectFolderDialog)
        self.main.layout.addWidget(self.steamFolderLabel)
        self.main.layout.addWidget(self.steamFolderButton)
        self.main.layout.addWidget(QLabel())

        self.steamNameInput = QLineEdit(settings.value("steam_name","steam name not set"))
        self.steamNameInput.returnPressed.connect(self.ChangeSteamName)
        self.steamNameInput.setDisabled(True)
        self.steamNameButton = QPushButton("Change Steam Name")
        self.steamNameButton.clicked.connect(self.ChangeSteamName)
        self.main.layout.addWidget(self.steamNameInput)
        self.main.layout.addWidget(self.steamNameButton)
        self.main.layout.addWidget(QLabel())

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
        self.main.layout.addWidget(QLabel())


        open_dir_button = QPushButton(" Open Settings Folder ")
        open_dir_button.setSizePolicy(QSizePolicy.Policy.Maximum,QSizePolicy.Policy.Maximum)
        open_dir_button.clicked.connect(lambda : os.startfile(app_data_path))
        self.main.layout.addWidget(open_dir_button)
        self.main.layout.setAlignment(open_dir_button,Qt.AlignmentFlag.AlignHCenter)

        self.setCentralWidget(self.main)

    def setKdaRange(self):
        settings.setValue("kda_range",self.KdaRangeDropBox.currentData())
    def setDropdownRange(self):
        settings.setValue("dropdown_range",self.dropdownRangeDropBox.currentData())

    def ChangeSteamName(self):
        if self.steamNameInput.isEnabled():
            if(len(self.steamNameInput.text()) > 0):
                settings.setValue("steam_name",self.steamNameInput.text())
                print('steam name updated')
                print(settings.value('steam_name'))
                self.steamNameInput.setText(settings.value("steam_name"))
                self.parent().update()
            self.steamNameInput.setDisabled(True)
        else:
            self.steamNameInput.setDisabled(False)
    
    def SelectFolderDialog(self):
        suffix = "user/profiles/default/attributes.xml"
        hunt_dir = QFileDialog.getExistingDirectory(self,"Select folder",settings.value('hunt_dir','.'))
        xml_path = os.path.join(hunt_dir,suffix)
        print(hunt_dir)
        print(xml_path)
        if not os.path.exists(xml_path):
            print('attributes.xml not found.')
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