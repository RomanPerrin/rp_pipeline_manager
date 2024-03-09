# coding : utf-8
__author__ = 'Roman PERRIN'
#Author: Roman PERRIN

#Libraries
import maya.cmds as cmds
import maya.mel as mel
import os
import json
import sys

#files
from . import pluginUtility

def saveScene(*args):
    if cmds.file(q=True, sceneName=True):
        cmds.file(f=True, type='mayaAscii', save=True)

def openScene(dir, *args):
    cancelled = pluginUtility.warningLoaded('RenderMan_for_Maya.py', autoDisable=True)
    if cancelled:
        return

    if os.path.exists(dir):
        opened_file = cmds.file(dir, open=True , force=True)
        return

def readSetting(setting):
    file = os.path.join(sys.modules[__package__].__path__[0], 'settings.json')
    content = json.load(file)
    print(content)
    print(content[setting])


print(readSetting('pluginsToAvoid'))