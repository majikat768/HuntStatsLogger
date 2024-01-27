import os
from PyQt6.QtWidgets import QFileDialog
from resources import settings
from DbHandler import get_pid_from_bloodlinename

def SelectSteamFolderDialog(parent):
    steam_suffix = "steam.exe"
    steam_dir = QFileDialog.getExistingDirectory(parent,"Select folder",settings.value("steam_dir","."))
    steam_path = os.path.join(steam_dir, steam_suffix)
    if not os.path.exists(steam_path):
        return False
    settings.setValue("steam_dir",steam_dir)
    parent.steamDirLabel.setText(settings.value("steam_dir"))

    if(len(settings.value("hunt_dir","")) == 0):
        hunt_suffix = "steamapps/common/Hunt Showdown"
        xml_suffix = "user/profiles/default/attributes.xml"
        if(os.path.exists(os.path.join(steam_dir,hunt_suffix,xml_suffix))):
            settings.setValue("hunt_dir",os.path.join(steam_dir,hunt_suffix))
            settings.setValue("xml_path",os.path.join(steam_dir,hunt_suffix,xml_suffix))
            parent.huntDirLabel.setText(settings.value("hunt_dir").replace(settings.value("steam_dir"),"..."))
    return True

def SelectHuntFolderDialog(parent):
    xml_suffix = "user/profiles/default/attributes.xml"
    hunt_dir = QFileDialog.getExistingDirectory(parent,"Select folder",settings.value("hunt_dir","."))
    xml_path = os.path.join(hunt_dir, xml_suffix)
    if not os.path.exists(xml_path):
        return False
    settings.setValue("hunt_dir",hunt_dir)
    settings.setValue("xml_path",xml_path)
    parent.huntDirLabel.setText(settings.value("hunt_dir"))

def ChangeSteamName(parent):
    if(parent.steamNameInput.isEnabled()):
        parent.steamNameInput.setDisabled(True)
        name = parent.steamNameInput.text()
        if len(name) > 0:
            settings.setValue("steam_name",name)
            pid = get_pid_from_bloodlinename(name)
            settings.setValue("profileid",pid)
            print("update")
            parent.parent().parent().update()
        else:
            parent.steamNameInput.setText(settings.value("steam_name",""))
    else:
        parent.steamNameInput.setDisabled(False)
        parent.steamNameInput.setFocus()
        parent.steamNameInput.selectAll()