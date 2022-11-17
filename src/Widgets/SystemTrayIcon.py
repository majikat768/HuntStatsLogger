from PyQt6.QtWidgets import QSystemTrayIcon, QMenu, QMessageBox
from PyQt6.QtGui import QIcon, QCursor
from resources import resource_path
import sys

class SystemTrayIcon(QSystemTrayIcon):
    def __init__(self,parent=None):
        super().__init__(parent)
        self.setIcon(QIcon(resource_path('assets/icons/hsl.ico')))

        self.menu = QMenu(parent)
        exit_ = self.menu.addAction("Exit")
        exit_.triggered.connect(lambda : self.setParent(None))
        exit_.triggered.connect(self.deleteLater)
        exit_.triggered.connect(sys.exit)

        self.setContextMenu(self.menu)

        self.activated.connect(lambda reason : self.clicked(reason))

        self.setToolTip("Hunt Stats Logger")
        
        self.menu.popup(QCursor.pos())
        self.show()

    def clicked(self, reason) -> None:
        print(reason)
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            print('trigger')
            self.parent().show()
            self.parent().raise_()
            self.parent().activateWindow()
        elif reason == QSystemTrayIcon.ActivationReason.Context:
            self.menu.popup(QCursor.pos())