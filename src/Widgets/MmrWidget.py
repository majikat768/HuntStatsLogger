from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtGui import QPixmap, QColor, QPainter
from DbHandler import GetCurrentMmr, GetBestMmr
from resources import mmr_to_stars, star_path

star_size = 16

class MmrWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.mmrLabel = QLabel()
        self.bestLabel = QLabel()
        self.starsLabel = QLabel()

        self.mmr = GetCurrentMmr()
        self.stars = mmr_to_stars(self.mmr)

        self.layout.addWidget(self.starsLabel)
        self.layout.addWidget(self.mmrLabel)
        self.layout.addWidget(self.bestLabel)
        self.layout.addStretch()

    def set_stars(self):
        self.starsLabel.setText(("<img src='%s'>" % star_path())*self.stars)

    def update(self):
        self.mmr = GetCurrentMmr()
        self.stars = mmr_to_stars(self.mmr)
        self.mmrLabel.setText("MMR: %d" % self.mmr)
        self.bestLabel.setText("Best: %d" % GetBestMmr())
        self.set_stars()