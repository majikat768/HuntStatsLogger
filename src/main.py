import sys, os

from util.StatusBar import StatusBar
# Append parent directory to import path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFontDatabase
from viewer.ViewerWindow import ViewerWindow
from resources import resource_path

if __name__ == '__main__':
    app = QApplication(sys.argv)
    QFontDatabase.addApplicationFont(resource_path('./assets/fonts/LibreBaskerville/LibreBaskerville-Regular.ttf'))
    stylesheet = open(resource_path('./assets/MaterialDark.qss'),'r').read()
    app.setStyleSheet(stylesheet)

    viewerWindow = ViewerWindow()
    viewerWindow.show()

    app.exec()