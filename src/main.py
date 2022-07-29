import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QFontDatabase
import Logger, App, Connection

def killall():
    Logger.killall = True
    Connection.killall = True

if __name__ == '__main__':
    app = QApplication(sys.argv)

    QFontDatabase.addApplicationFont('./assets/fonts/LibreBaskerville/LibreBaskerville-Regular.ttf')
    stylesheet = open('./assets/MaterialDark.qss','r').read()

    app.setStyleSheet(stylesheet)
    app.aboutToQuit.connect(killall)

    if len(sys.argv) > 1:
        if sys.argv[1] == '-nogui':
            logger = Logger.Logger()
            logger.run()
        elif sys.argv[1] == '-nolog':
            ex2 = App.App(log=False)

            app.exec_()

    else:

        ex2 = App.App()
        app.exec_()

        Logger.killall = True
        Connection.killall = True