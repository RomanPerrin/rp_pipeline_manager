# coding : utf-8
__author__ = 'Roman PERRIN'
#Author: Roman PERRIN

#Libraries
import maya.cmds as cmds
import maya.mel as mel
import os

#files
import pluginUtility

def saveScene(*args):
    if cmds.file(q=True, sceneName=True):
        cmds.file(f=True, type='mayaAscii', save=True)

def openScene(dir, *args):
    dismissed = pluginUtility.warningLoaded('RenderMan_for_Maya.py', autoDisable=True)
    if dismissed:
        return

    if os.path.exists(dir):
        opened_file = cmds.file(dir, open=True , force=True)
        return
