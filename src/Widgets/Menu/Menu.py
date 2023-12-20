from PyQt6.QtWidgets import QVBoxLayout, QFrame
from PyQt6.QtGui import QIcon
from Widgets.Menu.MenuButton import MenuButton
from resources import resource_path, launch_hunt, MENU_ICON_SIZE
from Settings.Settings import Settings

PAD = 8

class Menu(QFrame):
    def __init__(self,parent):
        super().__init__(parent)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.layout.setContentsMargins(PAD,PAD,PAD,PAD)
        self.layout.setSpacing(PAD)

        self.setObjectName("Menu")
        self.buttons = {}

        self.expanded = False

        self.addTab("Menu")
        self.addTab("Hunts Recap")
        self.addTab("Hunters")
        self.addTab("Teams")
        self.addTab("Analytics")
        self.addTab("Records")

        self.layout.addStretch()

        self.addTab("Launch Hunt")
        self.addTab("Settings")

        self.settings = Settings(self.parent())
        
        self.setMinimumHeight(MENU_ICON_SIZE*len(self.buttons)*2)

        self.set_focus("Hunts Recap")

    def addTab(self, text):
        tab = MenuButton(
            QIcon(resource_path("assets/icons/menubar/%s.png"%text)),
            text,
            self)
        tab.setAction(self.button_action)
        self.buttons[text] = tab
        self.layout.addWidget(tab)

    def resize(self,height):
        self.setGeometry(0,0,self.sizeHint().width(),height)

    def button_action(self,button):
        print(button)
        if(button == "Menu"):
            self.expand()
        elif(button == "Launch Hunt"):
            launch_hunt()
            if(self.expanded):
                self.expand()

        elif(button == "Settings"):
            self.settings.show()
            if(self.expanded):
                self.expand()
        else:
            self.parent().setCurrentWidget(button)
            self.set_focus(button)
            if(self.expanded):
                self.expand()

    def set_focus(self,button):
        for b in self.buttons:
            self.buttons[b].set_focus(False)
        self.buttons[button].set_focus(True)

    def expand(self):
        self.expanded = not self.expanded
        if(self.expanded):
            self.setObjectName("MenuExp")
        else:
            self.setObjectName("Menu")
        for button in self.buttons:
            self.buttons[button].showLabel(self.expanded)
        self.resize(self.height())
        self.style().polish(self)
        self.ensurePolished()
