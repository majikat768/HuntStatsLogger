from PyQt6.QtWidgets import QLabel
from resources import *

class HunterLabel(QLabel):
    instanceList = []
    HideUsers = False
    maxLen = 24 

    def __init__(self,name=''):
        super().__init__()
        self.name = name
        self.fullname = name
        if len(self.name) > HunterLabel.maxLen:
            self.name = self.name[:HunterLabel.maxLen-3]+'...'
        self.setWordWrap(True)

        super().setText(self.name)
        self.setToolTip(self.fullname)

        if(HunterLabel.HideUsers and self.name != settings.value('steam_name','')):
            self.HideUsername()
        HunterLabel.instanceList.append(self)
    
    def setText(self, a0: str) -> None:
        self.name = a0
        super().setText(self.name)
        if(HunterLabel.HideUsers and self.name != settings.value('steam_name','')):
            self.HideUsername()
        if self.name == settings.value('steam_name'):
            super().setStyleSheet('QLabel{color:#cccc67;}')
        else:
            super().setStyleSheet('QLabel{color:#a9b7c6;}')

    def HideUsername(self):
        if self.name != settings.value('steam_name'):
            super().setText('Hunter')
            super().setStyleSheet('QLabel{font-style:italic;color:#a9b7c6}')
        else:
            super().setStyleSheet('QLabel{color:#cccc67;}')

    def ShowUsername(self):
        super().setText(self.name)
        if self.name != settings.value('steam_name'):
            super().setStyleSheet('QLabel{font-style:none;color:#a9b7c6}')
        else:
            super().setStyleSheet('QLabel{color:#cccc67;}')

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