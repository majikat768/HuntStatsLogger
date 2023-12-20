from PyQt6.QtWidgets import QMainWindow, QWidget, QLabel, QPushButton, QVBoxLayout, QLineEdit, QSizePolicy, QHBoxLayout
from PyQt6.QtCore import Qt
from resources import *
from Settings.Dialogs import *

class Settings(QMainWindow):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setCentralWidget(SettingsMain(self.parent()))

class SettingsMain(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.setObjectName("SettingsWindow")

        self.initUI()

        self.setBaseSize(self.sizeHint().height(),self.sizeHint().width()*2)

    def initUI(self):
        self.initSteamOptions()
        self.layout.addStretch()
        settingsDirButton = QPushButton("Open Settings Folder")
        settingsDirButton.clicked.connect(lambda : os.startfile(app_data_path))
        settingsDirButton.setSizePolicy(QSizePolicy.Policy.Fixed,QSizePolicy.Policy.Fixed)
        self.layout.addWidget(settingsDirButton)
        self.layout.setAlignment(settingsDirButton,Qt.AlignmentFlag.AlignHCenter)
        huntDirButton = QPushButton(" Open Hunt Directory ")
        huntDirButton.clicked.connect(lambda : os.startfile(settings.value("hunt_dir",".")))
        huntDirButton.setSizePolicy(QSizePolicy.Policy.Fixed,QSizePolicy.Policy.Fixed)
        self.layout.addWidget(huntDirButton)
        self.layout.setAlignment(huntDirButton,Qt.AlignmentFlag.AlignHCenter)
 

    def initSteamOptions(self):
        self.steamName = QWidget()
        self.steamName.layout = QHBoxLayout()
        self.steamName.setLayout(self.steamName.layout)
        self.steamNameInput = QLineEdit(settings.value("steam_name","Set steam name"))
        self.steamNameInput.returnPressed.connect(lambda : ChangeSteamName(self))
        self.steamNameInput.setDisabled(True)
        self.steamNameButton = QPushButton("Set Steam Name")
        self.steamNameButton.setSizePolicy(QSizePolicy.Policy.Fixed,QSizePolicy.Policy.Fixed)
        self.steamNameButton.clicked.connect(lambda : ChangeSteamName(self))

        self.steamName.layout.addWidget(self.steamNameInput)
        self.steamName.layout.addWidget(self.steamNameButton)
        self.layout.addWidget(self.steamName)
        self.layout.setAlignment(self.steamName,Qt.AlignmentFlag.AlignHCenter)

        self.steamDirLabel = QLabel(settings.value("steam_dir","<i>Select Steam Folder</i>"))
        self.layout.addWidget(self.steamDirLabel)
        self.setSteamDir = QPushButton("Select Steam Folder")
        self.setSteamDir.clicked.connect(lambda : SelectSteamFolderDialog(self))
        self.setSteamDir.setSizePolicy(QSizePolicy.Policy.Fixed,QSizePolicy.Policy.Fixed)
        self.layout.addWidget(self.setSteamDir)
        self.layout.setAlignment(self.setSteamDir,Qt.AlignmentFlag.AlignHCenter)

        self.huntDirLabel = QLabel()
        if len(settings.value("hunt_dir","")) > 0:
            if len(settings.value("steam_dir","")) > 0:
                self.huntDirLabel.setText(
                    settings.value("hunt_dir").replace(settings.value("steam_dir",None),"..."))
            else:
                self.huntDirLabel.setText(settings.value("hunt_dir"))
        else:
            self.huntDirLabel.setText("<i>Select Hunt Folder</i>")
        self.layout.addWidget(self.huntDirLabel)
        self.setHuntDir = QPushButton("Select Hunt Folder")
        self.setHuntDir.clicked.connect(lambda : SelectHuntFolderDialog(self))
        self.setHuntDir.setSizePolicy(QSizePolicy.Policy.Fixed,QSizePolicy.Policy.Fixed)
        self.layout.addWidget(self.setHuntDir)
        self.layout.setAlignment(self.setHuntDir,Qt.AlignmentFlag.AlignHCenter)