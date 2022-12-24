from PyQt6.QtWidgets import QMainWindow, QGraphicsOpacityEffect
from PyQt6.QtCore import Qt, QAbstractAnimation, QPropertyAnimation

class Popup(QMainWindow):
    def __init__(self, widget,x,y,parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.SubWindow) 
        self.setObjectName("popup")
        self.setCentralWidget(widget)

        self.setMaximumSize(self.sizeHint())
        self.move(int(x+self.size().width()/4),int(y-self.size().height()/4))

        self.opacity = 1
        self.animation = QPropertyAnimation(self, b"windowOpacity",self)
        self.animation.setStartValue(0.0)
        self.animation.setTargetObject(self)
        self.animation.setDuration(200)
        self.animation.setEndValue(self.opacity)
        self.animation.valueChanged.connect(self.setOpacity)
        self.setGraphicsEffect(QGraphicsOpacityEffect(opacity=0.0))

    def keepAlive(self,keep):
        if(keep):
            self.setWindowFlag(Qt.WindowType.Popup)

    def show(self) -> None:
        self.animation.setDirection(QAbstractAnimation.Direction.Forward)
        self.animation.start()
        return super().show()

    def hide(self):
        self.animation.setDirection(QAbstractAnimation.Direction.Backward)
        self.animation.start()

    def close(self) -> bool:
        return super().close()

    def setOpacity(self,opacity: float):
        opacity_effect = QGraphicsOpacityEffect(opacity=opacity)
        self.setGraphicsEffect(opacity_effect)
        self.opacity = opacity
        if self.opacity == 0.0:
            self.close()


