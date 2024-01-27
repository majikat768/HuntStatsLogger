from PyQt6.QtWidgets import QWidget, QGridLayout, QVBoxLayout, QSizePolicy,QSpacerItem, QGroupBox
from DbHandler import get_bounty_data, get_entries
from resources import tab
from Widgets.Label import Label

class BountiesWidget(QGroupBox):
    def __init__(self, game_id, parent: QWidget | None = None):
        super().__init__(parent)
        self.game_id = game_id

        self.data = {}
        self.setTitle("Bounties")
        self.setObjectName("BountiesWidget")
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.setSizePolicy(QSizePolicy.Policy.Expanding,QSizePolicy.Policy.Minimum)

        self.layout.setContentsMargins(0,6,0,0)
        self.layout.setSpacing(4)

        self.main = QWidget()
        self.main.layout = QVBoxLayout()
        self.main.layout.setContentsMargins(1,1,1,1)
        self.main.setLayout(self.main.layout)

        self.layout.addWidget(self.main)

    def init(self):
        if len(self.data) == 0:
            self.data['hunt'] = get_bounty_data(self.game_id)
            self.widgets = {}
            self.entries = get_entries(self.game_id)
            bounties = {}
            monsters_killed = {}
            tokens_extracted = 0
            if(self.data["hunt"]["IsQuickPlay"] == "true"):
                self.setTitle("Soul Survivor")
                bounties['rifts_closed'] = 0
            else:
                self.setTitle("Bounty Hunt")
                for boss in ['butcher','spider','assassin','scrapbeak']:
                    if self.data['hunt'][boss] == 'true':
                        bounties[boss] = {'clues':0,'killed':0,'banished':0,'extracted':0}
            for entry in self.entries:
                cat = entry['category']
                if "killed_" in cat:
                    boss = cat.split("_")[2]
                    if boss in bounties:
                        bounties[boss]["killed"] = 1
                elif "banished" in cat:
                    boss = cat.split("_")[2]
                    if boss in bounties:
                        bounties[boss]["banished"] = 1
                elif "clues_found" in cat:
                    boss = entry['descriptorName'].split(" ")[1]
                    if boss in bounties:
                        bounties[boss]["clues"] += 1
                elif "_extract_" in cat and "_token" in cat:
                    tokens_extracted = get_n_tokens(entry['descriptorName'])
                elif "wellsprings_found" in cat:
                    bounties['rifts_closed'] += 1
                elif 'monsters_killed' in cat:
                    monster = entry['descriptorName'].split(' ')[1]
                    if monster not in monsters_killed:
                        monsters_killed[monster] = 0
                    monsters_killed[monster] += entry['amount']

                self.data['tokens_extracted'] = tokens_extracted
                self.data['bounties'] = bounties
                self.data['monsters_killed'] = monsters_killed
            if self.data['hunt']['IsQuickPlay'] == 'false':
                for bounty in bounties:
                    w = QWidget()
                    w.layout = QVBoxLayout()
                    w.setLayout(w.layout)
                    w.layout.setSpacing(2)
                    w.layout.addWidget(Label(bounty.capitalize()))
                    w.layout.addWidget(Label("%sFound %d clues." % (tab(), bounties[bounty]['clues'])))
                    if bounties[bounty]['killed']:
                        w.layout.addWidget(Label("%sKilled." % tab()))
                    if bounties[bounty]['banished']:
                        w.layout.addWidget(Label("%sBanished." % tab()))
                    self.main.layout.addWidget(w)
                    self.widgets[boss] = w
            else:
                w = QWidget()
                w.layout = QVBoxLayout()
                w.setLayout(w.layout)
                w.layout.setSpacing(0)
                w.layout.addWidget(Label("Closed %d rifts." % bounties['rifts_closed']))
                self.main.layout.addWidget(w)


            #self.layout.addStretch()

def get_n_tokens(entry):
    return 1 if 'one token' in entry else 2 if 'two tokens' in entry else 3 if 'three tokens' in entry else 4 if 'four tokens' in entry else 0