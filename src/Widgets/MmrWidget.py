from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtGui import QPixmap, QColor, QPainter
from DbHandler import GetCurrentMmr, GetBestMmr
from resources import mmr_to_stars, star_path

star_size = 24

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
        pm = QPixmap(star_size*self.stars,star_size)
        pm.fill(QColor(0,0,0,0))
        painter = QPainter(pm)
        for i in range(self.stars):
            painter.drawPixmap(i*star_size,0,star_size,star_size,QPixmap(star_path()).scaled(star_size,star_size))
        del painter
        self.starsLabel.setPixmap(pm)

    def update(self):
        self.mmr = GetCurrentMmr()
        self.mmrLabel.setText("MMR: %d" % self.mmr)
        self.bestLabel.setText("Best: %d" % GetBestMmr())
        self.set_stars()