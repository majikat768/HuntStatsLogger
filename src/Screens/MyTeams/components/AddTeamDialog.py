from PyQt6.QtWidgets import QWidget, QGridLayout, QLabel, QDialog, QLineEdit, QDialogButtonBox
from resources import settings
from DbHandler import get_pid_from_bloodlinename

class AddTeamDialog(QDialog):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

        self.first = QLineEdit()
        self.first.setText(settings.value("steam_name"))
        self.first.setDisabled(True)
        self.second = QLineEdit()
        self.third = QLineEdit()

        self.buttonBox = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.buttonBox.rejected.connect(self.reject)
        self.buttonBox.accepted.connect(self.accept)

        self.layout = QGridLayout()
        self.setLayout(self.layout)

        self.layout.addWidget(QLabel("Enter one or two hunter names:"),0,0,1,2)
        self.layout.addWidget(QLabel("You: "),1,0)
        self.layout.addWidget(self.first,1,1)
        self.layout.addWidget(QLabel("Hunter 2: "),2,0)
        self.layout.addWidget(self.second,2,1)
        self.layout.addWidget(QLabel("Hunter 3: "),3,0)
        self.layout.addWidget(self.third,3,1)
        self.layout.addWidget(self.buttonBox,4,0,1,2)

        self.errorText = QLabel()
        self.errorText.setVisible(False)
        self.layout.addWidget(self.errorText,5,0,1,2)

    def accept(self) -> None:
        self.errorText.setVisible(False)
        hunters = self.get_values()
        hunters = [h for h in hunters if len(h) > 0]
        pids = []
        for name in hunters:
            pid = get_pid_from_bloodlinename(name)
            if(pid < 0):
                self.setErrorText("Could not find hunter '%s'." % name)
                return False    # do something error handley here
            pids.append(pid)
        print(pids)
        current_teams = eval(settings.value("my_teams","[]"))
        if pids not in current_teams:
            current_teams.append(pids)
            settings.setValue("my_teams",str(current_teams))
        self.second.setText("")
        self.third.setText("")
        return super().accept()

    def get_values(self):
        res = [
            self.first.text(),
            self.second.text(),
            self.third.text()
        ]
        return res

    def setErrorText(self,text):
        self.errorText.setVisible(True)
        self.errorText.setText(text)