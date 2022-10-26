from PyQt6.QtWidgets import QMainWindow,QWidget,QVBoxLayout, QGridLayout, QGroupBox, QPushButton,QLabel, QFileDialog, QSizePolicy, QLineEdit
from PyQt6.QtCore import Qt
from resources import *

class SettingsWindow(QMainWindow):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        self.setObjectName("SettingsWindow")

        self.main = QWidget()
        self.main.layout = QGridLayout()
        self.main.setLayout(self.main.layout)

        self.initUI()

    def initUI(self):

        self.steamFolderLabel = QLabel(settings.value("hunt_dir","<i>ex: C:/Steam</i>"))
        self.steamFolderButton = QPushButton("Select Steam Installation Directory")
        self.steamFolderButton.clicked.connect(self.SelectFolderDialog)
        self.main.layout.addWidget(self.steamFolderButton,0,0)
        self.main.layout.addWidget(self.steamFolderLabel,0,1)

        self.steamNameInput = QLineEdit(settings.value("steam_name","steam name not set"))
        self.steamNameInput.returnPressed.connect(self.ChangeSteamName)
        self.steamNameInput.setDisabled(True)
        self.steamNameButton = QPushButton("Change Steam Name")
        self.steamNameButton.clicked.connect(self.ChangeSteamName)
        self.main.layout.addWidget(self.steamNameButton,1,0)
        self.main.layout.addWidget(self.steamNameInput,1,1)

        open_dir_button = QPushButton(" Open Settings Folder ")
        open_dir_button.setSizePolicy(QSizePolicy.Policy.Maximum,QSizePolicy.Policy.Maximum)
        open_dir_button.clicked.connect(lambda : os.startfile(app_data_path))
        self.main.layout.addWidget(open_dir_button,2,0,1,2)
        self.main.layout.setAlignment(open_dir_button,Qt.AlignmentFlag.AlignHCenter)

        self.setCentralWidget(self.main)


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
        hunt = "steamapps/common/Hunt Showdown"
        suffix = "user/profiles/default/attributes.xml"
        steam_dir = QFileDialog.getExistingDirectory(self,"Select folder",settings.value('steam_dir','.'))
        hunt_dir = os.path.join(steam_dir,hunt)
        xml_path = os.path.join(hunt_dir,suffix)
        print(steam_dir)
        print(hunt_dir)
        print(xml_path)
        if not os.path.exists(xml_path):
            print('attributes.xml not found.')
            return
        settings.setValue('steam_dir',steam_dir)
        settings.setValue('hunt_dir',hunt_dir)
        settings.setValue('xml_path',xml_path)
        self.steamFolderLabel.setText(settings.value("steam_dir"))
        if not self.parent().logger.running:
            self.parent().StartLogger()

    def show(self):
        self.steamFolderLabel.setText(settings.value("steam_dir"))
        self.steamNameInput.setText(settings.value("steam_name"))
        super().show()