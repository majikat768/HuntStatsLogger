from random import random
import sys
from PyQt6.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QApplication
from PIL import Image
import os
import json
from PyQt6.QtCore import QEvent, Qt
from PyQt6.QtGui import QMouseEvent, QColor, QPixmap
from MapWindow.Marker import Border, Label, Marker
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

class MapView(QGraphicsView):
    def __init__(self) -> None:
        super().__init__()
        self.scene = None
        self.current = list(maps.keys())[0]

        self.zoom = 0
        self.factor = 1

        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.setMap(self.current)

    def initScene(self,w,h):
        self.scene = QGraphicsScene(0,0,w,h)
        #self.setFixedSize(w,h)
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
                if self.scene == None:
                    self.initScene(4*size,4*size)
                tile = QGraphicsPixmapItem(QPixmap(path))
                self.scene.addItem(tile)
                tile.setPos(x*size,y*size)

        self.show()
        self.update()
        self.InitSpawnPoints(self.current)
        self.InitBeetleSpawns(self.current)
        self.InitCompoundLabels(self.current)
        self.InitCompoundEdges(self.current)

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

    def InitSpawnPoints(self,map):
        print('init.spawns')
        with open(spawn_points_file,'r') as f:
            self.spawn_points_json = json.loads(f.read())
        brush = QColor("#ff0000ff")
        pen = QColor("#ffffff")
        pts = self.spawn_points_json[map]
        self.spawns = []
        for pt in pts:
            x = pt['x']/100 * self.size().width()
            y = pt['y']/100 * self.size().height()
            self.spawns.append(
                Marker(x=x,y=y,size=16,brushColor=brush,penColor=pen)
            )
        for spawn in self.spawns:
            self.scene.addItem(spawn)
            #self.scene.addItem(spawn.textBox)

    def InitBeetleSpawns(self,map):
        print('init.beetles')
        with open(beetle_spawns_file,'r') as f:
            self.beetle_spawns_json = json.loads(f.read())
        brush = QColor("#ffff0000")
        pen = QColor("#ffffff")
        lst = self.beetle_spawns_json[map]
        self.beetles = []
        for type in lst:
            for pt in lst[type]:
                x = pt['x']/100 * self.size().width()
                y = pt['y']/100 * self.size().height()
                dot = Marker(x=x,y=y,size=16,brushColor=brush,penColor=pen)
                self.beetles.append(dot)
        for beetle in self.beetles:
            self.scene.addItem(beetle)
            #self.scene.addItem(beetle.textBox)
        self.update()

    def InitCompoundEdges(self,map):
        print('init.edges')
        with open(compounds_file,'r') as f:
            self.compound_verts_json = json.loads(f.read())
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
        print('init.labels')
        with open(compounds_file,'r') as f:
            self.compound_names_json = json.loads(f.read())
        compounds = self.compound_names_json[map]
        self.compound_labels = []
        for compound in compounds:
            for pt in compounds[compound]:
                if 'center' in pt:
                    x = compounds[compound]['center']['x']/100*self.size().width()
                    y = compounds[compound]['center']['y']/100*self.size().height()
                    if x > 0 and y > 0:
                        label = Label(compound,x=x,y=y)
                        self.compound_labels.append(label)
        for label in self.compound_labels:
            self.scene.addItem(label)
        self.update()

    def eventFilter(self, obj,event):
        if obj == self.scene:
            if event.type() == QEvent.Type.GraphicsSceneWheel:
                if event.delta() > 0:
                    self.factor = 1.25
                    self.zoom += 1
                else:
                    self.factor = 0.8
                    self.zoom -= 1
                if self.zoom > 5:
                    self.zoom = 5
                    self.factor = 1
                elif self.zoom < -1:
                    self.zoom = -1 
                    self.factor = 1
                self.scale(self.factor,self.factor)
            if event.type() == QEvent.Type.Enter:
                self.setCursor(Qt.CursorShape.ArrowCursor)
                QApplication.setOverrideCursor(Qt.CursorShape.ArrowCursor)

        elif obj == self:
            pass
        elif type(obj) == Marker:
            print("event",obj)
        return True
    
    def mousePressEvent(self, event: QMouseEvent) -> None:
        items = self.items(event.pos())
        for item in items:
            if type(item) == Marker:
                pass
        self.update()
        print(event.pos())
        return super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        self.window().statusBar.showMessage("(%s %s)" % (int(event.position().x()),int(event.position().y())))
        return super().mouseMoveEvent(event)