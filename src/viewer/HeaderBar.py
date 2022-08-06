from PyQt6.QtWidgets import QGroupBox,QHBoxLayout,QVBoxLayout,QWidget,QLabel,QGridLayout,QComboBox,QSpacerItem,QSizePolicy
from PyQt6.QtCore import Qt,QEvent
from PyQt6.QtGui import QPixmap,QFont
from resources import *
from util.TextArea import TextArea
from viewer import DbHandler

class HeaderBar(QGroupBox):
    def __init__(self,parent):
        super().__init__(parent)
        self.layout = QHBoxLayout()
        self.setLayout(self.layout)
        self.setSizePolicy(QSizePolicy.Policy.MinimumExpanding,QSizePolicy.Policy.Fixed)

        self.setObjectName("HeaderBar")

        self.initUI()
        self.setFixedHeight(self.sizeHint().height())

    def initUI(self):
        self.hunterBox = self.initHunterBox()
        self.kdaBox = self.initKdaBox()
        self.mmrBox = self.initMmrBox()
        self.layout.addWidget(self.hunterBox,Qt.AlignmentFlag.AlignLeft)
        self.layout.addStretch()
        self.layout.addWidget(self.kdaBox,Qt.AlignmentFlag.AlignHCenter)
        self.layout.addStretch()
        self.layout.addWidget(self.mmrBox)
        self.mmrBox.setAlignment(Qt.AlignmentFlag.AlignRight)

    def update(self):
        self.updateHunterBox()
        self.updateMmrBox()
        self.updateKdaBox(self.kdaBox.get('gameType').text())

    def updateMmrBox(self):
        mmr = DbHandler.GetMmr(settings.value("profileid",-1))
        bestMmr = DbHandler.GetMaxMmr(settings.value("profileid",-1))
        self.mmrBox.get('mmr').setText("MMR: %d" % mmr)
        self.mmrBox.get('best').setText("Best: %d" % bestMmr)
        starsIcon = self.mmrBox.get('stars')
        starsIcon.setPixmap(star_pixmap(mmr_to_stars(mmr)))

    def updateHunterBox(self):
        self.hunterBox.get('name').setText(settings.value("steam_name","")) 

        lvl = DbHandler.execute_query("select HunterLevel from 'game' where timestamp is (select max(timestamp) from 'game')")
        lvl = 0 if lvl is None or len(lvl) == 0 else lvl[0][0]
        lvl = 0 if lvl is None else lvl
        self.hunterBox.get('level').setText("Level %d" % lvl)
        self.hunterBox.get('hunts').setText("Hunts: %d" % DbHandler.getHuntCount())

    def initHunterBox(self):
        area = TextArea()
        area.addLine('name',settings.value("steam_name","hunter"))
        area.get('name').setObjectName("HunterTitle")
        area.addLine('hunts',"Hunts: 0")
        area.addLine('level',"Level 0")

        return area

    def initMmrBox(self):
        area = TextArea()
        starsIcon = QLabel()
        starsIcon.setPixmap(QPixmap(os.path.join(resource_path('assets/icons/'),'_6star.png')))

        area.addLabel('stars',starsIcon,alignment=Qt.AlignmentFlag.AlignRight)
        area.addLine('mmr',"MMR: 0",alignment=Qt.AlignmentFlag.AlignRight)
        area.addLine('best',"Best: 0",alignment=Qt.AlignmentFlag.AlignRight)
        area.addStretch()
        return area

    def initKdaBox(self):
        area = TextArea(alignment=Qt.AlignmentFlag.AlignCenter)

        area.addLine('kda','1.000',Qt.AlignmentFlag.AlignCenter)
        area.get('kda').setObjectName("kdaTitle")
        area.addLine('values','0k 0d 0a',Qt.AlignmentFlag.AlignCenter)
        area.addLine('gameType','All Hunts',Qt.AlignmentFlag.AlignCenter)
        area.get('gameType').setObjectName('link')
        area.get('gameType').installEventFilter(self)
        area.addStretch()

        return area

    def eventFilter(self, obj, e):
        if e.type() == QEvent.Type.MouseButtonPress:
            obj.setText(
                gameTypes[
                    (gameTypes.index(obj.text())+1) % len(gameTypes)
                    ]
            )
            self.updateKdaBox(obj.text())
        return super().eventFilter(obj, e)

    def updateKdaBox(self,gameType):
        print(gameType)
        kills = DbHandler.execute_query(
            "select downedbyme + killedbyme,timestamp from 'hunter' where (downedbyme > 0 or killedbyme > 0)"
        )
        deaths = DbHandler.execute_query(
            "select downedme + killedme,timestamp from 'hunter' where (downedme > 0 or killedme > 0)"
        )
        assists = DbHandler.execute_query(
            "select amount,timestamp from 'entry' where category is 'accolade_players_killed_assist'"
        )
        if kills is None or deaths is None or assists is None:  return
        if gameType != "All Hunts":
            include = [i[0] for i in DbHandler.execute_query("select timestamp from 'game' where MissionBagIsQuickPlay is %d" % (0 if gameType == "Quick Play" else 1)) ]
            kills = [k for k in kills if k[1] in include]
            deaths = [d for d in deaths if d[1] in include]
            assists = [a for a in assists if a[1] in include]
        

        kills = sum([k[0] for k in kills])
        deaths = sum([d[0] for d in deaths])
        assists = sum([a[0] for a in assists])

        if int(deaths) == 0:
            kda = (kills + assists)
        else:
            kda = (kills + assists) / deaths

        self.kdaBox.get('kda').setText('%s' % '{:.3f}'.format(kda))
        self.kdaBox.get('values').setText('%sk %sd %sa' % (kills,deaths,assists))