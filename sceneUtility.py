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

print(__package__)
print(__name__)
print(getattr(sys.modules[__package__], __package__))

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
    os.path.join(eval(__package__).__path__)
    # json.loads()