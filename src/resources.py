import os
import subprocess
import math
import sys
import time
from datetime import datetime

from PyQt6.QtCore import QSettings, QStandardPaths
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QLabel, QSizePolicy, QWidgetItem, QSpacerItem, QApplication

app_data_path = os.path.join(QStandardPaths.writableLocation(
    QStandardPaths.StandardLocation.AppDataLocation), 'hsl_files2')
icon_size = 24

game_id = "594650"

debug = False
is_exe = getattr(sys,'frozen',False) and hasattr(sys, '_MEIPASS')

if not os.path.exists(app_data_path):
    os.makedirs(app_data_path, exist_ok=True)

json_dir = os.path.join(app_data_path, 'json')
if not os.path.exists(json_dir):
    os.makedirs(json_dir, exist_ok=True)

logs_dir = os.path.join(app_data_path,'logs')
if not os.path.exists(logs_dir):
    os.makedirs(logs_dir, exist_ok=True)

log_file = os.path.join(logs_dir,'log.txt')

database = None

settings = QSettings(os.path.join(
    app_data_path, 'settings.ini'), QSettings.Format.IniFormat)

def set_database(str):
    global database
    database = str

set_database(os.path.join(app_data_path, 'huntstats.db'))

def log(str):
    with open(log_file,'a', encoding='utf-8') as f:
        line = "%d\t%s\n" % (int(time.time()),str)
        f.write(line)
        print(str)
    if os.stat(log_file).st_size > 1024 * 512:
        os.rename(log_file,os.path.join(logs_dir,"log_%d.txt" % int(time.time())))

def resource_path(relative_path):
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


def mmr_to_stars(mmr):
    return 0 if mmr == -1 else 1 if mmr <= 2000 else 2 if mmr <= 2300 else 3 if mmr <= 2600 else 4 if mmr <= 2750 else 5 if mmr <= 3000 else 6


def unix_to_datetime(timestamp):
    try:
        return datetime.fromtimestamp(timestamp).strftime('%H:%M %m/%d/%y')
    except Exception as e:
        log('unix_to_datetime error')
        log(e)
        return -1


def GetBounties(game):
    bounties = []
    if game['MissionBagBoss_0'].lower() == 'true':
        bounties.append('Butcher')
    if game['MissionBagBoss_1'].lower() == 'true':
        bounties.append('Spider')
    if game['MissionBagBoss_2'].lower() == 'true':
        bounties.append('Assassin')
    if game['MissionBagBoss_3'].lower() == 'true':
        bounties.append('Scrapbeak')
    return bounties


def star_path():
    return os.path.join(resource_path('assets/icons'), 'star.png')


def max(a, b=None):
    if b == None:
        arr = list(a)
        maximum = arr[0]
        for i in arr:
            maximum = max(maximum,i)
        return maximum
    return a if a > b else b

def min(a, b=None):
    if b == None:
        arr = list(a)
        minimum = arr[0]
        for i in arr:
            minimum = min(minimum,i)
        return minimum
    return a if a < b else b


deadIcon = resource_path('assets/icons/death.png')
livedIcon = resource_path('assets/icons/lived2.png')
killedByIcon = resource_path('assets/icons/killedby.png')
killedIcon = resource_path('assets/icons/killed.png')
teammateKilledIcon = resource_path('assets/icons/teammatekilled.png')
killedTeammateIcon = resource_path('assets/icons/killedteammate.png')
bountyIcon = resource_path('assets/icons/bounty.png')
blankIcon = resource_path('assets/icons/blank.png')
chevronRightIcon = resource_path('assets/icons/chevron-right.svg')
chevronDownIcon = resource_path('assets/icons/chevron-down.svg')

teamTable = " "*4


def get_icon(path,x=icon_size,y=icon_size,border=True):
    pm = QPixmap(path)
    i = QLabel()
    i.setPixmap(pm.scaled(x, y))
    if border:
        i.setObjectName("icon")
    else:
        i.setObjectName("icon_borderless")
    #i.setStyleSheet("QLabel{border:1px solid white;}")
    i.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
    return i


def clearLayout(layout):
    for i in reversed(range(layout.count())):
        item = layout.itemAt(i)
        if isinstance(item,QWidgetItem):
            layout.itemAt(i).widget().setParent(None)
        elif isinstance(item,QSpacerItem):
            layout.removeItem(item)

def GoToHuntPage(timestamp,main):
    tab = main.huntsTab
    index = tab.HuntSelect.findData(timestamp)
    tab.HuntSelect.setCurrentIndex(index)
    main.tabs.setCurrentWidget(tab)
    tab.updateDetails(ts=timestamp)


def launch_hunt():
    if (settings.value("hunt_dir","") != "" and "HuntGame.exe" not in subprocess.check_output(['tasklist', '/FI', 'IMAGENAME eq HuntGame.exe']).decode()):
        log("starting hunt.exe")
        steam_dir ="/".join(settings.value("hunt_dir").split("/")[:-3])
        steam_exe = os.path.join(steam_dir,"steam.exe").replace("\\","/")
        subprocess.Popen([steam_exe,"steam://rungameid/"+game_id])