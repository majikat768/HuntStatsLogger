from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QSizePolicy
from resources import clearLayout

class BountiesWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QHBoxLayout()
        self.setLayout(self.layout)
        self.setSizePolicy(
            QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)

    def update(self, qp, bounties, targets):
        clearLayout(self.layout)
        text = []
        if qp:
            widget = QWidget()
            widget.layout = QVBoxLayout()
            widget.setLayout(widget.layout)
            widget.layout.addWidget(QLabel("Quick Play"))
            widget.layout.addWidget(QLabel("closed %d rifts." % bounties['rifts_closed']))
            self.layout.addWidget(widget)
        else:
            widgets = []
            for name in targets:
                text = []
                widget = QWidget()
                widget.layout = QVBoxLayout()
                widget.setLayout(widget.layout)

                boss = bounties[name.lower()]
                bossLabel = QLabel("%s" % name.capitalize())
                bossLabel.setObjectName("BountyHeading")
                if sum(boss.values()) > 0:
                    text.append("Found %d clues." % boss['clues'])
                    if boss['killed']:
                        text.append("Killed.")
                    if boss['banished']:
                        text.append("Banished.")
                else:
                    text.append('')

                widget.layout.addWidget(bossLabel)
                for line in text:
                    label = QLabel(line)
                    label.setSizePolicy(QSizePolicy.Policy.Fixed,QSizePolicy.Policy.Fixed)
                    widget.layout.addWidget(label)
                widget.layout.addStretch()
                widgets.append(widget)
            for i in range(len(widgets)):
                widget = widgets[i]
                self.layout.addWidget(widget)
                if i < len(widgets)-2:
                    self.layout.addStretch()