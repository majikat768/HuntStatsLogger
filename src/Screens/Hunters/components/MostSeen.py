from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTableWidget, QHeaderView, QSizePolicy, QTableWidgetItem, QAbstractItemView
from DbHandler import execute_query
from resources import settings
from Screens.Hunters.components.Table import Table

class MostSeen(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.layout.setContentsMargins(0,0,0,0)
        label = QLabel("Most Seen")
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
            "select blood_line_name, max(mmr), count(profileid)\
                from 'hunters' where profileid != '%s'\
                group by profileid\
                order by count(profileid) desc\
                limit 20" % settings.value("profileid","0")
        )

        self.huntersTable.setData(hunters,["Hunter","MMR","Seen"])
        self.huntersTable.horizontalHeader().setSectionResizeMode(0,QHeaderView.ResizeMode.Stretch)
        self.huntersTable.horizontalHeader().setSectionResizeMode(1,QHeaderView.ResizeMode.Fixed)
        self.huntersTable.horizontalHeader().setSectionResizeMode(2,QHeaderView.ResizeMode.Fixed)
        self.huntersTable.resizeColumnsToContents()