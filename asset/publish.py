# coding : utf-8
__author__ = 'Roman PERRIN'
#Author: Roman PERRIN

#Libraries
from fileinput import filename
import maya.cmds as cmds
import maya.mel as mel
import os

#files
from .. import cache_manager_v1_20

def publish(self, *args):
    selection_export = cmds.ls(sl=1)
    if not selection_export:
        dismissed = cmds.framelessDialog( title='Publish error', message='No selection found', 
                path='please select an item and try again', button=['OK'], primary=['OK'])
        return
    current_scene = cmds.file(q=1, sn=1)
    os.path.dirname(self.opened_scene)
    step = os.path.dirname(self.opened_scene).split('/')[-1]
    dir =  os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(self.opened_scene)))))
    asset = dir.split('/')[-1]
    file_name = os.path.join(dir, "scenes", "publish", step, f"{asset}_publish_{step}")
    print(file_name)
    #saves scene
    if cmds.file(q=True, sceneName=True):
        cmds.file(f=True, type='mayaAscii', save=True)
    
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
            # cmds.unloadPlugin('RenderMan_for_Maya.py', force=True)
            # print('assigning Lambert')
            # for i in sel:
                # cmds.select(i, r=True)
                # cmds.hyperShade(assign='lambert1')
            
            print("renaming shapes")
            cache_manager_v1_20.rename_meshes(force=True, message=False)
        print("deleting volume aggregate")
        deleteVolumAggregate()
        print("deleting unsused nodes")
        unknownNodes = cmds.ls(typ=('unknown','unknownDag'))
        print(unknownNodes)
        for node in unknownNodes:
            try:
                cmds.lockNode(node,l=False)
                cmds.delete(node)
            except:
                print('Problem deleting unknown node "'+node+'"!')
        # print('deleting unused shading nodes')
        # deleteUnusedShadingNodes()
    
        print('deleting display layers')
        deleteDisplayLayers()
        print('deleting empty sets')
        deleteEmptySets()
        print('deleting render layer')
        deleteRenderLayers()
        print("remove unused plugins")
        deleteUnusedPlugins()
        print("deleting namespaces")
        deleteNamespaces()
        if self.selectedStep() != 'rig':
            print("deleting intermediate shapes")
            all_meshes = cmds.ls( type="mesh", ap=True )
            no_intermediate_meshes = cmds.ls( type="mesh", ap=True, noIntermediate=True )
            for shape in list(set(all_meshes)-set(no_intermediate_meshes)):
                cmds.delete(shape)
                print("deleting", shape, "intermediate")
    	
        selection_export = [obj.split(':')[-1] for obj in selection_export]
        sel = cmds.ls(selection_export, dag=1, l=1)
        shadingGrps:List = cmds.listConnections(sel ,type='shadingEngine')
        if not shadingGrps:
            shadingGrps = []
        shaders = cmds.ls(cmds.listConnections(shadingGrps),materials=1)
        if not shaders:
            shaders = []
        print(shaders + shadingGrps + sel)
        cmds.select(shaders + shadingGrps + sel, noExpand=True)
        cmds.file(file_name, force = True, options = "v=0", type = "mayaAscii", shader = True, constructionHistory = True, exportSelected = True) 
        print("publish scene saved")
    
    except Exception as error:
        cmds.error("error during publish", error)
    
    cmds.file(current_scene, open=True , force=True)


def deleteUnusedShadingNodes(*args):
    '''
    Delete all unused shading nodes in the scene
    '''
    #texList = mc.ls(tex=True)
    #if texList: mc.delete(texList)
    mel.eval('MLdeleteUnused')

def deleteDisplayLayers(*args):
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

def deleteRenderLayers(*args):
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

def deleteVolumAggregate(*args):
    thoseDamnRMNodes = cmds.ls(type="rmanVolumeAggregateSet",l=True, ap=True)
    nbShit=len(thoseDamnRMNodes)
    print(thoseDamnRMNodes)

    if nbShit>0:
        for each_damnRMNode in thoseDamnRMNodes:
            cmds.lockNode(each_damnRMNode, lock=False)
            cmds.delete(each_damnRMNode)

def deleteEmptySets(setList=[], *args):
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