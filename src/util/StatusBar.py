from PyQt6.QtWidgets import QStatusBar,QPushButton,QWIDGETSIZE_MAX,QApplication
from resources import *

class StatusBar(QStatusBar):
    def __init__(self, parent = None):
        super().__init__(parent)
        self.setEnabled(True)
        self.setStyleSheet("QSizeGrip{image: url(\"%s\")};QStatusBar{font-family:courier new;}" % resource_path("assets/icons/sizegrip.png").replace("\\","/"))

        self.toggleButton = QPushButton("roll up")
        self.toggleButton.setStyleSheet("QPushButton{font-size:12px;}")
        self.toggleButton.clicked.connect(self.toggle)

        self.addPermanentWidget(self.toggleButton)
        #self.show()

    def toggle(self):
        if self.parent().mainframe.isVisible():
            self.origSize = self.window().size()
            self.parent().mainframe.hide()
            self.window().setMinimumHeight(self.window().sizeHint().height())
            self.window().setMaximumHeight(self.window().sizeHint().height())

            #self.parent().mainframe.body.hide()
            #self.parent().mainframe.settingsButton.hide()
            #self.window().setMinimumHeight(self.parent().mainframe.sizeHint().height())
            #self.window().setMaximumHeight(self.parent().mainframe.sizeHint().height()+self.sizeHint().height()*2.5)

            self.toggleButton.setText("roll down") 
        else:
            self.parent().mainframe.show()
            self.window().setMinimumHeight(self.parent().mainframe.sizeHint().height()/2)
            self.window().setMaximumHeight(QApplication.primaryScreen().size().height())

            #self.parent().mainframe.body.show()
            #self.parent().mainframe.settingsButton.show()

            self.window().adjustSize()
            self.toggleButton.setText("roll up") 

    def showMessage(self, message: str, msecs: int = ...) -> None:
        return super().showMessage(message)