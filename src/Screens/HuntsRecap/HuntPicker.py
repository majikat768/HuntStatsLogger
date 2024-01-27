import typing
from PyQt6 import QtCore, QtGui
from PyQt6.QtWidgets import QComboBox, QWidget, QTableWidget, QTableWidgetItem, QHBoxLayout, QLabel, QSizePolicy, QHeaderView, QStyledItemDelegate
from PyQt6.QtGui import QPixmap, QIcon, QMouseEvent
from PyQt6.QtCore import Qt, QSize, QRect
from DbHandler import get_n_hunts
from resources import resource_path, tab
from datetime import datetime

cols = ["extracted","game_type","timestamp","kills","deaths","assists","team_kills","team_deaths"]

class HuntPicker(QWidget):
    def __init__(self, target, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Policy.Expanding,QSizePolicy.Policy.Fixed)
        self.setMouseTracking(True)
        self.target = target

        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_StyledBackground)      
        self.button = QTableWidget()
        self.button.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
        self.button.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)

        self.huntList = []

        self.button.setColumnCount(6)
        self.button.setRowCount(1)
        self.button.horizontalHeader().hide()
        self.button.verticalHeader().hide()
        self.setFixedHeight(36)
        arrow = QLabel()
        arrow.setPixmap(QPixmap(resource_path("assets/icons/huntArrowDown.png")))
        arrow.setObjectName("down-arrow")
        #arrow = QTableWidgetItem(QIcon(resource_path("assets/icons/huntArrowDown.png")),'')
        #self.button.setItem(0,self.button.columnCount()-1,arrow)
        self.button.setIconSize(QSize(32,32))
        self.button.setRowHeight(0,32)
        self.button.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.button.setSizePolicy(QSizePolicy.Policy.Expanding,QSizePolicy.Policy.Fixed)

        self.layout = QHBoxLayout()
        self.setLayout(self.layout)
        self.layout.addWidget(self.button,stretch=1)
        self.layout.addWidget(arrow)
        self.layout.setContentsMargins(2,2,2,2)
        self.button.mousePressEvent = self.mousePressEvent

    def getLatestHunt(self):
        self.table.getLatestHunt()

    def init(self):
        self.table = HuntsTable()
        self.table.initialize_table()
        self.table.setParent(self)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        self.table.focusOutEvent = self.closeTable
        self.table.itemEntered = (lambda x : print(x,1))

    def setTarget(self,parent):
        self.target = parent

    def show_hunt(self,id):
        self.target.show_hunt(id)
        print(id)

    def closeTable(self, a0):
        self.table.hide()

    def mousePressEvent(self, a0) -> None:
        self.table.show(self)

        return super().mousePressEvent(a0)

class HuntsTable(QTableWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.verticalHeader().hide()
        self.header = None
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.SubWindow
        )
        self.setSizePolicy(QSizePolicy.Policy.Expanding,QSizePolicy.Policy.Fixed)
        self.huntList = []
        self.setMouseTracking(True)
        self.hover_row = None
        self.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
        self.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)

    def getLatestHunt(self):
        if(len(self.huntList) == 0):
            self.initialize_table()
            return
        newHunt = get_n_hunts(1)
        if len(newHunt) == 0:
            return
        if(len(self.huntList) > 0 and self.huntList[0]['game_id'] == newHunt[0]['game_id']):
            return
        newHunt = newHunt[0]
        self.insertRow(0)
        self.huntList = [newHunt] + self.huntList
        for j in range(len(cols)):
            if cols[j] == 'extracted':
                pixmap = QPixmap(
                    resource_path("assets/icons/Hunt %s Icon.png" % ("Loss" if newHunt['extracted'] == 'true' else 'Extract')))
                item = HuntTableItem(icon=QIcon(pixmap.scaled(36,36)),text='') 
                self.setItem(0,j,item)
            elif cols[j] == 'game_type':
                item = HuntTableItem(text="Bounty Hunt" if newHunt['game_type'] != 'true' else "Soul Survivor")
                self.setItem(0,j,item)
            elif cols[j] == 'timestamp':
                ts = str(datetime.fromtimestamp(newHunt[cols[j]]).strftime("%H:%M | %b %d"))
                self.setItem(0,j,HuntTableItem(text=ts))
            else:
                self.setItem(0,j,HuntTableItem(text=str(newHunt[cols[j]]) if newHunt[cols[j]] is not None else '0'))
            self.item(0,j).setParent(self)
            self.item(0,j).setForeground(QtGui.QColor("#cccccc"))
        self.set_title(0)
        


    def setParent(self,widget):
        self.header = widget
        self.set_title(0)

    def focusOutEvent(self, e) -> None:
        self.hide()
        return super().focusOutEvent(e)

    def set_title(self,row):
        hunt = self.huntList[row]
        self.header.button.setItem(0,0,QTableWidgetItem(
            QIcon(resource_path("assets/icons/Hunt %s Icon.png" % ("Loss" if hunt['extracted'] == 'true' else 'Extract'))),
            "Bounty Hunt" if hunt['game_type'] != 'true' else "Soul Survivor")
        )
        self.header.button.item(0,0).setForeground(QtGui.QColor("#cccccc"))
        self.header.button.setItem(0,1,QTableWidgetItem(
            str(datetime.fromtimestamp(hunt['timestamp']).strftime("%H:%M | %b %d"))
        ))
        self.header.button.item(0,1).setForeground(QtGui.QColor("#cccccc"))
        self.header.button.setItem(0,2,QTableWidgetItem(
            "K/D/A:%s%d/%d/%d" % (tab(), hunt['kills'], hunt['deaths'],hunt['assists'] if hunt['assists'] is not None else 0)
        ))
        self.header.button.item(0,2).setForeground(QtGui.QColor("#cccccc"))
        self.header.button.setItem(0,3,QTableWidgetItem(
            "Team K/D:%s%d/%d" % (tab(), hunt['team_kills'], hunt['team_deaths'])
        ))
        self.header.button.item(0,3).setForeground(QtGui.QColor("#cccccc"))
        self.header.button.resizeColumnsToContents()
        self.header.show_hunt(self.huntList[row]['game_id'])

    def mousePressEvent(self, e: QMouseEvent) -> None:
        self.set_title(self.hover_row)
        self.hide()
        return super().mousePressEvent(e)

    def show(self,parent) -> None:
        self.setMouseTracking(True)
        self.setFocus()
        self.activateWindow()
        self.raise_()
        pos = parent.mapToGlobal(parent.pos())
        pos.setY(pos.y() - windowFrameSize(parent.window()).height() + self.header.height())
        self.setGeometry(pos.x(),pos.y(),int(parent.width()*1.0),self.height())
        return super().show()

    def mouseMoveEvent(self, e: QMouseEvent) -> None:
        row = self.indexAt(e.pos()).row()
        if self.hover_row != row:
            if self.hover_row != None:
                for i in range(len(cols)):
                    self.item(self.hover_row,i).setBackground(QtGui.QColor("#00000000"))
            self.hover_row = row
            for i in range(len(cols)):
                self.item(row,i).setBackground(QtGui.QColor("#666666cc"))
        return super().mouseMoveEvent(e)

    def leaveEvent(self, a0) -> None:
        self.hover_row = None
        return super().leaveEvent(a0)

    def initialize_table(self):
        self.huntList = get_n_hunts(50)
        if len(self.huntList) == 0:
            return
        self.setRowCount(len(self.huntList))
        self.setColumnCount(len(cols))
        
        self.setHorizontalHeaderLabels([' '.join([x.capitalize() for x in c.split("_")]) for c in cols])
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.setIconSize(QSize(36,36))

        for i in range(len(self.huntList)):
            data = self.huntList[i]
            for j in range(len(cols)):
                if cols[j] == 'extracted':
                    pixmap = QPixmap(
                        resource_path("assets/icons/Hunt %s Icon.png" % ("Loss" if data['extracted'] == 'true' else 'Extract')))
                    item = HuntTableItem(icon=QIcon(pixmap.scaled(36,36)),text='') 
                    self.setItem(i,j,item)
                elif cols[j] == 'game_type':
                    item = HuntTableItem(text="Bounty Hunt" if data['game_type'] != 'true' else "Soul Survivor")
                    self.setItem(i,j,item)
                elif cols[j] == 'timestamp':
                    ts = str(datetime.fromtimestamp(data[cols[j]]).strftime("%H:%M | %b %d"))
                    self.setItem(i,j,HuntTableItem(text=ts))
                else:
                    self.setItem(i,j,HuntTableItem(text=str(data[cols[j]]) if data[cols[j]] is not None else '0'))
                self.item(i,j).setParent(self)
                self.item(i,j).setForeground(QtGui.QColor("#cccccc"))
            
        self.resizeColumnsToContents()

class HuntTableItem(QTableWidgetItem):
    def __init__(self,parent = None, icon = None, text = ''):
        if(icon == None):
            super().__init__(text)
        else:
            super().__init__(icon,text)
        self.parent = parent if parent is not None else None
    def setParent(self,widget):
        self.parent = widget

def windowFrameSize(window):
    return QSize(
        window.frameSize().width() - window.size().width(),
        window.frameSize().height() - window.size().height(),
    )

class ItemDelegate(QStyledItemDelegate):
    def __init__(self, parent = None) -> None:
        super().__init__(parent)

    def paint(self, painter, option, index) -> None:
        return super().paint(painter, option, index)
