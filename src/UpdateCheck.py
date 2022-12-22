from PyQt6.QtWidgets import QLabel, QPushButton, QWidget, QHBoxLayout,QSizePolicy

from resources import is_exe, version, api_url
from Widgets.Toast import Toast
import requests

global yesToast, noToast

def init_toast(parent):
    global yesToast, noToast
    getBtn = QPushButton("\t\tOpen in browser\t\t")
    xBtn = QPushButton("\t\tX\t\t")
    yesToast = Toast("A new update is available.",parent=parent,widgets=[getBtn,xBtn])
    getBtn.clicked.connect(lambda : get_update(parent=parent))
    getBtn.clicked.connect(yesToast.close)
    xBtn.clicked.connect(yesToast.close)

    noToast = Toast("No updates available.",parent=parent,duration=2)

def check_for_updates():
    global yesToast
    update = update_available()
    if update_available():
        yesToast.show()
    else:
        noToast.show()

def update_available():
    #res = {0:{'tag_name':'v9.0.0'}}
    res = requests.get(api_url).json()
    if (len(res) > 0) or 1:
        latest = res[0]['tag_name']
        if latest > version:
            return True
        else:
            return False

def get_update(parent=None):
    import webbrowser
    res = requests.get(api_url).json()
    if len(res) > 0:
        res = requests.get(api_url).json()
        release_url = res[0]['html_url']
        webbrowser.open(release_url)
        #show_update_window(release_url=release_url,parent=parent)
        return release_url
    return None

def show_update_window(release_url=None,parent=None):
    from Widgets.Modal import Modal
    from PyQt6.QtWidgets import QPushButton
    import webbrowser
    win = Modal(parent)
    win.addWidget(QLabel("An Update Is Available"))
    btn = QPushButton("Show in browser")
    btn.clicked.connect(lambda : webbrowser.open(release_url))
    win.addWidget(btn)
    win.show()