from PyQt6.QtWidgets import QWidget, QGridLayout, QVBoxLayout, QLabel,QSizePolicy,QSpacerItem, QGroupBox
from PyQt6.QtCore import Qt
from DbHandler import execute_query
from resources import tab

class MonstersWidget(QGroupBox):
    def __init__(self, game_id, parent: QWidget | None = None):
        super().__init__(parent)
        self.game_id = game_id

        self.data = {}
        self.setTitle("Monsters")
        self.setObjectName("MonstersWidget")
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.layout.setContentsMargins(0,6,0,0)
        self.layout.setSpacing(2)

        self.main = QWidget()
        self.main.layout = QGridLayout()
        self.main.layout.setContentsMargins(8,8,8,8)
        self.main.setLayout(self.main.layout)

        self.layout.addWidget(self.main)
    
    def init(self):
        if len(self.data) == 0:
            monster_entries = execute_query("select descriptorName, amount from 'entries'\
                                            where game_id = ? and (category like 'accolade_monsters_killed' or descriptorName like 'kill horse')",self.game_id)
            monsters = []
            for i in range(len(monster_entries)):
                entry = monster_entries[i]
                monster = ' '.join(entry[0].split(' ')[1:])
                amount = entry[1]
                self.data['monster'] = amount
                monsters.append({"amount":amount,"monster":sanitizeMonsterNames(monster)})
                #self.main.layout.addWidget(QLabel(sanitizeMonsterNames(monster)),i,1)
                #self.main.layout.addWidget(QLabel(str(amount)),i,2)
            monsters = list(reversed(sorted(monsters,key=lambda x : x['amount'])))
            for i in range(len(monsters)):
                monster = monsters[i]
                self.main.layout.addWidget(QLabel(monster['monster']),i,1)
                self.main.layout.addWidget(QLabel(str(monster['amount'])),i,2,alignment=Qt.AlignmentFlag.AlignRight)
            

def sanitizeMonsterNames(monster):
    if monster == 'waterdevil':
        return 'Water Devil'
    else:
        return monster.capitalize()
