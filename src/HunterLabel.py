from PyQt6.QtWidgets import QLabel
from PyQt6.QtCore import QSettings

settings = QSettings('./settings.ini',QSettings.Format.IniFormat)

class HunterLabel(QLabel):
    instanceList = []
    HideUsers = False
    maxLen = 16

    def __init__(self,name=''):
        super().__init__()
        self.name = name
        self.fullname = name
        if len(self.name) > HunterLabel.maxLen:
            self.name = self.name[:HunterLabel.maxLen-3]+'...'

        super().setText(self.name)
        self.setToolTip(self.fullname)
        if(HunterLabel.HideUsers and self.name != settings.value('hunterName','')):
            self.HideUsername()
        HunterLabel.instanceList.append(self)
    
    def setText(self, a0: str) -> None:
        self.name = a0
        super().setText(self.name)
        if(HunterLabel.HideUsers and self.name != settings.value('hunterName','')):
            self.HideUsername()
    
    def HideUsername(self):
        if self.name != settings.value('hunterName',''):
            super().setText('Hunter')
            super().setStyleSheet('QLabel{font-style:italic;}')

    def ShowUsername(self):
        super().setText(self.name)
        super().setStyleSheet('QLabel{font-style:none;}')

    def ToggleNames():
        toremove = []
        for instance in HunterLabel.instanceList:
            try:
                if HunterLabel.HideUsers:
                    instance.HideUsername()
                else:
                    instance.ShowUsername()
            except:
                toremove.append(instance)
        for instance in toremove:
            HunterLabel.instanceList.remove(instance)