from PyQt6.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QApplication, QPushButton
from PIL import Image
import os
import json
from PyQt6.QtCore import QEvent, Qt, QSize
from PyQt6.QtGui import QMouseEvent, QColor, QPen, QBrush, QPixmap
from MapWindow.Grid import Grid
from MapWindow.Marker import Border, Label, Marker
from MapWindow.Ruler import Ruler
from resources import resource_path

maps = {
    "DeSalle" : resource_path("assets/maps/desalle"),
    "Lawson Delta" : resource_path("assets/maps/lawson"),
    "Stillwater Bayou" : resource_path("assets/maps/stillwater")
}

coords = {
    "DeSalle":[],
    "Lawson Delta":[],
    "Stillwater Bayou":[]
}
spawn_points_file = resource_path("assets/json/spawn_points.json")
beetle_spawns_file = resource_path("assets/json/beetle_spawns.json")
compounds_file = resource_path("assets/json/compound_coordinates.json")

grid_size = 8

class MapView(QGraphicsView):
    def __init__(self) -> None:
        super().__init__()
        self.scene = None
        self.current = list(maps.keys())[0]

        self.zoom = 1
        self.factor = 1
        self.rulerMode = False
        self.mapScale = 0.5

        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.setMap(self.current)

    def initScene(self,w,h):
        self.scene = QGraphicsScene(0,0,w,h)
        #self.setBaseSize(w,h)
        self.setFixedSize(int(w),int(h))
        self.setScene(self.scene)
        self.scene.installEventFilter(self)
    
    def setMap(self,map):
        self.current = map
        self.beetles = []
        self.spawns = []
        if self.scene:
            self.scene.clear()
        size = 0
        for f in os.listdir(maps[self.current]):
            if ".png" in f:
                x = int(f.split('-')[1].split('.')[0])
                y = int(f.split('-')[2].split('.')[0])
                path = os.path.join(maps[self.current],f)
                if size == 0:
                    size = Image.open(path).size[0]
                    size = size*self.mapScale
                if self.scene == None:
                    self.initScene(4*size,4*size)
                tile = QGraphicsPixmapItem(QPixmap(path))
                tile.setZValue(0)
                tile.setScale(self.mapScale)
                self.scene.addItem(tile)
                tile.setPos(x*size,y*size)

        self.show()
        self.update()
        self.InitSpawnPoints(self.current)
        self.InitBeetleSpawns(self.current)
        self.InitCompoundLabels(self.current)
        self.InitCompoundEdges(self.current)
        self.grid = Grid(int(self.size().width()),grid_size)
        self.scene.addItem(self.grid)
        self.ruler = Ruler()
        self.scene.addItem(self.ruler)
        if self.rulerMode:
            self.toggleRuler()

    def ToggleSpawnPoints(self):
        for spawn in self.spawns:
            spawn.toggle()
        self.show()
        self.update()

    def ToggleBeetles(self):
        for beetle in self.beetles:
            beetle.toggle()
        self.show()
        self.update()

    def ToggleCompoundNames(self):
        for name in self.compound_labels:
            name.toggle()
        self.show()
        self.update()

    def ToggleCompoundBorders(self):
        for border in self.compound_borders:
            border.toggle()
        self.show()
        self.update()

    def toggleRuler(self):
        self.defaultZoom()
        self.rulerMode = not self.rulerMode
        if self.rulerMode:
            self.window().statusBar.showMessage("Click a starting point")
            self.parent().buttons.ruler.setStyleSheet("QPushButton{border:2px solid #99ffff00;}")
        else:
            self.parent().buttons.ruler.setStyleSheet("QPushButton{border:1px solid black;}")
            self.setMap(self.current)
            self.ruler.clear()
            self.scene.update()

    def InitSpawnPoints(self,map):
        #print('init.spawns')
        with open(spawn_points_file,'r') as f:
            self.spawn_points_json = json.loads(f.read())
        brush = QColor("#ffffff00")
        pen = QColor("#000000")
        pts = self.spawn_points_json[map]
        self.spawns = []
        for pt in pts:
            x = pt['x']/100 * self.size().width()
            y = pt['y']/100 * self.size().height()
            self.spawns.append(
                Marker(x=x,y=y,brushColor=brush,penColor=pen)
            )
        for spawn in self.spawns:
            self.scene.addItem(spawn)
            #self.scene.addItem(spawn.textBox)

    def InitBeetleSpawns(self,map):
        #print('init.beetles')
        with open(beetle_spawns_file,'r') as f:
            self.beetle_spawns_json = json.loads(f.read())
        pbrush = QBrush(QColor("#44ff0000"))
        rbrush = QBrush(QColor("#440000ff"))
        ppen = QPen(QColor("#ff0000"))
        ppen.setWidth(4)
        rpen = QPen(QColor("#0000ff"))
        rpen.setWidth(4)
        #pen = QColor("#ffffff")
        lst = self.beetle_spawns_json[map]
        self.beetles = []
        for type in lst:
            for pt in lst[type]:
                x = pt['x']/100 * self.size().width()
                y = pt['y']/100 * self.size().height()
                if type == "Permanent":
                    dot = Marker(x=x,y=y,brushColor=pbrush,penColor=ppen)
                else:
                    dot = Marker(x=x,y=y,brushColor=rbrush,penColor=rpen)
                self.beetles.append(dot)
        for beetle in self.beetles:
            self.scene.addItem(beetle)
            #self.scene.addItem(beetle.textBox)
        self.update()

    def InitCompoundEdges(self,map):
        #print('init.edges')
        with open(compounds_file,'r') as f:
            self.compound_verts_json = json.loads(f.read())['compounds']
        self.compound_borders = []
        compounds = self.compound_verts_json[map]
        compounds = self.compound_verts_json[map]
        for compound in compounds:
            pts = compounds[compound]
            edgePts = []
            for pt in pts['corners']:
                if 'center' not in pt:
                    pt['x'] = pt['x']/100*self.size().width()
                    pt['y'] = pt['y']/100*self.size().height()
                    edgePts.append(pt)
            self.compound_borders.append(Border(edgePts))
        for border in self.compound_borders:
            self.scene.addItem(border)

    def InitCompoundLabels(self,map):
        #print('init.labels')
        with open(compounds_file,'r') as f:
            self.compound_names_json = json.loads(f.read())['compounds']
        compounds = self.compound_names_json[map]
        self.compound_labels = []
        for compound in compounds:
            for pt in compounds[compound]['corners']:
                if 'center' in pt:
                    center = pt['center']
                    x = center['x']/100*self.size().width()
                    y = center['y']/100*self.size().height()
                    if x > 0 and y > 0:
                        label = Label(compound,x=x,y=y)
                        self.compound_labels.append(label)
        for label in self.compound_labels:
            self.scene.addItem(label)
        self.update()

    def eventFilter(self, obj,event):
        if obj == self.scene:
            if event.type() == QEvent.Type.GraphicsSceneWheel and not self.rulerMode:
                if event.delta() > 0:
                    if self.zoom < 4:
                        self.factor = 1.25
                        self.zoom *= self.factor
                        self.scale(self.factor,self.factor)
                else:
                    if self.zoom > 0.8:
                        self.factor = 0.8
                        self.zoom *= self.factor
                        self.scale(self.factor,self.factor)

        elif type(obj) == Marker:
            print("event",obj)
        return True
    
    def defaultZoom(self):
        while self.zoom > 1:
            self.factor = 0.8
            self.zoom *= self.factor
            self.scale(self.factor,self.factor)
        while self.zoom < 1:
            self.factor = 1.25
            self.zoom *= self.factor
            self.scale(self.factor,self.factor)

    def enterEvent(self, event) -> None:
        if not self.rulerMode:
            QApplication.setOverrideCursor(Qt.CursorShape.ArrowCursor)
        else:
            QApplication.setOverrideCursor(Qt.CursorShape.CrossCursor)
        return super().enterEvent(event)

    def leaveEvent(self, a0) -> None:
        QApplication.setOverrideCursor(Qt.CursorShape.ArrowCursor)
        return super().leaveEvent(a0)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if self.rulerMode:
            if self.ruler.line.p1().x() < 0 or self.ruler.line.p1().y() < 0:
                x = event.pos().x() / self.zoom
                y = event.pos().y() / self.zoom
                self.ruler.setStart(x,y)
            elif not self.ruler.set:
                self.ruler.set = True
                x = event.pos().x() / self.zoom
                y = event.pos().y() / self.zoom
                self.ruler.moveEnd(x,y)
                self.window().statusBar.showMessage("%d meters" % (self.ruler.length() / self.mapScale))
            elif self.ruler.set:
                self.ruler.set = False
                self.ruler.setStart(-1,-1)
                self.window().statusBar.showMessage("Click a starting point")

        items = self.items(event.pos())
        for item in items:
            if type(item) == Marker:
                pass
        self.update()
        return super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if self.rulerMode:
            if not self.ruler.set and (self.ruler.line.p1().x() > 0 or self.ruler.line.p1().y() > 0):
                x = event.pos().x() / self.zoom
                y = event.pos().y() / self.zoom
                self.ruler.moveEnd(x,y)
                self.update()
                self.scene.update()
                self.window().statusBar.showMessage("%d meters | click again to anchor" % (self.ruler.length() / self.mapScale))
        else:
            x = event.pos().x() / self.mapScale
            y = event.pos().y() / self.mapScale
            self.window().statusBar.showMessage("(%d %d)" % (x,y))
        return super().mouseMoveEvent(event)