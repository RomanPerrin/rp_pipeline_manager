# coding : utf-8
__author__ = 'Roman PERRIN'
#Author: Roman PERRIN

#Libraries
import json
import maya.cmds as cmds
import maya.mel as mel
import os

#files
from . import pluginUtility

print(__package__)

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
    os.path.join(__package__)
    # json.loads()