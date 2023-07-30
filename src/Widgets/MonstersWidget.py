from PyQt6.QtWidgets import QWidget, QVBoxLayout, QSizePolicy, QPushButton, QGroupBox
from PyQt6.QtCore import QEvent
from resources import clearLayout
from Widgets.Popup import Popup
from Widgets.Label import Label

class MonstersWidget(QGroupBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout()
        self.setObjectName("MonstersWidget")
        self.setLayout(self.layout)
        self.setSizePolicy(QSizePolicy.Policy.Minimum,QSizePolicy.Policy.MinimumExpanding)
        self.setTitle("Monsters")

    def sanitizeMonsterNames(self, monster):
        match monster:
            case 'waterdevil': return 'Water Devil'
            case _: return monster.capitalize()      

    def update(self, monsters_killed):
        clearLayout(self.layout)
        n = sum(monsters_killed.values())
        values = ["%d %s" % (monsters_killed[m], m)
                  for m in monsters_killed if monsters_killed[m] > 0]

        title = Label("Monster kills: %d" % n)
        title.setSizePolicy(QSizePolicy.Policy.Fixed,QSizePolicy.Policy.Fixed)
        self.layout.addWidget(title)
        overflow = None
        i = 0
        for monster,kills in reversed(sorted(monsters_killed.items(),key=lambda item : item[1])):
            if kills > 0:
                if i < 3:
                    label = Label("%d %s" % (kills, self.sanitizeMonsterNames(monster)))
                    label.setSizePolicy(QSizePolicy.Policy.Fixed,QSizePolicy.Policy.Fixed)
                    self.layout.addWidget(label)
                    #i += 1
                else:
                    if overflow == None:
                        overflow = QPushButton(" > > ")
                        overflow.setObjectName("link")
                        overflow.setSizePolicy(QSizePolicy.Policy.Fixed,QSizePolicy.Policy.Fixed)
                        overflow.installEventFilter(self)
                        overflow.data = {}
                    overflow.data[monster] = kills
        if overflow != None:
            self.layout.addWidget(overflow)
        self.adjustSize()

    def eventFilter(self, obj, event) -> bool:
        if obj.objectName() == "overflow":
            if event.type() == QEvent.Type.Enter:
                info = QWidget()
                info.layout = QVBoxLayout()
                info.setLayout(info.layout)
                x = event.globalPosition().x()
                y = event.globalPosition().y()
                for d in obj.data:
                    info.layout.addWidget(Label("%d %s" % (obj.data[d],d)))
                self.popup = Popup(info, x, y)
                # self.popup.keepAlive(True)
                self.popup.show()
                self.raise_()
                self.activateWindow()
            elif event.type() == QEvent.Type.Leave:
                try:
                    self.popup.hide()
                except:
                    self.popup = None
                pass
        return super().eventFilter(obj, event)