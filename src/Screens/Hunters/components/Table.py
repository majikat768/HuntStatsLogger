from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTableWidget, QHeaderView, QSizePolicy, QTableWidgetItem, QAbstractItemView
from Screens.Hunters.components.HunterWindow import HunterWindow
from DbHandler import execute_query
from resources import settings

class Table(QTableWidget):
    def __init__(self,parent = None):
        super().__init__(parent)

        self.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
        self.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)

        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

        #self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.setSizePolicy(QSizePolicy.Policy.Expanding,QSizePolicy.Policy.Expanding)
        self.setContentsMargins(0,0,0,0)
        self.cellClicked.connect(self.showHunterData)
        self.data = []

    def setData(self,data, colNames):
        self.clear()
        self.setColumnCount(len(colNames))
        self.setRowCount(len(data))
        self.setHorizontalHeaderLabels(colNames)
        for i in range(len(data)):
            self.data.append({})
            for j in range(len(colNames)):
                self.data[i][colNames[j]] = data[i][j]
                self.setItem(i,j,QTableWidgetItem(str(data[i][j])))
            self.data[i]["id"] = data[i][len(colNames)]
            self.setRowHeight(i,32)
        self.setFixedHeight(33*len(data)+self.horizontalHeader().height())

    def showHunterData(self,row,col):
        win = HunterWindow(self.data[row]['id'],parent=self)
        win.show()
