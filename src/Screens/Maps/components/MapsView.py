from PyQt6.QtWidgets import QGraphicsView,QGraphicsScene,QGraphicsPixmapItem, QSizePolicy
from PyQt6.QtGui import QMouseEvent, QPixmap, QBrush,QColor, QPen
from PyQt6.QtCore import QEvent, QObject, Qt, QPoint 
from PIL import Image
from resources import resource_path
import json, os
from Screens.Maps.components.Marker import Label, Border, Marker

maps = {
    "DeSalle": resource_path("assets/maps/desalle"),
    "Lawson Delta": resource_path("assets/maps/lawson"),
    "Stillwater Bayou": resource_path("assets/maps/stillwater"),
}

compounds_file = resource_path("assets/json/compound_coordinates.json")
beetles_file = resource_path("assets/json/beetle_spawns.json")
rotjaw_file = resource_path("assets/json/rotjaw.json")

class MapsView(QGraphicsView):
    def __init__(self,parent):
        super().__init__()
        self.parent = parent

        self.setMouseTracking(True)

        self.pan = False
        self.panStart = QPoint(0,0)

        self.factor = 1
        self.zoom = 1
        self.scene = None
        self.current = list(maps.keys())[0]

        self.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)

        self.setMap(self.current)

    def initScene(self,w,h):
        self.scene = QGraphicsScene(0,0,w,h)
        self.setScene(self.scene)
        self.scene.installEventFilter(self)

    def setMap(self,map):
        self.current = map
        if self.scene:
            self.scene.clear()
        size = int(min(
            self.parent.size().width(),
            self.parent.size().height()
        )/5*1.0)
        self.setFixedSize(size*4,size*4)
        if self.scene == None:
            self.initScene(size*4,size*4)
        for f in os.listdir(maps[self.current]):
            if ".png" in f:
                x = int(f.split("-")[1].split(".")[0])
                y = int(f.split("-")[2].split(".")[0])
                path = os.path.join(maps[self.current],f)
                tile = QGraphicsPixmapItem(QPixmap(path))
                tile.setScale(size/Image.open(path).size[0])
                tile.setZValue(0)
                self.scene.addItem(tile)
                tile.setPos(x*size,y*size)

        self.initCompoundLabels(map)
        self.initCompoundBorders(map)
        self.initBeetleSpawns(map)
        #self.initRotjaw(map)
        self.show()
        self.update()
    
    def initCompoundLabels(self,map):
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

    def initCompoundBorders(self,map):
        with open(compounds_file,'r') as f:
            self.compound_verts_json = json.loads(f.read())['compounds']
        self.compound_borders = []
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

    def initBeetleSpawns(self,map):
        with open(beetles_file,'r') as f:
            self.beetle_json = json.loads(f.read())
        pbrush = QBrush(QColor("#44ff0000"))
        rbrush = QBrush(QColor("#440000ff"))
        ppen = QPen(QColor("#ff0000"))
        ppen.setWidth(4)
        rpen = QPen(QColor("#0000ff"))
        rpen.setWidth(4)
        #pen = QColor("#ffffff")
        lst = self.beetle_json[map]
        self.beetles = []
        for type in lst:
            for pt in lst[type]:
                x = pt['x']/100 * self.size().width()
                y = pt['y']/100 * self.size().height()
                dot = Marker(x=x,y=y,brushColor=pbrush,penColor=ppen)
                self.beetles.append(dot)
        for beetle in self.beetles:
            self.scene.addItem(beetle)
            #self.scene.addItem(beetle.textBox)
        self.update()

    def initRotjaw(self,map):
        with open(rotjaw_file,'r') as f:
            self.rotjaw_json = json.loads(f.read())
        pbrush = QBrush(QColor("#4444aa44"))
        rbrush = QBrush(QColor("#440000ff"))
        ppen = QPen(QColor("#44aa44"))
        ppen.setWidth(4)
        rpen = QPen(QColor("#0000ff"))
        rpen.setWidth(4)
        #pen = QColor("#ffffff")
        lst = self.rotjaw_json[map]
        self.rotjaw = []
        for type in lst:
            for pt in lst[type]:
                x = pt['x']/100 * self.size().width()
                y = pt['y']/100 * self.size().height()
                dot = Marker(x=x,y=y,brushColor=pbrush,penColor=ppen)
                self.rotjaw.append(dot)
        for rotjaw in self.rotjaw:
            self.scene.addItem(rotjaw)
            #self.scene.addItem(beetle.textBox)
        self.update()


    def toggleCompoundBorders(self):
        for border in self.compound_borders:
            border.toggle()

    def toggleBeetles(self):
        for beetle in self.beetles:
            beetle.toggle()

    def toggleRotjaw(self):
        for rotjaw in self.rotjaw:
            rotjaw.toggle()

    def toggleCompoundLabels(self):
        state = not self.compound_labels[0].isVisible()
        for label in self.compound_labels:
            label.setVisible(state)

    def eventFilter(self, obj: QObject, event: QEvent) -> bool:
        if obj == self.scene:
            if event.type() == QEvent.Type.GraphicsSceneWheel:
                if event.delta() > 0:
                    if self.zoom < 4:
                        self.factor = 1.25
                        self.zoom *= self.factor
                        self.scale(self.factor,self.factor)
                elif event.delta() < 0:
                    if self.zoom > 0.8:
                        self.factor = 0.8
                        self.zoom *= self.factor
                        self.scale(self.factor,self.factor)
        return super().eventFilter(obj, event)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        self.pan = True
        self.panStart = QPoint(event.pos().x(),event.pos().y())
        return super().mousePressEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        self.pan = False
        return super().mouseReleaseEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if self.pan:
            pass
        else:
            x = event.pos().x() / self.size().width() * 1000
            y = event.pos().y() / self.size().width() * 1000
            self.window().statusBar.showMessage("(%d,%d)" % (x,y))

        return super().mouseMoveEvent(event)