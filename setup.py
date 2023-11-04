# coding : utf-8
__author__ = 'Roman PERRIN'
#Author: Roman PERRIN

import maya.cmds as cmds
import os
import sys
import maya.mel as mel
import autoUpdate
from importlib import reload
reload(autoUpdate)

path = os.path.join(autoUpdate.dir, autoUpdate.repo_name).replace(os.sep, '/')

def installShelf():
    currentShelfLayout = mel.eval('$tmpVar=$gShelfTopLevel')
    currentShelf = cmds.shelfTabLayout(currentShelfLayout, q=1, selectTab=1)
    
    buttons = cmds.shelfLayout(currentShelf, q=1, ca=1)
    for button in buttons:
        if cmds.shelfButton(button, q=1, ex=1):
            if 'Pipeline Manager' in cmds.shelfButton(button, q=1, l=1):
                return
    
    button = cmds.shelfButton(parent = currentShelf,
                visible = 1,
                flexibleWidthType = 1,
                annotation = "Pipeline Manager",
                label = "Pipeline Manager",
                useAlpha = 1,
                style = "iconOnly",
                image = f"{path}/icone2.svg",
                command = "import rp_pipeline_manager\nfrom importlib import reload\nreload(rp_pipeline_manager)",
                sourceType = "python",
                commandRepeatable = 1,
                flat = 1)
    
    return

def installOnStartup():
    global path
    user_setup = """
import maya.cmds as cmds
cmds.evalDeferred('''if cmds.optionVar(q='rp_pipeline_manager_autoUpdate') == 1:
    import rp_pipeline_manager
    rp_pipeline_manager.autoUpdate.updater()''')"""
    file = ''
    
    dir = os.path.join(os.path.dirname(cmds.internalVar(usd=1)), 'scripts', 'userSetup.py').replace(os.sep, '/')
    
    try:
        with open(dir, 'r') as f:
            file = f.read()
    except:
        pass
    
    if not user_setup in file:
        with open(dir, 'w') as f:
            f.write(file + user_setup)

def installer():
    installShelf()
    installOnStartup()
    if not cmds.optionVar(exists='rp_pipeline_manager_autoUpdate'):
        cmds.optionVar(iv=('rp_pipeline_manager_autoUpdate', 1))
    