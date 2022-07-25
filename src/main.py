import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QFontDatabase
import Logger, App, Connection

def killall():
    Logger.killall = True
    Connection.killall = True

if __name__ == '__main__':
    if len(sys.argv) > 1:
        if sys.argv[1] == '-nogui':
            logger = Logger.Logger()
            logger.run()
        elif sys.argv[1] == '-nolog':
            #appctxt = ApplicationContext()
            app = QApplication(sys.argv)
            #app.setStyleSheet(open('./assets/stylesheet.qss','r').read())
            app.setStyleSheet(open('./assets/MaterialDark.qss','r').read())
            #app.setStyleSheet(open('./assets/ManjaroMix.qss','r').read())
            ex2 = App.App(log=False)
            #app.setStyleSheet(open('./assets/SpyBot.qss','r').read())


            app.exec_()

    else:
        #appctxt = ApplicationContext()
        app = QApplication(sys.argv)
        app.aboutToQuit.connect(killall)
        #app.setStyleSheet(open('./assets/stylesheet.qss','r').read())
        QFontDatabase.addApplicationFont('assets/ubuntu/UbuntuMono-R.ttf')
        app.setStyleSheet(open('./assets/MaterialDark.qss','r').read())
        #app.setStyleSheet(open('./assets/ManjaroMix.qss','r').read())
        ex2 = App.App()
        #app.setStyleSheet(open('./assets/SpyBot.qss','r').read())
        app.exec_()
        Logger.killall = True
        Connection.killall = True