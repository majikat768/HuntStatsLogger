from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QPushButton, QGroupBox
from Widgets.Label import Label
from DbHandler import get_hunter_encounters, get_all_names, execute_query
from resources import tab, settings

class HunterWindow(QMainWindow):
    def __init__(self, pid, parent: QWidget | None = None):
        super().__init__(parent)
        self.main = QWidget()
        self.main.layout = QVBoxLayout()
        self.main.setLayout(self.main.layout)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground)      
        self.main.layout.setContentsMargins(16,8,16,8)

        encounters = get_hunter_encounters(pid)
        if(len(encounters) >= 0):
            encounters = encounters[0][0]
            names = get_all_names(pid)
            self.main.layout.addWidget(Label(names[0][0]),alignment=Qt.AlignmentFlag.AlignCenter)
            if(len(names) > 1):
                aka = ListBox(names,"AKA:")
                self.main.layout.addWidget(aka)
        self.main.layout.addWidget(Label("Encountered %d times." % encounters))
        self.main.layout.addWidget(Label("You've killed them %d times." % self.get_kill_count(pid)))
        self.main.layout.addWidget(Label("They've killed you %d times." % self.get_killed_by_count(pid)))
        self.main.layout.addWidget(Label("Been on their team %d times." % self.get_team_count(pid)))
        self.main.layout.addStretch()

        closeButton = QPushButton("Close")
        closeButton.clicked.connect(self.close)
        self.main.layout.addWidget(closeButton)
        self.setCentralWidget(self.main)

    def get_kill_count(self,pid):
        count = execute_query(
            "select sum(h.killedbyme+h.downedbyme) from 'hunters' h where h.profileid = ?", pid)
        if len(count) == 0:
            return 0
        return count[0][0]

    def get_killed_by_count(self,pid):
        count = execute_query(
            "select sum(h.killedme+h.downedme) from 'hunters' h where h.profileid = ?", pid)
        if len(count) == 0:
            return 0
        return count[0][0]

    def get_team_count(self,pid):
        count = execute_query("select count(*)\
                              from 'hunters' h\
                              join 'hunters' h2 on h2.team_num = h.team_num and h2.timestamp = h.timestamp\
                              where h.profileid = ? and h2.profileid = ?", settings.value("profileid",0),pid)
        if len(count) == 0:
            return 0
        return count[0][0]

class ListBox(QWidget):
    def __init__(self,list,title=""):
        super().__init__()
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.layout.addWidget(Label(title))
        self.layout.setContentsMargins(8,8,8,8)
        self.layout.setSpacing(0)

        self.listWidget = QWidget()
        self.listWidget.layout = QVBoxLayout()
        self.listWidget.setLayout(self.listWidget.layout)
        self.listWidget.layout.setContentsMargins(0,0,0,0)
        self.listWidget.layout.setSpacing(0)

        for item in list:
            self.listWidget.layout.addWidget(Label("•%s%s" % (tab(),item[0])))

        self.layout.addWidget(self.listWidget)