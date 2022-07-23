from PyQt5.QtWidgets import QGroupBox
from PyQt5.QtCore import Qt

class GroupBox(QGroupBox):
    def __init__(self,layout,title=''):
        super().__init__()
        self.setTitle(title)
        self.layout = layout
        self.setLayout(self.layout)
        self.alignment = None

    def addWidget(self,widget,row=0,column=0,rowspan=1,colspan=1,alignment=Qt.AlignLeft):
        if self.alignment != None:
            alignment = self.alignment
        if self.layout.__class__.__name__ == 'QGridLayout':
            self.layout.addWidget(widget,row,column,rowspan,colspan,alignment)
        else:
            self.layout.addWidget(widget,alignment)

    def setBorderVisible(self,visible):
        if(visible):
            self.setStyleSheet('GroupBox{border-style:solid;}')
        else:
            self.setStyleSheet('GroupBox{border-style:none;}')

    def setAlignment(self, a0: int) -> None:
        return super().setAlignment(a0)
        self.alignment = a0