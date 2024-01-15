# coding : utf-8
__author__ = 'Roman PERRIN'
#Author: Roman PERRIN

#Libraries
import maya.cmds as cmds
import maya.mel as mel
import os
from functools import partial
import shutil
import json
from importlib import reload
import install

#files
from asset.asset import AssetUi


#self.pipe_dir/self.selectedAssetType()/self.selectedAssets()/maya/scenes/edit/self.selectedStep()

def saveScene(*args):
    if cmds.file(q=True, sceneName=True):
        cmds.file(f=True, type='mayaAscii', save=True)

def createRmanUserToken(indexToken, userTokenKeys, userTokenValues, type, *args):
    cmds.setAttr(f'rmanGlobals.UserTokens[{indexToken}].userTokenKeys', userTokenKeys, type='string')
    cmds.setAttr(f'rmanGlobals.UserTokens[{indexToken}].userTokenValues', userTokenValues, type=type)

class UI():
    def __init__(self, *args):
        self.UI()
        cmds.optionVar(iv=('isIncrementalSaveEnabled', 1))
        cmds.optionVar(iv=('rfmExtensionsInChannelBox', 0))
    
    def UI(self, *args):
        size = (200, 400)
        
        self.window = f"rp_pipeline_manager"
        if install.getInstalledBranch() != 'main':
            self.window = f"{install.getInstalledBranch()}_rp_pipeline_manager"
        if cmds.window(self.window, q=True,exists=True):
            cmds.deleteUI(self.window)
        self.window = cmds.window(self.window, wh=size, minimizeButton=False, maximizeButton=False)
        
        menuBarLayout = cmds.menuBarLayout()
        menu = cmds.menu(l='File', p=menuBarLayout)
        cmds.menuItem(l='Open pipeline directory', p=menu, c=self.openDirectory)
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
        

        #ASSET TAB
        self.tabs = cmds.tabLayout(p=self.window, innerMarginWidth=5, innerMarginHeight=5)
        asset_lay = cmds.columnLayout(p=self.tabs, adjustableColumn=True)

        self.assetUI = AssetUi(asset_lay)
        

        #SHOT TAB
        shot_lay = cmds.columnLayout(p=self.tabs, adjustableColumn=True)


        cmds.tabLayout( self.tabs, edit=True, tabLabel=((asset_lay, 'Asset'), (shot_lay, 'Shot')) )

        try:
            self.pipe_dir = self.loadPipelineDirectory()
            cmds.textField(self.pipeline_dir, e=True, text=self.pipe_dir)
            self.getPipelineDirectory()
        except:
            pass
        
        cmds.showWindow(self.window)
    
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
        dir = os.path.normpath(self.pipe_dir)
        os.popen(fr'explorer "{dir}"')

    def fileDialog(self, fileMode, caption, *args):
        filename = cmds.fileDialog2(fileMode=fileMode, caption=caption)[0]
        cmds.textField(self.pipeline_dir, e=True, text=filename)
        self.savePipelineDirectory(filename)
        dir = self.getPipelineDirectory()
        self.assetUI.pipe_dir = dir
        self.assetUI.updateAssetTypeScrollList()
    
    def savePipelineDirectory(self, pipeline_dir, *args):
        with open(f"{os.path.dirname(__file__)}/data.json", "w") as file:
            json.dump(pipeline_dir, file)
    
    def loadPipelineDirectory(self, *args):
        with open(f"{os.path.dirname(__file__)}/data.json", "r") as file:
            return json.load(file)
    
    def getPipelineDirectory(self, *args):
        self.pipe_dir = cmds.textField(self.pipeline_dir, q=True, text=True)
        return cmds.textField(self.pipeline_dir, q=True, text=True)
    
    