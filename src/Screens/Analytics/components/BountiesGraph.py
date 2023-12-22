from PyQt6.QtGui import QColor, QFont, QPen
from PyQt6.QtCore import QRectF
import pyqtgraph
from DbHandler import execute_query
from Screens.Analytics.components.PlotItem import PlotItem

font = QFont()
font.setFamily("Arial")
font.setWeight(600)
font.setPixelSize(16)

brushes=[
    QColor("#c3cfc7"),
    QColor("#cccccc"),
    QColor("#ccbba6"),
    QColor("#9c7661"),
    QColor("#798c5d"),
    QColor("#283940"),
    QColor("#51181B")
]

class BountiesGraph(PlotItem):
    def __init__(self, parent=None, name=None, labels=None, title=None, viewBox=None, axisItems=None, enableMenu=True, **kargs):
        super().__init__(parent, name, labels, title, viewBox, axisItems, enableMenu, **kargs)
        self.legend = pyqtgraph.LegendItem(colCount=2)
        self.layout.setContentsMargins(0,0,0,0)
        self.ymax = 0
        self.setFixedHeight(200)

        self.data = {}

        ticks = [
            [
                (0,"Skunked"),
                (15,"Single"),
                (30,"Double"),
                (45,"Triple"),
                (60,"Gauntlet"),
                #(75,"Extractions"),
                #(90,"Died"),
            ]
        ]
            

        self.getAxis("bottom").setTickSpacing(major=15, minor=15)
        self.getAxis("bottom").setTicks(ticks)
        self.getAxis("bottom").setLabel(" ")
        self.getAxis("left").setLabel("Hunts")
        self.setTitle("Extraction Results")

        self.setBountiesData()

    def setBountiesData(self):
        self.clear()
        vals = execute_query("SELECT category, count(*) FROM 'accolades' where category like 'accolade_extract\_%token%' escape '\\' group by category;")
        extractions = execute_query("select count(*) from 'games' where MissionBagIsQuickPlay = 'false' and MissionBagIsHunterDead = 'false'")
        extractions = execute_query("select sum(case when g.MissionBagIsHunterDead = 'false' then 1 else 0 end) as survived,\
                             count(*) as total from 'games' g where g.MissionBagIsQuickPlay = 'false'")

        if len(extractions) == 0:
            return
        extractions = extractions[0]
        if extractions == None or extractions[0] == None or extractions[1] == None:
            return
        extractions = {
            "extractions":extractions[0],
            "total":extractions[1]
        }
        extractions['died'] = extractions['total'] - extractions['extractions']
        if extractions == 0:
            return
        tokens = { 
            "Skunked":0,
            "Single":0,
            "Double":0,
            "Triple":0,
            "Gauntlet":0,
        }

        for v in vals:
            if "four_tokens" in v[0]:
                tokens["Gauntlet"] = v[1]
            elif "three_tokens" in v[0]:
                tokens["Triple"] = v[1]
            elif "two_tokens" in v[0]:
                tokens["Double"] = v[1]
            elif "one_token" in v[0]:
                tokens["Single"] = v[1]

        tokens["Skunked"] = extractions['extractions'] - sum(tokens.values())
        self.ymax = max(tokens.values())

        heights = [ tokens[i] for i in tokens.keys() ]
        heights = heights + [extractions['extractions'], extractions['died']]

        self.bars = []
        [bar,label] = get_bar(tokens['Skunked'],0)
        self.addItem(bar)
        self.addItem(label)
        [bar,label] = get_bar(tokens['Single'],1)
        self.addItem(bar)
        self.addItem(label)
        [bar,label] = get_bar(tokens['Double'],2)
        self.addItem(bar)
        self.addItem(label)
        [bar,label] = get_bar(tokens['Triple'],3)
        self.addItem(bar)
        self.addItem(label)
        [bar,label] = get_bar(tokens['Gauntlet'],4)
        self.addItem(bar)
        self.addItem(label)
        [bar,label] = get_bar(extractions['extractions'],5)
        #self.addItem(bar)
        #self.addItem(label)
        [bar,label] = get_bar(extractions['died'],6)
        #self.addItem(bar)
        #self.addItem(label)
        '''
        for n in range(0,5):
            bar = pyqtgraph.BarGraphItem(
                    x = x[n],
                    height = heights[n],
                    width = widths[n],
                    brush = brushes[0][n])
            self.addItem(bar)
            label = pyqtgraph.TextItem(str(heights[n]),anchor=(0.5,1),color=(223,223,223),)
            label.setPos(x[n],heights[n])
            self.addItem(label,ignoreBounds=True)
            label.setFont(self.font)
        self.addItem(pyqtgraph.BarGraphItem(
            x = x[5],
            height = heights[5],
            width = widths[5],
            brush = brushes[0][5]
        ))
        self.addItem(pyqtgraph.BarGraphItem(
            x = x[6],
            height = heights[6],
            width = widths[6],
            brush = brushes[0][6]
        ))
        '''
        self.setLimits(yMin=0,yMax = self.ymax*1.2, xMin=-10,xMax=70)
        self.setXRange(-10,70)
        self.setYRange(0,self.ymax*1.2)

    def update(self):
        self.setBountiesData()

def str_to_n(txt):
    return 4 if txt == "four" else 3 if txt == "three" else 2 if txt == "two" else 1 if txt == "one" else 0
def n_to_str(n):
    return "four"  if n == 4 else "three" if n  == 3 else "two" if n == 2 else "one" if n == 1 else "zero"

def get_bar(height,n):
    width = 10
    bar = pyqtgraph.BarGraphItem(
        x=n*width*1.5,
        height=height,
        width=width,
        brush=brushes[n]
    )
    label = pyqtgraph.TextItem(
        str(height),
        anchor=(0.5,1),
        color=(233,233,233)
    )
    label.setPos(n*width*1.5,height)
    label.setFont(font)
    return [bar,label]

class BountiesWindow(pyqtgraph.GraphicsLayoutWidget):
    def __init__(self, parent=None, show=False, size=None, title=None, **kargs):
        super().__init__(parent, show, size, title, **kargs)
        self.bountiesGraph  = BountiesGraph()
        self.addItem(self.bountiesGraph,0,0)
        self.setFixedHeight(220)

    def update(self):
        self.bountiesGraph.update()