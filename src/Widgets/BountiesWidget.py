from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QSizePolicy, QGroupBox
from resources import clearLayout
from Widgets.Label import Label

class BountiesWidget(QGroupBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("BountiesWidget")
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.setSizePolicy(QSizePolicy.Policy.Minimum,QSizePolicy.Policy.Expanding)
        self.setTitle("Bounties")

    def update(self, qp, bounties, targets):
        clearLayout(self.layout)
        text = []
        if qp:
            widget = QWidget()
            widget.layout = QVBoxLayout()
            widget.setLayout(widget.layout)
            widget.layout.addWidget(Label("Quick Play"))
            widget.layout.addWidget(Label("closed %d rifts." % bounties['rifts_closed']))
            self.layout.addWidget(widget)
        else:
            for name in targets:
                text = []
                widget = QWidget()
                widget.layout = QVBoxLayout()
                widget.setLayout(widget.layout)

                boss = bounties[name.lower()]
                bossLabel = Label("%s" % name.capitalize())
                bossLabel.setObjectName("BountyHeading")
                if sum(boss.values()) > 0:
                    text.append("\tFound %d clues." % boss['clues'])
                    if boss['killed']:
                        text.append("\tKilled.")
                    if boss['banished']:
                        text.append("\tBanished.")
                else:
                    text.append('')

                self.layout.addWidget(bossLabel)
                for line in text:
                    label = Label(line)
                    label.setSizePolicy(QSizePolicy.Policy.Fixed,QSizePolicy.Policy.Fixed)
                    self.layout.addWidget(label)
                    #widget.layout.addWidget(label)
                self.layout.addWidget(Label())
        self.layout.addStretch()