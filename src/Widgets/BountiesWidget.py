from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QSizePolicy
from resources import clearLayout

class BountiesWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.setSizePolicy(
            QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)

    def update(self, qp, bounties, targets):
        clearLayout(self.layout)
        text = []
        if qp:
            text.append("Quick Play")
            text.append("closed %d rifts." % bounties['rifts_closed'])
        else:
            for name in targets:
                boss = bounties[name.lower()]
                text.append("%s:" % name.capitalize())
                if sum(boss.values()) > 0:
                    if boss['clues'] > 0:
                        text.append("Found %d clues." % boss['clues'])
                    if boss['killed']:
                        text.append("Killed.")
                    if boss['banished']:
                        text.append("Banished.")
                else:
                    text.append('')

        for line in text:
            label = QLabel(line)
            label.setSizePolicy(QSizePolicy.Policy.Fixed,QSizePolicy.Policy.Fixed)
            self.layout.addWidget(label)
        self.layout.addStretch()