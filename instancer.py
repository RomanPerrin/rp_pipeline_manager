# coding : utf-8

# Maya's Libraries
import maya.cmds as cmds
import maya.mel as mel

# Python's Libraries

# Globales Variables

def filter_sel( sel=[], filters_type=[], filters_prefix=[], filters_suffix=[] ):
    if not sel:
        sel = cmds.ls( sl=True, ap=True, fl=True )
    elif type(sel) is not list:
        sel = [sel]
        
    if filters_type:
        if type( filters_type ) is not list:
            filters_type = [filters_type]
        new_sel = []
        for obj in sel:
            obj_type = cmds.objectType(obj)
            for filter_type in filters_type:
                if obj_type == filter_type:
                    new_sel.append( obj )
        sel = new_sel[:]
                
    if filters_prefix:
        if type( filters_prefix ) is not list:
            filters_prefix = [filters_prefix]
        new_sel = []
        for obj in sel:
            for filter_prefix in filters_prefix:
                if obj.startswith( filter_prefix ):
                    new_sel.append( obj )
        sel = new_sel[:]
        
    if filters_suffix:
        if type( filters_suffix ) is not list:
            filters_suffix = [filters_suffix]
        new_sel = []
        for obj in sel:
            for filter_suffix in filters_suffix:
                if obj.startswith( filter_suffix ):
                    new_sel.append( obj )
        sel = new_sel[:]

    return sel

def filter_shapes_and_transforms( sel=[] ):
    sel = filter_sel( sel )
    shapes = []
    transforms = []
    for i in range(len( sel ) ):
        obj = sel[i]
        obj_type = cmds.objectType( obj )
        if obj_type in ["objectSet"]: # Filter types wich aren't shapes
            continue
        if obj_type in ["transform", "joint"]:
            if i == 0:
                obj_shapes = cmds.listRelatives( obj, shapes=True, path=True )
                if obj_shapes:
                    shapes += obj_shapes
            else:
                transforms.append( obj )
        else:
            shapes.append( obj )
            
    if not shapes:
        cmds.error( "Have to select at least one transform with shapes or one or several shapes" )
    elif not transforms:
        cmds.error( "Have to select at least one transform to instance your shapes on" )
            
    return shapes, transforms

def filter_shapes( sel=[] ):
    sel = filter_sel( sel )
    shapes = []
    for obj in sel:
        obj_type = cmds.objectType( obj )
        if obj_type in ["objectSet"]:
            continue
        if obj_type in ["transform", "joint"]:
            obj_shapes = cmds.listRelatives( obj, s=True, path=True )
            if obj_shapes:
                shapes += obj_shapes
        else:
            shapes.append( obj )
    return shapes

def instance_shapes( sel=[] ):
    """
    """
    shapes, transforms = filter_shapes_and_transforms( sel )
    for transform in transforms:
        try:
            cmds.parent( shapes, transform, addObject=True, shape=True )
        except:
            pass

def uninstance_shapes( sel=[] ):
    shapes = filter_shapes( sel )
    for shape in shapes:
        cmds.parent( shape, removeObject=True, s=True )

def delete_shapes( sel=[] ):
    """
    """
    shapes = filter_shapes( sel )
    cmds.delete( shapes )

def autoInstance(*args):
    referenceNodeList = cmds.ls(rf=1)
    filenameList = []
    
    for referenceNode in referenceNodeList:
        dict = {}
        dict['refNode'] = referenceNode
        dict['filename'] = cmds.referenceQuery(referenceNode, f=1)
        
        children = []
        nodes = cmds.referenceQuery(referenceNode, nodes=1)
        nodes = [node for node in nodes if cmds.nodeType(node) == 'mesh']
        
        #for node in nodes:
        #    children.extend(cmds.listRelatives(node, ad=1))
        #nodes = [node for node in nodes if node not in children]
        dict['node'] = nodes
        
        filenameList.append(dict)
    
    ref = []
    toInstance = []
    for dict in filenameList:
        if "{" in dict['filename']:
            toInstance.append(dict)
        else:
            ref.append(dict)
    
    print(ref)
    print(toInstance)
    
    for i in range(len(toInstance)):
        for j in range(len(ref)):
            if toInstance[i]['filename'].split('{')[0] == ref[j]['filename']:
                toInstance[i]['source'] = ref[j]['node']
    
    print(toInstance)
    
    for i in range(len(toInstance)):
        shapeParent = [cmds.listRelatives(node, p=1, pa=1)[0] for node in toInstance[i]['node']]
        cmds.file(toInstance[i]['filename'], importReference=True)
        for j in range(len(shapeParent)):
            delete_shapes(toInstance[i]['node'][j])
            instance_shapes([toInstance[i]['source'][j], shapeParent[j]])