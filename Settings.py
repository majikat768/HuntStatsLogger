from PyQt5.QtWidgets import QPushButton,QLabel,QLineEdit,QFileDialog, QSizePolicy
from PyQt5.QtCore import Qt, QSettings

from GroupBox import GroupBox

class Settings(GroupBox):
    def __init__(self,parent,layout,title=''):
        super().__init__(layout,title)
        self.parent = parent
        self.settings = QSettings('majikat','HuntStats')
        self.layout = layout
        self.setLayout(self.layout)
        self.layout.setAlignment(Qt.AlignLeft)

        self.setSizePolicy(QSizePolicy.MinimumExpanding,QSizePolicy.Maximum)
        self.huntDirButton = QPushButton('Select Hunt Installation Directory')
        self.huntDirButton.clicked.connect(self.SelectHuntFolder)
        self.huntDirLabel = QLabel(self.settings.value('huntDir','select Hunt Installation Directory'))
        self.layout.addWidget(self.huntDirButton,0,0)
        self.layout.addWidget(self.huntDirLabel,0,1)
        self.layout.setRowStretch(0,0)

        self.nameInputButton = QPushButton('Update Steam Name')
        self.nameInput = QLineEdit(self.settings.value('hunterName',''))
        self.nameInput.setPlaceholderText('Enter your Steam username')
        self.nameInput.setVisible(False)
        self.nameLabel = QLabel(self.settings.value('hunterName',''))
        self.nameInputButton.clicked.connect(self.UpdateHunterName)
        self.nameInput.returnPressed.connect(self.UpdateHunterName)

        self.layout.addWidget(self.nameInputButton,1,0)
        self.layout.addWidget(self.nameLabel,1,1)
        self.layout.addWidget(self.nameInput,1,1)
        self.layout.setRowStretch(1,0)

        self.layout.setRowStretch(self.layout.rowCount(),1)
    
    def SelectHuntFolder(self):
        options = QFileDialog.Options()
        #options |= QFileDialog.DontUseNativeDialog
        directory = QFileDialog.getExistingDirectory(self, "Select Hunt Installation Directory",self.huntDir,options=options)
        if directory != '':
            print('directory set')
            self.settings.setValue('huntDir',directory)
            self.huntDirLabel.setText(self.settings.value('huntDir',''))

    def UpdateHunterName(self):
        if self.nameInput.isVisible():
            self.settings.setValue('hunterName',self.nameInput.text())
            self.nameLabel.setText(self.settings.value('hunterName',''))
            self.parent.UpdateHunterTab()
            self.nameInput.setVisible(False)
            self.nameLabel.setVisible(True)

        else:
            self.nameLabel.setVisible(False)
            self.nameInput.setVisible(True)
            self.nameInput.setFocus()