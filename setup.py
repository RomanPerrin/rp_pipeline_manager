# coding : utf-8
__author__ = 'Roman PERRIN'
#Author: Roman PERRIN

#Libraries
import maya.cmds as cmds
import os
import maya.mel as mel

#files
import rp_pipeline_manager


path = rp_pipeline_manager.__path__[0]

def installShelf() -> None:
    currentShelfLayout = mel.eval('$tmpVar=$gShelfTopLevel')
    currentShelf = cmds.shelfTabLayout(currentShelfLayout, q=1, selectTab=1)
    
    buttons = cmds.shelfLayout(currentShelf, q=1, ca=1)
    for button in buttons:
        if cmds.shelfButton(button, q=1, ex=1):
            if 'Pipeline Manager' in cmds.shelfButton(button, q=1, l=1):
                cmds.deleteUI(button)
    
    button = cmds.shelfButton(parent = currentShelf,
                visible = 1,
                flexibleWidthType = 1,
                annotation = "Pipeline Manager",
                label = "Pipeline Manager",
                useAlpha = 1,
                style = "iconOnly",
                image = f"{path}/icons/icone2.svg",
                command = "import rp_pipeline_manager\nfrom importlib import reload\nreload(rp_pipeline_manager)\nrp_pipeline_manager.main_window.UI()",
                sourceType = "python",
                commandRepeatable = 1,
                flat = 1)
    
    return

def installOnStartup() -> None:
    global path
    user_setup = """
import maya.cmds as cmds
cmds.evalDeferred('''
import rp_pipeline_manager
rp_pipeline_manager.install.updater()''')"""
    file = ''
    
    dir = os.path.join(os.path.dirname(cmds.internalVar(usd=1)), 'userSetup.py').replace(os.sep, '/')
    
    try:
        with open(dir, 'r') as f:
            file = f.read()
    except:
        pass
    
    if not user_setup in file:
        with open(dir, 'w') as f:
            f.write(file + user_setup)

def installer() -> None:
    installShelf()
    installOnStartup()
    
