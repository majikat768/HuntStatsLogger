from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QSizePolicy
from resources import clearLayout

class MonstersWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.setSizePolicy(
            QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)

    def update(self, monsters_killed):
        clearLayout(self.layout)
        n = sum(monsters_killed.values())
        values = ["%d %s" % (monsters_killed[m], m)
                  for m in monsters_killed if monsters_killed[m] > 0]

        title = QLabel("Monster kills: %d" % n)
        title.setSizePolicy(QSizePolicy.Policy.Fixed,QSizePolicy.Policy.Fixed)
        self.layout.addWidget(title)
        for m in monsters_killed:
            if monsters_killed[m] > 0:
                label = QLabel("%d %s" % (monsters_killed[m],m))
                label.setSizePolicy(QSizePolicy.Policy.Fixed,QSizePolicy.Policy.Fixed)
                self.layout.addWidget(label)