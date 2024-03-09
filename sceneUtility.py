# coding : utf-8
__author__ = 'Roman PERRIN'
#Author: Roman PERRIN

#Libraries
import maya.cmds as cmds
import maya.mel as mel
import os
import json
import sys

print("sceneUtility")
#files
from . import pluginUtility

def saveScene(*args):
    if cmds.file(q=True, sceneName=True):
        cmds.file(f=True, type='mayaAscii', save=True)

def openScene(dir, projectDir='', *args):
    cancelled = pluginUtility.checkPlugin()
    if cancelled:
        return

    if projectDir:
        try:
            mel.eval(f'setProject "{projectDir}"')
        except:
            raise RuntimeError(f'error setting project: {projectDir}')

    try:
        opened_file = cmds.file(dir, open=True , force=True)
    except:
        raise IOError('error opening file: ' dir)

def readSetting(setting):
    file = os.path.join(sys.modules[__package__].__path__[0], 'settings.json')

    content = []
    with open(file, 'r') as j:
        content = json.loads(j.read())[setting]
    
    if not content:
        raise NameError(f'{setting} setting not found')
    
    return content    
