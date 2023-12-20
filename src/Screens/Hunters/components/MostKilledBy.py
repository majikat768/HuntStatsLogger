from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTableWidget, QHeaderView, QSizePolicy, QTableWidgetItem, QAbstractItemView
from DbHandler import execute_query
from Screens.Hunters.components.Table import Table

class MostKilledBy(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.layout.setContentsMargins(0,0,0,0)

        label = QLabel("Most Killed By")
        label.setSizePolicy(
            QSizePolicy.Policy.Fixed,
            QSizePolicy.Policy.Fixed,
        )
        self.layout.addWidget(label)
        self.huntersTable = Table()
        #self.huntersTable.horizontalHeader().hide()

        self.setSizePolicy(QSizePolicy.Policy.Expanding,QSizePolicy.Policy.Expanding)
        self.layout.addWidget(self.huntersTable)
        self.layout.addStretch()

        self.update()


    def update(self):
        hunters = execute_query(
            "select h.blood_line_name,max(h.mmr),\
                sum(h.killedbyme+h.downedbyme) || '/' || sum(h.killedme+h.downedme)\
                from 'hunters' h\
                where h.killedme > 0 or h.downedme > 0\
                group by h.profileid order by sum(h.killedme+h.downedme) desc limit 20"
        )

        self.huntersTable.setData(hunters,["Hunter","MMR","K/D"])
        self.huntersTable.horizontalHeader().setSectionResizeMode(0,QHeaderView.ResizeMode.Stretch)
        self.huntersTable.horizontalHeader().setSectionResizeMode(1,QHeaderView.ResizeMode.Fixed)
        self.huntersTable.horizontalHeader().setSectionResizeMode(2,QHeaderView.ResizeMode.Fixed)
        self.huntersTable.resizeColumnsToContents()