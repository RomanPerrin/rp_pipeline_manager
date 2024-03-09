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
    try:
        plugins = readSetting('pluginsToAvoid')
        cancelled = pluginUtility.warningLoaded(plugins, autoDisable=True)
        if cancelled:
            return
    except NameError as e:
        print(e)

    if os.path.exists(dir):
        opened_file = cmds.file(dir, open=True , force=True)
        return

def readSetting(setting):
    file = os.path.join(sys.modules[__package__].__path__[0], 'settings.json')

    content = []
    with open(file, 'r') as j:
        content = json.loads(j.read())[setting]
    
    if not content:
        raise NameError(f'{setting} setting not found')
    
