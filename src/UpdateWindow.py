from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout
from Widgets import Modal

class UpdateWindow(Modal):
    def __init__(self,updates,parent=None):
        win = QMainWindow()
        w = QWidget()
        w.layout = QVBoxLayout()
        w.setLayout(w.layout)