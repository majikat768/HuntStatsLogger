from PyQt6.QtWidgets import QStatusBar,QPushButton,QWIDGETSIZE_MAX,QWidget,QMainWindow
from resources import *

class StatusBar(QStatusBar):
    instances = []
    def setStatus(text,color="#02cf7f"):
        for status in StatusBar.instances:
            status.showMessage(text)
            #status.setStyleSheet(status.styleSheet() + "StatusBar{color:%s}" % color)

    def __init__(self, parent = None):
        super().__init__(parent)
        StatusBar.instances.append(self)
        self.setEnabled(True)
        self.setObjectName('statusbar')
        self.setStyleSheet("QSizeGrip{image: url(\"%s\")}" % resource_path("assets/icons/sizegrip.png").replace("\\","/"))

        self.toggleButton = QPushButton("roll up")
        self.toggleButton.setStyleSheet("QPushButton{font-size:12px;}")
        self.toggleButton.clicked.connect(self.toggle)

        self.addPermanentWidget(self.toggleButton)

        self.rolledUp = False
        self.keep = []


    def toggle(self):
        main = self.window().centralWidget()
        if not self.rolledUp:
            self.rolledUp = True
            for w in main.children():
                if isinstance(w,QWidget) and not isinstance(w,QMainWindow) and w not in self.keep:
                    w.hide()
            main.adjustSize()
            self.window().setMinimumHeight(self.window().sizeHint().height())
            self.window().setMaximumHeight(self.window().sizeHint().height())
            self.toggleButton.setText("roll down") 

        else:
            self.rolledUp = False
            for w in main.children():
                if isinstance(w,QWidget) and not isinstance(w,QMainWindow):
                    w.show()
            self.window().setMinimumHeight(self.window().sizeHint().height()//2)
            self.window().setMaximumHeight(self.window().sizeHint().height()*2)
            self.window().setBaseSize(self.window().mainframe.sizeHint())

            self.window().adjustSize()
            self.toggleButton.setText("roll up") 