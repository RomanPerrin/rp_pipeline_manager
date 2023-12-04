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
import rfm2
from importlib import reload
from . import install

#files
from . import cache_manager_v1_20
from . import Ind_RenderMan_Utilities

icon_size = 35
row_size = 35

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

        master_lay = cmds.columnLayout(p=self.window, adjustableColumn=True)
        
        
        #file dialog
        pipe_dir_lay = cmds.rowLayout(p=master_lay, numberOfColumns=3, height=row_size, adjustableColumn=1)
        self.pipeline_dir = cmds.textField(p=pipe_dir_lay)
        cmds.symbolButton(p=pipe_dir_lay, ann='browse', i='fileOpen.png', height=icon_size, width=icon_size, command=partial(self.fileDialog, 2, "Pipeline directory"))
        
        
        #List asset type
        self.assetTypeScrollList = cmds.textScrollList('assetType', p=master_lay, numberOfRows=5, allowMultiSelection=False, selectCommand=self.search)
        
        #search field
        self.search_field = cmds.textField(p=master_lay, sf=1, tcc=self.search)
        
        #List assets
        assets_lay = cmds.formLayout(p=master_lay)
        assetsScrollList = cmds.textScrollList('assets', p=assets_lay, numberOfRows=5, allowMultiSelection=False, selectCommand=self.updateStepScrollList)
        assetsAddButton = cmds.symbolButton('assetsAddButton', p=assets_lay, ann=f'add asset', i='pickHandlesComp', height=icon_size, width=icon_size, command=self.addAsset)
        # Attach the assetsScrollList
        cmds.formLayout(assets_lay, e=True, attachForm=[(assetsScrollList, "left", 0), (assetsScrollList, "top", 0)])
        # Attach the assetsAddButton
        cmds.formLayout(assets_lay, e=True, attachForm=[(assetsAddButton, "right", 0), (assetsAddButton, "top", 0)])
        cmds.formLayout(assets_lay, e=True, attachControl=[(assetsScrollList, "right", 0, assetsAddButton)])
        
        
        #List working step
        self.stepScrollList = cmds.textScrollList('steps', p=master_lay, numberOfRows=3, allowMultiSelection=False)
        
        
        cmds.button(p=master_lay, label="open", command=self.openLastEdit)
        cmds.button(p=master_lay, label="publish", command=self.publish)
        cmds.button(p=master_lay, label="import as reference", command=self.importAsReference)
        
        try:
            self.pipe_dir = self.loadPipelineDirectory()
            cmds.textField(self.pipeline_dir, e=True, text=self.pipe_dir)
            self.getPipelineDirectory()
            self.getAssetsDirectory()
            self.updateAssetTypeScrollList()
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

    def openDirectory(self, *args):
        dir = os.path.normpath(self.pipe_dir)
        os.popen(fr'explorer "{dir}"')

    def fileDialog(self, fileMode, caption, *args):
        filename = cmds.fileDialog2(fileMode=fileMode, caption=caption)[0]
        cmds.textField(self.pipeline_dir, e=True, text=filename)
        self.savePipelineDirectory(filename)
        self.getPipelineDirectory()
        self.updateAssetTypeScrollList()
    
    def savePipelineDirectory(self, pipeline_dir, *args):
        with open(f"{os.path.dirname(__file__)}/data.json", "w") as file:
            json.dump(pipeline_dir, file)
    
    def loadPipelineDirectory(self, *args):
        with open(f"{os.path.dirname(__file__)}/data.json", "r") as file:
            return json.load(file)
    
    def getPipelineDirectory(self, *args):
        self.pipe_dir = cmds.textField(self.pipeline_dir, q=True, text=True)
        return cmds.textField(self.pipeline_dir, q=True, text=True)
    
    def getAssetsDirectory(self, *args):
        asset_dir = os.path.join(self.getPipelineDirectory(), '04_asset').replace(os.sep, '/')
        if not os.path.isdir(asset_dir):
            raise Exception('Assets folder name not found')
        
        return asset_dir
    
    def getAssetTypeDirectory(self, *args):
        return (os.path.join(self.getAssetsDirectory(), self.selectedAssetType())).replace(os.sep, '/')
    
    def getAssetDirectory(self, *args):
        return (os.path.join(self.getAssetTypeDirectory(), self.selectedAssets())).replace(os.sep, '/')
    
    def updateAssetTypeScrollList(self, *args):
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
        return cmds.textScrollList('assetType', q=True, si=True)[0]
    
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
        return cmds.textScrollList('assets', q=True, si=True)[0]
    
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
    
    def getWorkingDirectory(self, *args):
        print(os.path.normpath(os.path.join(self.getAssetDirectory(), 'maya')))
        return os.path.normpath(os.path.join(self.getAssetDirectory(), 'maya'))
    
    def openLastEdit(self, *args):
        saveScene()

        working_dir = self.getWorkingDirectory()
        working_dir = working_dir.replace(os.sep, '/')
        
        #cmds.unloadPlugin('rfm_volume_aggregate_set.py', force=True)
        #cmds.unloadPlugin('rfm_manipulators.py', force=True)
        #cmds.unloadPlugin('rfm.py', force=True)
        
        #set project
        mel.eval(f'setProject "{working_dir}"')
        edit_dir = os.path.join(working_dir, 'scenes', 'edit', self.selectedStep()).replace(os.sep, '/')
        
        file_list = cmds.getFileList( folder=edit_dir, filespec='*.ma' )
        file_list.sort()
        
        #create new file
        if file_list:
            opened_file = cmds.file( edit_dir+'/'+file_list[-1], open=True , force=True)
            return
        
        cmds.file(f=True, new=True )
        print('import mode?', self.selectedStep(), not self.selectedStep() in ['modeling', 'dressing'])
        if not self.selectedStep() in ['modeling', 'dressing']:
            if not os.path.isdir(os.path.join(edit_dir, 'incrementalSave')):
                cmds.file(os.path.join(working_dir, 'scenes', 'publish', 'modeling', f"{self.selectedAssets()}_publish_modeling.ma"), reference=True, ns=f"{self.selectedAssets()}_{self.selectedStep()}")
        
        if self.selectedStep() == 'lookdev':
            cmds.loadPlugin('RenderMan_for_Maya.py')
            self.addRmanUserToken()
            self.assignPxrSurf()
        
        cmds.file(rename=os.path.join(edit_dir, f'{self.selectedAssets()}_edit_{self.selectedStep()}.ma'))
        cmds.file(f=True, type='mayaAscii', save=True )
        
        return
    
    def publish(self, *args):
        selection_export = cmds.ls(sl=1)
        if not selection_export:
            dismissed = cmds.framelessDialog( title='Publish error', message='No selection found', 
                    path='please select an item and try again', button=['OK'], primary=['OK'])
            return
        current_scene = cmds.file(q=1, sn=1)
        file_name = os.path.join(self.getWorkingDirectory(), "scenes", "publish", self.selectedStep(), f"{self.selectedAssets()}_publish_{self.selectedStep()}")

        saveScene()
        
        try:
            print("importing object from reference")
            self.importObjFromRef()
            
            print("deactivating smooth preview")
            cmds.displaySmoothness(polygonObject=0)

            if self.selectedStep() == 'modeling':
                print('fixing non-manifold')
                cmds.delete(cmds.polyInfo(nmv=1, nuv=1, nue=1, nme=1))
                print('fixing lamina faces')
                cmds.delete(cmds.polyInfo(lf=1))
                cmds.makeIdentity(a=1)
                cmds.DeleteHistory(cmds.ls())
                cmds.makeIdentity(t=1, r=1, s=1)
                cmds.polyClean()

                sel = cmds.ls(geometry=True)
                if self.selectedAssetType() == 'prop':
                    print('creating set geo cache')
                    cmds.sets(cmds.listRelatives(sel, p=1), n=f'set_geo_cache {self.selectedAssets()}')

                cmds.unloadPlugin('RenderMan_for_Maya.py', force=True)
                print('assigning Lambert')
                for i in sel:
                    cmds.select(i, r=True)
                    cmds.hyperShade(assign='lambert1')
                
                print("renaming shapes")
                cache_manager_v1_20.rename_meshes(force=True, message=False)

            print("deleting volume aggregate")
            self.deleteVolumAggregate()

            print("deleting unsused nodes")
            unknownNodes = cmds.ls(typ=('unknown','unknownDag'))
            print(unknownNodes)
            for node in unknownNodes:
                try:
                    cmds.lockNode(node,l=False)
                    cmds.delete(node)
                except:
                    print('Problem deleting unknown node "'+node+'"!')

            print('deleting unused shading nodes')
            self.deleteUnusedShadingNodes()
        
            print('deleting display layers')
            self.deleteDisplayLayers()

            print('deleting empty sets')
            self.deleteEmptySets()

            print('deleting render layer')
            self.deleteRenderLayers()

            print("remove unused plugins")
            self.deleteUnusedPlugins()

            print("deleting namespaces")
            self.deleteNamespaces()

            if self.selectedStep() != 'rig':
                print("deleting intermediate shapes")
                all_meshes = cmds.ls( type="mesh", ap=True )
                no_intermediate_meshes = cmds.ls( type="mesh", ap=True, noIntermediate=True )
                for shape in list(set(all_meshes)-set(no_intermediate_meshes)):
                    cmds.delete(shape)
                    print("deleting", shape, "namespace")

            cmds.select(selection_export)
            cmds.file(file_name, force = True, options = "v=0", type = "mayaAscii", shader = True, constructionHistory = True, exportSelected = True) 
            print("publish scene saved")

            # cmds.file(rename=file_name)
            # cmds.file(save=True, type='mayaAscii')
        
        except Exception as error:
            cmds.error("error during publish", error)
        
        cmds.file(current_scene, open=True , force=True)
    
    def deleteUnusedShadingNodes(self):
        '''
        Delete all unused shading nodes in the scene
        '''
        #texList = mc.ls(tex=True)
        #if texList: mc.delete(texList)
        mel.eval('MLdeleteUnused')

    def deleteDisplayLayers(self):
        '''
        Delete all display layers
        '''
        # Get display layer list
        displayLayers = cmds.ls(type='displayLayer')
        displayLayers.remove('defaultLayer')

        # Delete display layers
        if displayLayers:
            print(displayLayers)
            cmds.delete(displayLayers)

        # Return result
        return displayLayers

    def deleteRenderLayers(self):
        '''
        Delete all render layers
        '''
        # Get render layer list
        renderLayers = cmds.ls(typ='renderLayer')
        renderLayers.remove('defaultRenderLayer')
    
	    # Delete render layers
        if renderLayers: 
            print(renderLayers)
            cmds.delete(renderLayers)
    
	    # Return result
        return renderLayers

    def deleteVolumAggregate(*arg):
        thoseDamnRMNodes = cmds.ls(type="rmanVolumeAggregateSet",l=True, ap=True)
        nbShit=len(thoseDamnRMNodes)
        print(thoseDamnRMNodes)
    
        if nbShit>0:
            for each_damnRMNode in thoseDamnRMNodes:
                cmds.lockNode(each_damnRMNode, lock=False)
                cmds.delete(each_damnRMNode)

    def deleteEmptySets(self, setList=[]):
        '''
        Delete empty object sets
        @param setList: A list of sets to check. If empty, checks all sets in current scene.
        @type setList: list
        '''
        # Check setList
        if not setList: setList = cmds.ls(sets=True)
    
        # Check empty sets
        emptySetList = []
        for set in setList:
            if not cmds.sets(set,q=True):
                emptySetList.append(set)

        # Removing Mash network from the deletion list
        for mash in cmds.ls(type="MASH_Waiter"):
            emptySetList.remove(mash)

        # Delete empty sets
        for emptySet in emptySetList:
            try:
                cmds.delete(emptySet)
                print(emptySet)
            except: print("error during", emptySet, "deletion")
    
        # Return result
        return emptySetList

    def deleteUnusedPlugins(*args):
        # Find and remove unknown plugins
        unknown_plugins = cmds.unknownPlugin(query=True, list=True)

        if not unknown_plugins:
            print("no unused plugins")
            return
        
        for plugin in unknown_plugins:
            try:
                cmds.unknownPlugin(plugin, remove=True)
                print("removing", plugin)
            except Exception as error:
                # Oddly enough, even if a plugin is unknown, it can still have a dependency in the scene.
                # So in this case, we log the error to look at after.
                cmds.warning("Unknown plugin cannot be removed due to ERROR: {}".format(error))

    def importObjFromRef(*args):
        refs = cmds.ls(rf = True)
        for ref in refs:
            rFile = cmds.referenceQuery(ref, f=True)
            cmds.file(rFile, importReference=True)

    def deleteNamespaces(*args):
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
        cmds.file(os.path.join(self.getWorkingDirectory(), 'scenes', 'publish', self.selectedStep(), f"{self.selectedAssets()}_publish_{self.selectedStep()}.ma"), reference=True, ns=f"{self.selectedAssets()}_{self.selectedStep()}")
        self.addRmanUserToken()
    
    def addRmanUserToken(self, *args):
        if self.getWorkingStep() == 'lookdev':
            cmds.loadPlugin('RenderMan_for_Maya.py')
            createRmanUserToken('0', 'pipeline', self.getAssetDirectory(), 'string')
    
    def addAsset(self, *args):
        if not self.selectedAssetType():
            return
        
        addAssetUI(self.getAssetsDirectory(), self.selectedAssetType(), self)
        return
    
    def rendermanAssign(self, shaderName, selection_list, texture_dir):
        # creer un shader
        myShader = cmds.shadingNode('PxrSurface', asShader=True, name=shaderName + "_Mtl")
    
        # creer un shading group
        myShaderSG = cmds.sets(renderable=True, noSurfaceShader=True, empty=True, name=myShader + "SG")
    
        # shader to shading group
        cmds.connectAttr('%s.outColor' % myShader, '%s.surfaceShader' % myShaderSG)
    
        # connect the nodes
        """ALBEDO NODES"""
        remap = cmds.shadingNode('PxrRemap', name='remap_albedo_' + shaderName, asTexture=True)
        hsl = cmds.shadingNode('PxrHSL', name='HSL_albedo_' + shaderName, asTexture=True)
        cc = cmds.shadingNode('PxrColorCorrect', name='color_correct_albedo_' + shaderName, asTexture=True)
        pxrtexture = cmds.shadingNode('PxrTexture', name='albedo_' + shaderName, asTexture=True)
    
        """SPECULAR NODES"""
        remap_spec = cmds.shadingNode('PxrRemap', name='remap_specular_' + shaderName, asTexture=True)
        hsl_spec = cmds.shadingNode('PxrHSL', name='HSL_specular_' + shaderName, asTexture=True)
        cc_spec = cmds.shadingNode('PxrColorCorrect', name='color_correct_specular_' + shaderName, asTexture=True)
        pxrtexture_spec = cmds.shadingNode('PxrTexture', name='specular_' + shaderName, asTexture=True)
    
        """ROUGHNESS NODES"""
        remap_roughness = cmds.shadingNode('PxrRemap', name='remap_roughess_' + shaderName, asTexture=True)
        hsl_roughness = cmds.shadingNode('PxrHSL', name='HSL_roughness_' + shaderName, asTexture=True)
        cc_roughness = cmds.shadingNode('PxrColorCorrect', name='color_correct_roughness_' + shaderName, asTexture=True)
        pxrtexture_roughness = cmds.shadingNode('PxrTexture', name='roughness_' + shaderName, asTexture=True)
    
        """BUMP AND NORMAL MAP NODES"""
        remap_bump_normal = cmds.shadingNode('PxrRemap', name='remap_bump_normal_' + shaderName, asTexture=True)
        pxrtexture_bump = cmds.shadingNode('PxrTexture', name='bump_normal_' + shaderName, asTexture=True)
        bump = cmds.shadingNode('PxrBump', name='bump_' + shaderName, asTexture=True)
    
        """DISPLACEMENT NODES"""
        displace = cmds.shadingNode('PxrDisplace', name='disp_' + shaderName, asShader=True)
        dispTransform = cmds.shadingNode('PxrDispTransform', name='dispTransform_' + shaderName, asTexture=True)
        pxrtexture_disp = cmds.shadingNode('PxrTexture', name='displacement_' + shaderName, asTexture=True)
    
        """ALBEDO"""
        cmds.connectAttr('%s.resultRGB' % remap, '%s.diffuseColor' % myShader)
        cmds.connectAttr('%s.resultRGB' % hsl, '%s.inputRGB' % remap)
        cmds.connectAttr('%s.resultRGB' % cc, '%s.inputRGB' % hsl)
        cmds.connectAttr('%s.resultRGB' % pxrtexture, '%s.inputRGB' % cc)
    
        """SPECULAR"""
        cmds.connectAttr('%s.resultRGB' % remap_spec, '%s.specularFaceColor' % myShader)
        cmds.connectAttr('%s.resultRGB' % hsl_spec, '%s.inputRGB' % remap_spec)
        cmds.connectAttr('%s.resultRGB' % cc_spec, '%s.inputRGB' % hsl_spec)
        cmds.connectAttr('%s.resultRGB' % pxrtexture_spec, '%s.inputRGB' % cc_spec)
    
        """ROUGHNESS"""
        cmds.connectAttr('%s.resultR' % remap_roughness, '%s.specularRoughness' % myShader)
        cmds.connectAttr('%s.resultRGB' % hsl_roughness, '%s.inputRGB' % remap_roughness)
        cmds.connectAttr('%s.resultRGB' % cc_roughness, '%s.inputRGB' % hsl_roughness)
        cmds.connectAttr('%s.resultRGB' % pxrtexture_roughness, '%s.inputRGB' % cc_roughness)
    
        """BUMP NORMAL"""
        cmds.connectAttr('%s.resultRGB' % pxrtexture_bump, '%s.inputRGB' % remap_bump_normal)
        cmds.connectAttr('%s.resultR' % remap_bump_normal, '%s.inputBump' % bump)
        cmds.connectAttr('%s.resultN' % bump, '%s.bumpNormal' % myShader)
    
        """DISPLACEMENT"""
        cmds.connectAttr('%s.resultR' % pxrtexture_disp, '%s.dispScalar' % dispTransform)
        cmds.connectAttr('%s.resultF' % dispTransform, '%s.dispScalar' % displace)
        cmds.connectAttr('%s.outColor' % displace, '%s.displacementShader' % myShaderSG)
    
        # PxrTexture attributes
        cmds.setAttr(pxrtexture + ".atlasStyle", 1)
        cmds.setAttr(pxrtexture + ".linearize", 1)
    
        # Specular attributes
        cmds.setAttr(pxrtexture_spec + ".atlasStyle", 1)
    
        # Roughness attributes
        cmds.setAttr(pxrtexture_roughness + ".atlasStyle", 1)
    
        # Bump and normal attributes
        cmds.setAttr(pxrtexture_bump + ".atlasStyle", 1)
    
        # Displacement attributes
        cmds.setAttr(pxrtexture_disp + ".atlasStyle", 1)
        cmds.setAttr(dispTransform + ".dispRemapMode", 2)
    
        # assign le shader a la selection
        for o in mySelectionList:
            cmds.sets(o, e=True, forceElement=myShaderSG)
    
        print('Renderman Shader assigned to object successfully')
    
    def assignPxrSurf(self, *args):
        print('assign')
        sel = cmds.ls(geometry=True)
        print(sel)
        for i in sel:
            self.rendermanAssign(f'PxrSurf_{i}', i, os.path.join(self.getWorkingDirectory(), 'sourceimages'))


class addAssetUI():
    def __init__(self, pipeline_dir, assets_dir, obj, *args):
        self.pipeline_dir = pipeline_dir
        self.assets_dir = assets_dir
        self.obj = obj
        self.UI()
    
    def UI(self, *args):
        size = (300, 50)
        
        self.window = f"Add {self.assets_dir}"
        if cmds.window(self.window, q=True,exists=True):
            cmds.deleteUI(self.window)
        self.window = cmds.window(self.window, wh=size, minimizeButton=False, maximizeButton=False)
        
        master_lay = cmds.rowLayout(numberOfColumns=3, height=row_size, adjustableColumn=2)
        cmds.text(label=f'name of the new {self.assets_dir}')
        self.asset_name = cmds.textField(p=master_lay, enterCommand=self.addAsset)
        cmds.button(p=master_lay, label='Create', command=self.addAsset)
        
        cmds.showWindow(self.window)
    
    def addAsset(self, *args):
        assetName = cmds.textField(self.asset_name, q=True, text=True)
        asset_dir = os.path.join(self.pipeline_dir, self.assets_dir, assetName, 'maya')
        asset_dir = asset_dir.replace(os.sep, '/')
        os.makedirs(asset_dir, exist_ok=True)
        
        os.makedirs(os.path.join(self.pipeline_dir, self.assets_dir, assetName, 'paint_2D'), exist_ok=True)
        os.makedirs(os.path.join(self.pipeline_dir, self.assets_dir, assetName, 'paint_3D'), exist_ok=True)
        os.makedirs(os.path.join(self.pipeline_dir, self.assets_dir, assetName, 'sculpt'), exist_ok=True)
        os.makedirs(os.path.join(self.pipeline_dir, self.assets_dir, assetName, 'houdini'), exist_ok=True)
        self.createProject(os.path.join(asset_dir))
        
        print(f'{self.assets_dir} created at {asset_dir}')
        cmds.deleteUI(self.window)
        self.obj.search()
        cmds.textScrollList('assets', e=True, si=assetName)
        return
    
    def createProject(self, project_dir, *args):
        os.makedirs(os.path.join(project_dir, 'cache', 'bifrost'), exist_ok=True)
        os.makedirs(os.path.join(project_dir, 'cache', 'nCache', 'fluid'), exist_ok=True)
        os.makedirs(os.path.join(project_dir, 'cache', 'particles'), exist_ok=True)
        os.makedirs(os.path.join(project_dir, 'data'), exist_ok=True)
        os.makedirs(os.path.join(project_dir, 'images'), exist_ok=True)
        os.makedirs(os.path.join(project_dir, 'movies'), exist_ok=True)
        os.makedirs(os.path.join(project_dir, 'scenes', 'edit', 'assetLayout'), exist_ok=True)
        os.makedirs(os.path.join(project_dir, 'scenes', 'edit', 'cloth'), exist_ok=True)
        os.makedirs(os.path.join(project_dir, 'scenes', 'edit', 'dressing'), exist_ok=True)
        os.makedirs(os.path.join(project_dir, 'scenes', 'edit', 'groom'), exist_ok=True)
        os.makedirs(os.path.join(project_dir, 'scenes', 'edit', 'lookdev'), exist_ok=True)
        os.makedirs(os.path.join(project_dir, 'scenes', 'edit', 'modeling'), exist_ok=True)
        os.makedirs(os.path.join(project_dir, 'scenes', 'edit', 'rig'), exist_ok=True)
        os.makedirs(os.path.join(project_dir, 'scenes', 'publish', 'assetLayout'), exist_ok=True)
        os.makedirs(os.path.join(project_dir, 'scenes', 'publish', 'cloth'), exist_ok=True)
        os.makedirs(os.path.join(project_dir, 'scenes', 'publish', 'dressing'), exist_ok=True)
        os.makedirs(os.path.join(project_dir, 'scenes', 'publish', 'groom'), exist_ok=True)
        os.makedirs(os.path.join(project_dir, 'scenes', 'publish', 'lightRig'), exist_ok=True)
        os.makedirs(os.path.join(project_dir, 'scenes', 'publish', 'lookdev'), exist_ok=True)
        os.makedirs(os.path.join(project_dir, 'scenes', 'publish', 'modeling'), exist_ok=True)
        os.makedirs(os.path.join(project_dir, 'scenes', 'publish', 'rig'), exist_ok=True)
        os.makedirs(os.path.join(project_dir, 'scenes', 'publish', 'shader'), exist_ok=True)
        os.makedirs(os.path.join(project_dir, 'sound'), exist_ok=True)
        os.makedirs(os.path.join(project_dir, 'sourceimages'), exist_ok=True)
        
        source = os.path.join(os.path.dirname(__file__), 'workspace.mel')
        source = source.replace(os.sep, '/')
        destination = os.path.join(project_dir, 'workspace.mel')
        destination = destination.replace(os.sep, '/')
        shutil.copy(source, destination)
        
        return
