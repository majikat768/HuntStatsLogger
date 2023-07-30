from PyQt6.QtWidgets import QWidget, QHBoxLayout, QGraphicsOpacityEffect
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QAbstractAnimation, QPoint
from PyQt6.QtGui import QFont, QColor
from Widgets.Label import Label
from resources import resource_path

# adapted from
#   https://github.com/yjg30737/pyqt-toast
#

class Toast(QWidget):
    def __init__(self, text, duration=2, widgets=[],parent=None):
        super().__init__(parent)
        self.__initVal(parent, duration)
        self.__initUi(text,widgets)

        stylesheet = open(resource_path('./assets/MaterialDark.qss'), 'r').read()
        self.setStyleSheet(stylesheet)

    def show(self):
        print('showtoast')
        if self.__timer.isActive():
            pass
        else:
            self.__animation.setDirection(QAbstractAnimation.Direction.Forward)
            self.__animation.start()
            self.raise_()
            if self.__duration > 0:
                self.__initTimeout()
        return super().show()


    def __initVal(self, parent, duration):
        self.__parent = parent
        self.__timer = QTimer(self)
        self.__duration = duration
        self.__opacity = 0.95
        self.__foregroundColor = '#464646'
        self.__backgroundColor = '#aacc44'
        self.__parent.installEventFilter(self)
        self.installEventFilter(self)

    def __initUi(self, text,widgets=[]):
        self.main = QWidget()
        self.main.setObjectName("toast")
        self.main.layout = QHBoxLayout()
        self.main.setLayout(self.main.layout)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.SubWindow)
        #self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)

        # text in toast (toast foreground)
        self.__lbl = Label(text)
        self.__lbl.setObjectName('popupLbl')

        self.__lbl.setMinimumWidth(self.__lbl.fontMetrics().boundingRect(text).width() * 1)
        self.__lbl.setMinimumHeight(self.__lbl.fontMetrics().boundingRect(text).height() * 2)
        self.__lbl.setWordWrap(False)

        self.__widgets = widgets

        # animation
        self.__initAnimation()

        # toast background
        self.main.layout.addWidget(self.__lbl)
        for widget in self.__widgets:
            widget.setMinimumHeight(widget.sizeHint().height())
            self.main.layout.addWidget(widget)

        self.__setToastSizeBasedOnTextSize()
        self.layout = QHBoxLayout()
        self.setLayout(self.layout)
        self.layout.addWidget(self.main)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)

    def __setOpacity(self, opacity):
        opacity_effect = QGraphicsOpacityEffect(opacity=opacity)
        self.setGraphicsEffect(opacity_effect)

    def __initAnimation(self):
        self.__animation = QPropertyAnimation(self, b"windowOpacity",self)
        self.__animation.setStartValue(0.0)
        self.__animation.setTargetObject(self)
        self.__animation.setDuration(500)
        self.__animation.setEndValue(self.__opacity)
        self.__animation.valueChanged.connect(self.__setOpacity)
        self.setGraphicsEffect(QGraphicsOpacityEffect(opacity=0.0))

    def __initTimeout(self):
        self.__timer = QTimer(self)
        self.__timer_to_wait = self.__duration
        self.__timer.setInterval(1000)
        self.__timer.timeout.connect(self.__changeContent)
        self.__timer.start()

    def __changeContent(self):
        self.__timer_to_wait -= 1
        if self.__timer_to_wait <= 0:
            self.__animation.setDirection(QAbstractAnimation.Direction.Backward)
            self.__animation.start()
            self.__timer.stop()

    def close(self):
        self.__animation.setDirection(QAbstractAnimation.Direction.Backward)
        self.__animation.start()

    def setPosition(self, pos):
        geo = self.geometry()
        geo.moveCenter(pos)
        self.setGeometry(geo)

    def setAlignment(self, alignment):
        self.__lbl.setAlignment(alignment)

    def isVisible(self) -> bool:
        return self.__timer.isActive()

    def setFont(self, font: QFont):
        self.__lbl.setFont(font)
        self.__setToastSizeBasedOnTextSize()

    def __setToastSizeBasedOnTextSize(self):
        self.setFixedWidth(self.main.sizeHint().width() * 2)
        self.setFixedHeight(self.main.sizeHint().height() * 2)

    def setDuration(self, duration: int):
        self.__duration = duration
        self.__initAnimation()

    def setForegroundColor(self, color: QColor):
        if isinstance(color, str):
            color = QColor(color)
        self.__foregroundColor = color.name()

    def setBackgroundColor(self, color: QColor):
        if isinstance(color, str):
            color = QColor(color)
        self.__backgroundColor = color.name()

    def __setForegroundColor(self):
        self.__lbl.setStyleSheet(f'QLabel#popupLbl {{ color: {self.__foregroundColor}; font-style:bold; }}')

    def __setBackgroundColor(self):
        pass

    def setOpacity(self, opacity: float):
        self.__opacity = opacity
        self.__initAnimation()

    def eventFilter(self, obj, e) -> bool:
        if e.type() == 14:
            self.setPosition(QPoint(self.__parent.rect().center().x(), self.__parent.rect().y()+self.height()//2))
        elif isinstance(obj, Toast):
            if e.type() == 75:
                self.__setForegroundColor()
                self.__setBackgroundColor()
        return super().eventFilter(obj, e)