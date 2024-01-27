import sys, os, time, subprocess 
from PyQt6.QtCore import QSettings, QStandardPaths, Qt
from PyQt6.QtWidgets import QSizePolicy, QWidget, QHBoxLayout
from PyQt6.QtGui import QPixmap, QPainter
from Widgets.Label import Label

debug = False

tabstop = 2

game_id = "594650"

app_data_path = os.path.join(QStandardPaths.writableLocation(
    QStandardPaths.StandardLocation.AppDataLocation), 'hsl_files2')

if not os.path.exists(app_data_path):
    os.makedirs(app_data_path,exist_ok=True)

json_dir = os.path.join(app_data_path, 'json')
if not os.path.exists(json_dir):
    os.makedirs(json_dir, exist_ok=True)

logs_dir = os.path.join(app_data_path,'logs')
if not os.path.exists(logs_dir):
    os.makedirs(logs_dir, exist_ok=True)

log_file = os.path.join(logs_dir,'log.txt')

database = os.path.join(app_data_path,"huntstats.db")

settings = QSettings(os.path.join(
    app_data_path, 'settings.ini'), QSettings.Format.IniFormat)

steam_dir = settings.value("steam_dir",None)
hunt_dir = settings.value("hunt_dir",None)

def resource_path(relative_path):
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


MENU_ICON_SIZE = 36 

def log(str):
    with open(log_file,'a', encoding='utf-8') as f:
        line = "%d\t%s\n" % (int(time.time()),str)
        f.write(line)
        print(str)
    if os.stat(log_file).st_size > 1024 * 512:
        os.rename(log_file,os.path.join(logs_dir,"log_%d.txt" % int(time.time())))

def launch_hunt():
    if (settings.value("hunt_dir","") != "" and "HuntGame.exe" not in subprocess.check_output(['tasklist', '/FI', 'IMAGENAME eq HuntGame.exe']).decode()):
        log("starting hunt.exe")
        # if no steam_dir is set in the settings, try to guess steam.exe location based on hunt_dir
        steam_dir = settings.value("steam_dir","/".join(settings.value("hunt_dir").split("/")[:-3]))
        steam_exe = os.path.join(steam_dir,"steam.exe").replace("\\","/")
        log("using " + steam_exe)
        subprocess.Popen([steam_exe,"steam://rungameid/"+game_id])

def mmr_to_stars(mmr):
    if mmr == -1:
        return 0
    elif mmr < 2000:
        return 1
    elif mmr < 2300:
        return 2
    elif mmr < 2600:
        return 3
    elif mmr < 2750:
        return 4
    elif mmr < 3000:
        return 5
    else:
        return 6

def stars_pixmap(s, h=18):
    w = h*s+4*s
    #w = h*6+24
    pm = QPixmap(w,h)
    pm.fill(Qt.GlobalColor.transparent)
    qp = QPainter(pm)
    for i in range(s):
        qp.drawPixmap((w-h)-((i*h)+(i*2)),0,h,h,QPixmap(resource_path("assets/icons/mmrStar.png")))
    return pm

def get_icon(path,height=32):
    pm = QPixmap(resource_path(path))
    i = Label()
    i.setPixmap(pm.scaled(height,height))
    i.setSizePolicy(QSizePolicy.Policy.Fixed,QSizePolicy.Policy.Fixed)
    i.setFixedHeight(height)
    return i

def tab():
    return " " * tabstop


comboBoxStyle = ("QComboBox::down-arrow{\
    image:url(%s);\
    width:20px;\
    height:20px;\
    right:6;\
    }\
    QComboBox{\
    border:1px inset #888\
    }" % resource_path("assets/icons/huntArrowDown.png")).replace("\\","/")


def hunter_name(name):
    if settings.value("hide_hunter_names",False):
        return "hunter%d" % (hash(name)%9999)
    return name