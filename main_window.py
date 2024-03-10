# coding : utf-8
__author__ = 'Roman PERRIN'
#Author: Roman PERRIN

#Libraries
import sys
from typing import Callable
import maya.cmds as cmds
import maya.mel as mel
import os
from functools import partial
import shutil
import json
from importlib import reload

#files
from .asset import asset
from .shot import shot
from . import instancer
from . import install
from . import pluginUtility

icon_size = 35
row_size = 35
pipe_dir = ""

#self.pipe_dir/self.selectedAssetType()/self.selectedAssets()/maya/scenes/edit/self.selectedStep()

def createRmanUserToken(indexToken, userTokenKeys, userTokenValues, type, *args):
    cmds.setAttr(f'rmanGlobals.UserTokens[{indexToken}].userTokenKeys', userTokenKeys, type='string')
    cmds.setAttr(f'rmanGlobals.UserTokens[{indexToken}].userTokenValues', userTokenValues, type=type)

class UI():
    def __init__(self, *args):
        self.UI()
        cmds.optionVar(iv=('isIncrementalSaveEnabled', 1))
        cmds.optionVar(iv=('incrementalSaveLimitBackups', 1))
        cmds.optionVar(iv=('incrementalSaveMaxBackups', 10))
    
    def UI(self, *args):
        global pipe_dir
        size = (300, 600)
        
        self.window = f"rp_pipeline_manager"
        if install.getInstalledBranch() != 'main':
            self.window = f"{install.getInstalledBranch()}_rp_pipeline_manager"
        if cmds.window(self.window, q=True,exists=True):
            cmds.deleteUI(self.window)
        self.window = cmds.window(self.window, wh=size, minimizeButton=True, maximizeButton=False)
        
        menuBarLayout = cmds.menuBarLayout()
        menu = cmds.menu(l='File', p=menuBarLayout)
        cmds.menuItem(l='Open pipeline directory', p=menu, c=self.openDirectory)
        menu = cmds.menu(l='Tools', p=menuBarLayout)
        cmds.menuItem(l='Change Cameras Clip Plane', p=menu, c=self.changeCamerasClipPlane)
        cmds.menuItem(l='Auto Instancer', p=menu, c=instancer.autoInstance)
        cmds.menuItem(l='create set instance for current selection', p=menu, c=self.createSetInstance)
        menu = cmds.menu(l='About', p=menuBarLayout)
        cmds.menuItem(l='Update', p=menu, c=self.update)

        state = 0
        if install.mode == 'dev':
            state = 1
        self.mode = cmds.menuItem(l='Dev mode', cb=state, p=menu, c=self.changeMode)

        
        #file dialog
        pipe_dir_lay = cmds.rowLayout(p=self.window, numberOfColumns=3, height=row_size, adjustableColumn=1)
        self.pipeline_dir = cmds.textField(p=pipe_dir_lay)
        cmds.symbolButton(p=pipe_dir_lay, ann='browse', i='fileOpen.png', height=icon_size, width=icon_size, command=partial(self.fileDialog, 2, "Pipeline directory"))
        

        self.tabs = cmds.tabLayout(p=self.window, innerMarginWidth=5, innerMarginHeight=5)

        #ASSET TAB
        self.assetUI = asset.AssetUi(self.tabs)
        
        #SHOT TAB
        self.shotUI = shot.ShotUi(self.tabs)

        cmds.tabLayout( self.tabs, edit=True, tabLabel=((self.assetUI.asset_lay, 'Asset'), (self.shotUI.layout, 'Shot')) )

        try:
            pipe_dir = self.loadPipelineDirectory()
            cmds.textField(self.pipeline_dir, e=True, text=pipe_dir)
            self.getPipelineDirectory()
            self.assetUI.updateAssetTypeScrollList()
            self.shotUI.updateSequenceScrollList()
        except:
            pass
        
        cmds.showWindow(self.window)
        
        pluginUtility.warningLoaded('RenderMan_for_Maya.py', autoDisable=True)


    def changeCamerasClipPlane(self, *args):
        cameras = cmds.ls(cameras=1)
        for camera in cameras:
            cmds.setAttr(f'{camera}.nearClipPlane', 10)
            cmds.setAttr(f'{camera}.farClipPlane', 100000)

    def createSetInstance(self, *args):
        shapes = set(cmds.listRelatives(cmds.ls(sl=1, l=1), ad=1, type='mesh', f=1))
        if not shapes:
            print('no mesh found')
            return
        setName = cmds.sets(cmds.listRelatives(shapes, p=1, pa=1), n='enviro')
        print(f'created {setName}')
        return

    def update(self, *args):
        install.updater()
        cmds.deleteUI(self.window)
        import rp_pipeline_manager
        reload(rp_pipeline_manager)
        rp_pipeline_manager.main_window.UI()
        print('Reloaded UI')

    def changeMode(self, *args):
        state = cmds.menuItem(self.mode, q=1, cb=1)
        if state:
            install.mode = 'dev'
        else:
            install.mode = ''
        print(install.mode)
        return

    def openDirectory(self, *args):
        global pipe_dir
        dir = os.path.normpath(pipe_dir)
        os.popen(fr'explorer "{dir}"')

    def fileDialog(self, fileMode, caption, *args):
        filename = cmds.fileDialog2(fileMode=fileMode, caption=caption)[0]
        cmds.textField(self.pipeline_dir, e=True, text=filename)
        self.savePipelineDirectory(filename)
        self.getPipelineDirectory()
    
    def savePipelineDirectory(self, pipeline_dir, *args):
        with open(f"{os.path.dirname(__file__)}/data.json", "w") as file:
            json.dump(pipeline_dir, file)
    
    def loadPipelineDirectory(self, *args):
        with open(f"{os.path.dirname(__file__)}/data.json", "r") as file:
            return json.load(file)
    
    def getPipelineDirectory(self, *args):
        global pipe_dir
        pipe_dir = cmds.textField(self.pipeline_dir, q=True, text=True)
        self.assetUI.updateAssetTypeScrollList()
        self.shotUI.updateSequenceScrollList()
        return cmds.textField(self.pipeline_dir, q=True, text=True)
    
    
def scrollListAdd(layout:str, name:str, updateScrollList:Callable, addCommand:Callable):
    lay = cmds.formLayout(p=layout)
    scrollList = cmds.textScrollList(name, p=lay, numberOfRows=5, allowMultiSelection=False, selectCommand=partial(updateScrollList))
    addButton = cmds.symbolButton('{name}AddButton', p=lay, ann=f'add {name}', i='pickHandlesComp', height=icon_size, width=icon_size, command=partial(addCommand))
    # Attach the assetsScrollList
    cmds.formLayout(lay, e=True, attachForm=[(scrollList, "left", 0), (scrollList, "top", 0), (scrollList, "bottom", 0)])
    # Attach the assetsAddButton
    cmds.formLayout(lay, e=True, attachForm=[(addButton, "right", 0), (addButton, "top", 0)])
    cmds.formLayout(lay, e=True, attachControl=[(scrollList, "right", 0, addButton)])
