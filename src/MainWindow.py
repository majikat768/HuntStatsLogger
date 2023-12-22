from PyQt6 import QtCore, QtGui
from PyQt6.QtCore import Qt, QThread
from PyQt6.QtWidgets import QMainWindow, QWidget, QStatusBar
from Widgets.Menu.Menu import Menu
from Listener import Listener
from resources import MENU_ICON_SIZE, settings
from Body import Body

class MainWindow(QMainWindow):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        self.setWindowTitle("Hunt Showdown Companion App")

        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.font().setPixelSize(16)
        self.statusBar.setSizeGripEnabled(True)

        self.listener = Listener(self)

        thread = QThread(parent=self)
        self.listener.moveToThread(thread)
        thread.started.connect(self.listener.run)
        self.listener.finished.connect(thread.quit)
        self.listener.finished.connect(thread.deleteLater)
        self.listener.progress.connect(self.main_update)

        thread.start()

        self.body = Body(self)
        self.menu = Menu(parent=self.body)
        self.body.menu = self.menu

        # move window to last known position / size
        # fixed by @monsterdhal
        if settings.value("geometry") != None:
            self.restoreGeometry(settings.value("geometry"))
        if settings.value("windowState") != None:
            self.restoreState(settings.value("windowState"))

        self.setContentsMargins(0,0,0,0)
        self.setMouseTracking(True)



        self.body.setContentsMargins(self.menu.sizeHint().width(),0,0,0)

        self.setCentralWidget(self.body)

        self.setMinimumHeight(MENU_ICON_SIZE*len(self.menu.buttons)*3)


    def main_update(self):
        self.body.update()

    def resizeEvent(self, event: QtGui.QResizeEvent) -> None:
        self.menu.resize(event.size().height() - self.statusBar.height())
        #self.body.resize(event)
        self.setMinimumWidth(self.sizeHint().width())
        #self.setMinimumHeight(self.sizeHint().height())
        return super().resizeEvent(event)

    def setStatus(self,txt):
        self.statusBar.showMessage(txt)

    def closeEvent(self, a0) -> None:
        settings.setValue("geometry",self.saveGeometry())
        settings.setValue("windowState",self.saveState())
        return super().closeEvent(a0)