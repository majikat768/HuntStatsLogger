from PyQt6.QtWidgets import QGroupBox,QWidget
from PyQt6.QtCore import Qt,QObject

class GroupBox(QGroupBox):
    def __init__(self,layout,title=''):
        super().__init__()
        #self.setTitle(title)
        self.layout = layout
        self.setLayout(self.layout)
        self.alignment = None

    def addWidget(self,widget,row=0,column=0,rowspan=1,colspan=1,alignment=Qt.AlignmentFlag.AlignLeft):
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