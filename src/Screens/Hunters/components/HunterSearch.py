from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLineEdit, QPushButton
from Screens.Hunters.components.HunterWindow import HunterWindow
from DbHandler import execute_query
from Widgets.Label import Label

class HunterSearch(QWidget):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.searchbar = QWidget()
        self.searchbar.layout = QHBoxLayout()
        self.searchbar.setLayout(self.searchbar.layout)

        self.input = QLineEdit()
        self.input.setPlaceholderText("Enter Hunter Name")
        self.searchBtn = QPushButton("Search")
        self.clearBtn = QPushButton("Clear")

        self.searchBtn.clicked.connect(lambda : self.search(self.input.text()))
        self.clearBtn.clicked.connect(self.clearResults)
        self.clearBtn.clicked.connect(lambda : self.input.setText(""))
        self.searchbar.layout.addWidget(self.input)
        self.searchbar.layout.addWidget(self.searchBtn)
        self.searchbar.layout.addWidget(self.clearBtn)

        self.layout.addWidget(self.searchbar)

        self.results = QWidget()
        self.results.layout = QVBoxLayout()
        self.results.setLayout(self.results.layout)

        self.layout.addWidget(self.results)

    def search(self,text):
        if len(text) == 0:
            return
        res = execute_query("select h.profileid,h.blood_line_name from 'hunters' h where h.blood_line_name like '%%%s%%' group by h.blood_line_name limit 30" % text)
        if len(res) > 0:
            self.updateResults([{'id':r[0],'blood_line_name':r[1]} for r in res])

    def updateResults(self,res):
        self.clearResults()
        for r in res:
            btn = QPushButton(r['blood_line_name'])
            btn.id = r['id']
            btn.clicked.connect(lambda x, txt = r['id']: self.showHunter(txt))
            self.results.layout.addWidget(btn)

    def showHunter(self,pid):
        win = HunterWindow(pid,parent=self)
        win.show()

    def clearResults(self):
        for i in reversed(range(self.results.layout.count())): 
            self.results.layout.itemAt(i).widget().setParent(None)