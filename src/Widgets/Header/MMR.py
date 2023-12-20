from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, QSizePolicy
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from resources import stars_pixmap, mmr_to_stars, settings
from DbHandler import get_new_mmr, get_best_mmr

class MMR(QWidget):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

        self.layout = QHBoxLayout()
        self.setLayout(self.layout)

        self.layout.setContentsMargins(0,0,8,0)
        self.layout.setSpacing(16)

        self.mmr = get_new_mmr() 
        self.best_mmr = get_best_mmr()
        self.mmrLabel = QLabel(str(self.mmr))
        self.mmrLabel.setSizePolicy(QSizePolicy.Policy.Fixed,QSizePolicy.Policy.Fixed)
        font = self.mmrLabel.font()
        font.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing,4)
        self.mmrLabel.setFont(font)
        self.starLabel = QLabel()
        self.starLabel.setSizePolicy(QSizePolicy.Policy.Fixed,QSizePolicy.Policy.Fixed)

        self.layout.addStretch()
        self.layout.addWidget(self.starLabel)
        self.layout.setAlignment(self.starLabel,Qt.AlignmentFlag.AlignRight)
        self.layout.addWidget(self.mmrLabel)
        self.layout.setAlignment(self.mmrLabel,Qt.AlignmentFlag.AlignRight)

        self.update()

    def update(self):
        self.mmr = get_new_mmr()
        self.best_mmr = get_best_mmr()
        self.mmrLabel.setText(str(self.mmr))
        self.mmrLabel.setToolTip("Best: %d" % self.best_mmr)
        self.starLabel.setPixmap(stars_pixmap(mmr_to_stars(self.mmr)))