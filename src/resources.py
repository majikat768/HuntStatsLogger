from PyQt6.QtCore import QSettings, QStandardPaths, QThread

from datetime import datetime
import os, sys

app_data_path = os.path.join(QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppDataLocation),'hsl_files2')

if not os.path.exists(app_data_path):
    os.makedirs(app_data_path,exist_ok=True)

json_dir = os.path.join(app_data_path,'json')
if not os.path.exists(json_dir):
    os.makedirs(json_dir,exist_ok=True)

settings = QSettings(os.path.join(app_data_path,'settings.ini'),QSettings.Format.IniFormat)
database = os.path.join(app_data_path,'huntstats.db')

def resource_path(relative_path):
    try:
    # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path,relative_path)


def mmr_to_stars(mmr):
    return 0 if mmr == -1 else 1 if mmr < 2000 else 2 if mmr < 2300 else 3 if mmr < 2600 else 4 if mmr < 2750 else 5 if mmr < 3000 else 6

def unix_to_datetime(timestamp):
    try:
        return datetime.fromtimestamp(timestamp).strftime('%H:%M %m/%d/%y')
    except Exception as e:
        print('unix_to_datetime')
        print(e)
        return -1


def GetBounties(game):
    bounties = []
    if game['MissionBagBoss_0'].lower() == 'true':    bounties.append('Butcher')
    if game['MissionBagBoss_1'].lower() == 'true':    bounties.append('Spider')
    if game['MissionBagBoss_2'].lower() == 'true':    bounties.append('Assassin')
    if game['MissionBagBoss_3'].lower() == 'true':    bounties.append('Scrapbeak')
    return bounties

def star_path():
    return os.path.join(resource_path('assets/icons'),'star.png')

def max(a,b):
    return a if a > b else b
def min(a,b):
    return a if a < b else b

deadIcon = resource_path('assets/icons/death2.png')
livedIcon = resource_path('assets/icons/lived2.png')