from Widgets.Modal import Modal
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QLabel, QHBoxLayout, QWidget, QLineEdit, QPushButton, QDialog
from DbHandler import execute_query
from resources import settings

class AddNewTeamWindow(Modal):
    def __init__(self, parent=None, flags=Qt.WindowType.Popup):
        super().__init__(parent, flags)

        self.addWidget(QLabel("Enter 2 or 3 hunter names"))

        hunter1widget = QWidget()
        hunter1widget.layout = QHBoxLayout()
        hunter1widget.setLayout(hunter1widget.layout)
        hunter1label = QLabel("1st Hunter: ")
        self.hunter1input = QLineEdit()
        hunter1widget.layout.addWidget(hunter1label)
        hunter1widget.layout.addWidget(self.hunter1input)

        hunter2widget = QWidget()
        hunter2widget.layout = QHBoxLayout()
        hunter2widget.setLayout(hunter2widget.layout)
        hunter2label = QLabel("2nd Hunter: ")
        self.hunter2input = QLineEdit()
        hunter2widget.layout.addWidget(hunter2label)
        hunter2widget.layout.addWidget(self.hunter2input)

        hunter3widget = QWidget()
        hunter3widget.layout = QHBoxLayout()
        hunter3widget.setLayout(hunter3widget.layout)
        hunter3label = QLabel("3rd Hunter: ")
        self.hunter3input = QLineEdit()
        hunter3widget.layout.addWidget(hunter3label)
        hunter3widget.layout.addWidget(self.hunter3input)

        self.addWidget(hunter1widget)
        self.addWidget(hunter2widget)
        self.addWidget(hunter3widget)

        teamSubmit = QPushButton("Submit")
        self.addWidget(teamSubmit)
        teamSubmit.clicked.connect(self.AddNewTeamSubmit)
        self.closeBtn.setText("Cancel")
        self.show()

    def AddNewTeamSubmit(self):
        hunters = []

        if len(self.hunter1input.text()) > 0:
            hunters.append(self.hunter1input.text())
        if len(self.hunter2input.text()) > 0:
            hunters.append(self.hunter2input.text())
        if len(self.hunter3input.text()) > 0:
            hunters.append(self.hunter3input.text())

        if len(hunters) < 2:
            self.ErrDialog("Need at least two team members.")
            return

        pids = []
        for hunter in hunters:
            pid = execute_query("select profileid from 'hunters' where blood_line_name = '%s' limit 1" % hunter)
            if len(pid) <= 0:
                self.ErrDialog("Hunter %s couldn't be found..." % hunter)
                break
            pids.append(pid[0][0])
        pids = sorted(pids)
        self.close()

        teams = eval(settings.value("my_teams","[]"))
        if pids not in teams:
            teams.append(pids)

        settings.setValue("my_teams",str(teams))

    def ErrDialog(self, txt):
        errDialog = Modal(parent=self)
        errDialog.addWidget(QLabel(txt))
        errDialog.show()

