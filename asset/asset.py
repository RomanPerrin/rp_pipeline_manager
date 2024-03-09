# coding : utf-8
__author__ = 'Roman PERRIN'
#Author: Roman PERRIN

#Libraries
from fileinput import filename
from typing_extensions import runtime
import maya.cmds as cmds
import maya.mel as mel
import os
from functools import partial

#files
from . import publish
from . import addAsset
from .. import main_window
from .. import sceneUtility

icon_size = 35
row_size = 35

class AssetUi():
    def __init__(self, parent_layout) -> None:
        self.parent_layout = parent_layout
        self.asset_lay = cmds.formLayout(p=self.parent_layout)

        #List asset type
        self.assetTypeScrollList = cmds.textScrollList('assetType', p=self.asset_lay, numberOfRows=5, allowMultiSelection=False, selectCommand=self.search)

        #search field
        self.search_field = cmds.textField(p=self.asset_lay, sf=1, tcc=self.search)

        #List assets
        assets_lay = cmds.formLayout(p=self.asset_lay)
        assetsScrollList = cmds.textScrollList('assets', p=assets_lay, numberOfRows=5, allowMultiSelection=False, selectCommand=self.updateStepScrollList)
        assetsAddButton = cmds.symbolButton('assetsAddButton', p=assets_lay, ann=f'add asset', i='pickHandlesComp', height=icon_size, width=icon_size, command=self.addAsset)
        assetsOpenDirectoryButton = cmds.symbolButton('assetsOpenDirectoryButton', p=assets_lay, ann=f'Open asset directory', i='fileOpen', height=icon_size, width=icon_size, command=self.openDirectory)
        # Attach the assetsScrollList
        cmds.formLayout(assets_lay, e=True, attachForm=[(assetsScrollList, "left", 0), (assetsScrollList, "top", 0), (assetsScrollList, "bottom", 0)])
        # Attach the assets*Buttons
        cmds.formLayout(assets_lay, e=True, attachForm=[(assetsAddButton, "right", 0),
                                                        (assetsAddButton, "top", 0),
                                                        (assetsOpenDirectoryButton, "right", 0)])
        cmds.formLayout(assets_lay, e=True, attachControl=[(assetsScrollList, "right", 0, assetsAddButton),
                                                           (assetsScrollList, "right", 0, assetsOpenDirectoryButton),
                                                           (assetsOpenDirectoryButton, "top", 0, assetsAddButton)])

        #List working step
        self.stepScrollList = cmds.textScrollList('steps', p=self.asset_lay, numberOfRows=3, allowMultiSelection=False)

        self.openButton = cmds.button(p=self.asset_lay, label="open", command=self.openLastEdit)
        self.publishButton = cmds.button(p=self.asset_lay, label="publish", command=partial(publish.publish, self))
        self.importRefButton = cmds.button(p=self.asset_lay, label="import as reference", command=self.importAsReference)

        cmds.formLayout( self.asset_lay, edit=True,
                        attachForm=[(self.assetTypeScrollList, 'top', 5),
                                    (self.assetTypeScrollList, 'left', 5),
                                    (self.assetTypeScrollList, 'right', 5),

                                    (self.search_field, 'left', 5),
                                    (self.search_field, 'right', 5),
                                    (assets_lay, 'left', 5),
                                    (assets_lay, 'right', 5),
                                    (self.stepScrollList, 'left', 5),
                                    (self.stepScrollList, 'right', 5),
                                    (self.openButton, 'left', 5),
                                    (self.openButton, 'right', 5),
                                    (self.publishButton, 'left', 5),
                                    (self.publishButton, 'right', 5),
                                    (self.importRefButton, 'left', 5),
                                    (self.importRefButton, 'right', 5),
                                    (self.importRefButton, 'bottom', 5) ],

                        attachControl=[(self.search_field, 'top', 5, self.assetTypeScrollList),
                                       (assets_lay, 'top', 5, self.search_field),
                                       (self.stepScrollList, 'bottom', 5, self.openButton),
                                       (self.publishButton, 'bottom', 5, self.importRefButton),
                                       (self.openButton, 'bottom', 5, self.publishButton),
                                       (assets_lay, 'bottom', 5, self.stepScrollList)])


        try:
            self.getAssetsDirectory()
            self.updateAssetTypeScrollList()
        except:
            pass

    def search(self, *args):
        self.updateStepScrollList()
        search_text = cmds.textField(self.search_field, q=1, tx=1)

        assetList = []
        assets = self.getAssets()
        searchList = search_text.split(' ')
        while ('' in searchList):
            searchList.remove('')

        for asset in assets:
            for word in searchList:
                if not word.lower() in asset.lower():
                    break
            else:
                assetList.append(asset)

        cmds.textScrollList('assets', e=True, removeAll=True)
        cmds.textScrollList('assets', e=True, append=assetList)
        cmds.symbolButton('assetsAddButton', e=True, ann=f'add {self.selectedAssetType()}')
        return assetList

    def getAssetsDirectory(self, *args):
        asset_dir = os.path.join(self.pipe_dir, '04_asset').replace(os.sep, '/')
        if not os.path.isdir(asset_dir):
            raise Exception('Assets folder name not found')

        return asset_dir

    def getAssetTypeDirectory(self, *args):
        assetsDir = self.getAssetsDirectory()
        selectedAssetType = self.selectedAssetType()
        if not assetsDir or not selectedAssetType:
            return
        return (os.path.join(assetsDir, selectedAssetType)).replace(os.sep, '/')

    def getAssetDirectory(self, *args):
        assetTypeDir = self.getAssetTypeDirectory()
        selectedAsset = self.selectedAssets()
        if not assetTypeDir or not selectedAsset:
            return
        
        return (os.path.join(assetTypeDir, selectedAsset)).replace(os.sep, '/')

    def updateAssetTypeScrollList(self, *args):
        self.pipe_dir = main_window.pipe_dir
        if not self.pipe_dir.split('/')[-1] in ['character', 'dress', 'module', 'prop', 'set']:
            assetType = self.getAssetType(self.getAssetsDirectory())
            cmds.textScrollList('assetType', e=True, removeAll=True)
            cmds.textScrollList('assetType', e=True, append=assetType)

        for i in ['character', 'dress', 'module', 'prop', 'set']:
            if self.pipe_dir.split('/')[-1] in i:
                self.pipe_dir = os.path.abspath(os.path.join(self.getAssetsDirectory(), os.pardir))
                assetType = self.getAssetType(self.getAssetsDirectory())
                cmds.textScrollList('assetType', e=True, removeAll=True)
                cmds.textScrollList('assetType', e=True, append=assetType)
                cmds.textScrollList('assetType', e=True, selectItem=i)
                self.search()

    def getAssetType(self, pipeline_dir, *args):
        assetType = []
        if pipeline_dir:
            for asset_dir in os.listdir(pipeline_dir):
                if os.path.isdir(os.path.join(pipeline_dir, asset_dir)):
                    assetType.append(asset_dir)
        return assetType

    def selectedAssetType(self, *args):
        sel = cmds.textScrollList('assetType', q=True, si=True)
        if not sel:
            return
        
        return sel[0]

    def updateAssetsScrollList(self, *args):
        self.updateStepScrollList()
        assets = self.getAssets()
        cmds.textScrollList('assets', e=True, removeAll=True)
        cmds.textScrollList('assets', e=True, append=assets)
        cmds.symbolButton('assetsAddButton', e=True, ann=f'add {self.selectedAssetType()}')

    def getAssets(self, *args):
        assets = []
        assetType_dir = self.getAssetTypeDirectory()
        if assetType_dir:
            for assets_dir in os.listdir(assetType_dir):
                if os.path.isdir(os.path.join(assetType_dir, assets_dir)):
                    assets.append(assets_dir)
        return assets

    def selectedAssets(self, *args):
        sel = cmds.textScrollList('assets', q=True, si=True)
        if not sel:
            return
        
        return sel[0]

    def updateStepScrollList(self, *args):
        #steps = self.getWorkingStep()
        steps = ['modeling', 'lookdev', 'rig']
        cmds.textScrollList('steps', e=True, removeAll=True)
        cmds.textScrollList('steps', e=True, append=steps)

    def getWorkingStep(self, *args):
        steps = []
        asset_dir = self.getAssetDirectory()
        if asset_dir:
            for step_dir in os.listdir(asset_dir):
                if os.path.isdir(os.path.join(asset_dir, step_dir)):
                    steps.append(step_dir)
        return steps

    def selectedStep(self, *args):
        step = 'dressing'

        if self.selectedAssetType() != 'dress':
            step = cmds.textScrollList(self.stepScrollList, q=True, si=True)[0]

        return step

    def getProjectDirectory(self, *args):
        assetDir = self.getAssetDirectory()
        if not assetDir:
            return
        
        # print(os.path.normpath(os.path.join(assetDir, 'maya')))
        return os.path.normpath(os.path.join(assetDir, 'maya')).replace(os.sep, '/')


    def openLastEdit(self, *args):
        sceneUtility.saveScene()
        projectDir = self.getProjectDirectory().replace(os.sep, '/')

        #set project
        edit_dir = os.path.join(projectDir, 'scenes', 'edit', self.selectedStep()).replace(os.sep, '/')

        file_list = cmds.getFileList( folder=edit_dir, filespec='*.ma' )
        file_list.sort()

        #open file
        if file_list:
            filename = edit_dir+'/'+file_list[-1]
            try:
                sceneUtility.openScene(filename, projectDir)
                return
            except IOError as e:
                print(e)
            except RuntimeError as e:
                print(e)
            
            return
            

        #create new file
        cmds.file(f=True, new=True )
        print('import mode?', self.selectedStep(), not self.selectedStep() in ['modeling', 'dressing'])
        if not self.selectedStep() in ['modeling', 'dressing']:
            if not os.path.isdir(os.path.join(edit_dir, 'incrementalSave')):
                mode_file = os.path.join(projectDir, 'scenes', 'publish', 'modeling', f"{self.selectedAssets()}_publish_modeling.ma")
                cmds.file(mode_file, reference=True, ns=f"{self.selectedAssets()}_{self.selectedStep()}")

        if self.selectedStep() == 'lookdev':
            cmds.loadPlugin('mtoa')

        cmds.file(rename=os.path.join(edit_dir, f'{self.selectedAssets()}_edit_{self.selectedStep()}.ma'))
        cmds.file(f=True, type='mayaAscii', save=True )

        return
    
    def importObjFromRef(self, *args):
        refs = cmds.ls(rf = True)
        for ref in refs:
            rFile = cmds.referenceQuery(ref, f=True)
            cmds.file(rFile, importReference=True)
    
    def deleteNamespaces(self, *args):
        # Set root namespace
        cmds.namespace(setNamespace=':')
        # Collect all namespaces except for the Maya built ins.
        all_namespaces = [x for x in cmds.namespaceInfo(listOnlyNamespaces=True, recurse=True) if x != "UI" and x != "shared"]

        if all_namespaces:
            # Sort by hierarchy, deepest first.
            all_namespaces.sort(key=len, reverse=True)
            for namespace in all_namespaces:
                # When a deep namespace is removed, it also removes the root. So check here to see if these still exist.
                if cmds.namespace(exists=namespace) is True:
                    cmds.namespace(removeNamespace=namespace, mergeNamespaceWithRoot=True)
                    print("deleting", namespace)
    
    def importAsReference(self, *args):
        #cmds.file( save=True, type='mayaAscii' )
        cmds.file(os.path.join(self.getProjectDirectory(), 'scenes', 'publish', self.selectedStep(), f"{self.selectedAssets()}_publish_{self.selectedStep()}.ma"), reference=True, ns=f"{self.selectedAssets()}_{self.selectedStep()}")

    def addAsset(self, *args):
        if not self.selectedAssetType():
            return

        addAsset.addAssetUI(self.getAssetsDirectory(), self.selectedAssetType(), self)
        return
    
    def openDirectory(self, *args):
        dir = self.getProjectDirectory()
        if not dir:
            return
        
        os.popen(fr'explorer "{dir}"')