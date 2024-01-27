from PyQt6 import QtGui
from PyQt6 import QtCore
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel,QSizePolicy, QScrollArea
from Screens.HuntsRecap.components.HuntWidget import HuntWidget
from datetime import datetime
from DbHandler import get_n_hunts, record_exists
from resources import get_icon

cols = ["extracted","timestamp","kills","deaths","assists","team_kills","team_deaths"]

class HuntList(QScrollArea):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

        self.setWidgetResizable(True)
        self.main = QWidget()
        self.main.layout = QVBoxLayout()
        self.main.setLayout(self.main.layout)

        self.currentWidget = None

        self.main.layout.setSpacing(0)
        self.main.layout.setContentsMargins(0,0,0,0)
        self.main.setObjectName("HuntList")

        self.setWidget(self.main)

        self.huntsArray = []
        self.initHuntsList()

    def resize(self,event):
        self.setMinimumWidth(
            self.main.sizeHint().width() +
            2*self.frameWidth() +
            self.verticalScrollBar().sizeHint().width()
        )
        if(self.currentWidget != None):
            self.currentWidget.resize(self.window().height()*0.8)


    def getLatestHunt(self):
        print('get latest hunt')
        if(len(self.huntsArray) == 0):
            self.initHuntsList()
            return
        newHunt = get_n_hunts(1)
        print('new hunt')
        if len(newHunt) == 0:
            return
        if(len(self.huntsArray) > 0 and self.huntsArray[0]['game_id'] == newHunt[0]['game_id']):
            return
        newHunt = newHunt[0]
        row = HuntListItem(newHunt,parent=self)
        widget = HuntWidget(newHunt['game_id'],parent=self)
        row.setWidget(widget)
        self.main.layout.insertWidget(1,row)
        self.main.layout.insertWidget(2,widget)

        self.toggle(widget)
        self.toggle(widget)
        self.toggle(widget)
        self.setMinimumWidth(self.sizeHint().width())

    def initHuntsList(self):
        self.huntsArray = get_n_hunts(50)
        if len(self.huntsArray) == 0:
            return
        self.setHeader()
        for i in range(len(self.huntsArray)):
            row = HuntListItem(self.huntsArray[i],parent=self)
            self.main.layout.addWidget(row)
            widget = HuntWidget(self.huntsArray[i]['game_id'])
            row.setWidget(widget)
            self.main.layout.addWidget(widget)
            if i == 0:
                self.currentWidget = widget
        self.main.layout.addStretch()
        self.toggle(self.currentWidget)

    def toggle(self,widget):
        if self.currentWidget == widget:
            self.currentWidget.toggle()
            return
        if self.currentWidget != None:
            self.currentWidget.setVisible(False)
            self.currentWidget = widget
            self.currentWidget.toggle()
            return
        self.currentWidget = widget
        self.currentWidget.toggle()


    def setHeader(self):
        print('setheader')
        self.clearLayout()
        header = QWidget()
        header.layout = QHBoxLayout()
        header.layout.setSpacing(0)
        header.layout.setContentsMargins(0,0,0,0)
        header.setLayout(header.layout)
        for i in range(len(cols)):
            label = cols[i].split("_")
            w = QLabel(' '.join([l.capitalize() for l in label]))
            w.setSizePolicy(QSizePolicy.Policy.Minimum,QSizePolicy.Policy.Minimum)
            w.setObjectName("HuntListHeaderItem")
            header.layout.addWidget(w,stretch=2 if cols[i] == 'timestamp' else 1)
        header.setFixedHeight(36)
        header.setObjectName("HuntListHeader")
        self.main.layout.addWidget(header)
    
    def clearLayout(self):
        for i in reversed(range(self.main.layout.count())): 
            w = self.main.layout.itemAt(i).widget()
            if w != None:
                w.setParent(None)


class HuntListItem(QWidget):
    def __init__(self, data, parent: QWidget | None = None):
        super().__init__(parent)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_StyledBackground)      
        self.layout = QHBoxLayout()
        self.setLayout(self.layout)
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0,0,0,0)
        self.parent = parent

        self.id = data['game_id']

        for j in range(len(cols)):
            w = QLabel()
            if cols[j] == 'extracted' :
                if(data[cols[j]] == 'true'):
                    i = get_icon('assets/icons/Hunt Loss Icon.png')
                else:
                    i = get_icon('assets/icons/Hunt Extract Icon.png')
                w = QWidget()
                w.layout = QHBoxLayout()
                w.layout.setContentsMargins(0,0,0,0)
                w.setLayout(w.layout)
                w.layout.addWidget(i)
            elif(cols[j] == 'timestamp'):
                w.setText(str(datetime.fromtimestamp(data[cols[j]]).strftime("%H:%M | %b %d")))
            elif(cols[j] == 'assists' and data[cols[j]] is None):
                w.setText('0')
            else:
                w.setText(str(data[cols[j]]))
            self.layout.addWidget(w,stretch=2 if cols[j] == 'timestamp' else 1)
        self.widget = None

        self.setFixedHeight(36)

    def setWidget(self,w):
        self.widget = w

    def mousePressEvent(self, a0: QtGui.QMouseEvent) -> None:
        self.parent.toggle(self.widget)
        #self.widget.toggle()
        return super().mousePressEvent(a0)