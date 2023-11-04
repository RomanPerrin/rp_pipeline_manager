# coding:utf-8

# Maya's Libs
import maya.cmds as cmds

# RenderMan Libs
import rfm2

# Python built-ins Libs
import pprint

def swap_refs_ribs( sel=[] ):
    # Variables
    if not sel:
        sel = cmds.ls( sl=True, type="transform", ap=True )
    else:
        sel = cmds.ls( sel, type="transform", ap=True )
    
    # Listing
    ribs = cmds.ls( type="RenderManArchive", ap=True )
    infos_ribs = {}
    for rib in ribs:
        rib_tr = cmds.listRelatives( rib, parent=True, path=True)[-1]
        infos_ribs[rib_tr] = {}
        infos_ribs[rib_tr]['rib'] = rib
        infos_ribs[rib_tr]['rib_file'] = cmds.getAttr( rib+".filename", asString=True )
        infos_ribs[rib_tr]['rib_filename'] = infos_ribs[rib_tr]['rib_file'].split(".")[0]

    refs = cmds.ls( type="reference", ap=True )
    infos_refs = {}
    for ref in refs:
        ns = cmds.referenceQuery( ref, namespace=True ).replace(":","",1)
        infos_refs[ns] = {}
        infos_refs[ns]['ref_node'] = ref
        infos_refs[ns]['ref_file'] = cmds.referenceQuery( ref, filename=True )
        infos_refs[ns]['ref_filename'] = infos_refs[ns]['ref_file'].split(".")[0]

    pprint.pprint( infos_ribs, indent=4 )
    pprint.pprint( infos_refs, indent=4 )

    # SWAP
    ribs_selected = []
    refs_selected = []
    for obj in sel:
        rmas_nodes = cmds.listRelatives( obj, s=True, type="RenderManArchive", path=True )
        coords = cmds.xform( obj, q=True, ws=True, matrix=True )
        parents = cmds.listRelatives( obj, p=True, path=True )
        if rmas_nodes:
            ribs_selected.append( obj )
            # Ref Instead
            obj_name = infos_ribs[obj]['rib_filename'].split("/")[-1]
            ref_node = cmds.file( infos_ribs[obj]['rib_filename']+".ma", deferReference=False, r=True, usingNamespaces=True, namespace=obj_name )
            #ref_node = cmds.referenceQuery( ref, referenceNode=True )
            ns = cmds.referenceQuery( ref_node, namespace=True ).replace(":","")
            top_nodes = cmds.ls( ns+":*", type="transform", ap=True, assemblies=True )
            cmds.xform( top_nodes, ws=True, matrix=coords )
            cmds.delete( obj )
            if parents:
                cmds.parent( top_nodes, parents[0] )
        else:
            nss = obj.split("|")[-1].split(":")
            if len(nss)>1:
                ns = nss[-2]
                if ns in infos_refs:
                    refs_selected.append( ns )
                    # Rib Instead
                    obj_name = infos_refs[ns]['ref_filename'].split("/")[-1]
                    rfm2.api.nodes.import_archive( infos_refs[ns]['ref_filename'] )
                    rib_node = cmds.ls( sl=True, ap=True )
                    tr_rib = cmds.listRelatives( rib_node, p=True, path=True )[-1]
                    # Remove Ref
                    cmds.file( infos_refs[ns]['ref_file'], removeReference=True )
                    
                    # Cleaning/Organization
                    cmds.xform( tr_rib, ws=True, matrix=coords )
                    if parents:
                        cmds.parent( tr_rib, parents[0] )
                        
def get_sn(obj):
    return obj.split("|")[-1].split(":")[-1].split(".")[0]

def filter_sel( sel=[] ):
    if not sel:
        sel = cmds.ls( sl=True, ap=True )
        if not sel:
            return None
    elif type(sel) is not list:
        sel = [sel]
    return sel

def get_SGs( sel=[] ):
    sel = filter_sel( sel )
    SGs = []
    for obj in sel:
        SG = ""
        obj_type = cmds.objectType( obj )
        if obj_type == "shadingEngine":
            SGs.append( obj )
        elif obj_type == "transform":
            meshes = cmds.listRelatives( obj, s=True, type="mesh", path=True, noIntermediate=True )
            if meshes:
                for mesh in meshes:
                    cos_SGs = cmds.listConnections( mesh, type="shadingEngine" )
                    if cos_SGs:
                        SGs += cos_SGs
    return list(set(SGs))

def convert_lambert_to_pxrSurface( sel=[] ):
    """
    Works only with connected nodes, not with attributes
    """
    # Variables
    sel = filter_sel( sel )
    
    # Filtering
    datas = {}
    for obj in sel:
        SGs = get_SGs( obj )
        for SG in SGs:
            SG_name = get_sn( SG )
            name = SG_name.replace("SG","")
            cos_HS = cmds.listConnections( SG+".surfaceShader" )
            if cos_HS:
                for shader in cos_HS:
                    shader_type = cmds.objectType( shader )
                    if shader_type == "phong":
                        pxr_shader = cmds.createNode( "PxrSurface", n=f"PxrSurface_{name}", ss=True )
                        cmds.connectAttr( pxr_shader+".outColor", SG+".rman__surface" )
                        cos_shader = cmds.listConnections( shader, destination=False, connections=True, plugs=True, skipConversionNodes=True )
                        if cos_shader:
                            cos_shader = dict( zip( cos_shader[1::2], cos_shader[0::2] ) )
                            for co in cos_shader:
                                co_node = co.split(".")[0]
                                co_node_type = cmds.objectType( co_node )
                                co_attr = cos_shader[co].split(".")[-1]
                                if co_attr == "color":
                                    cmds.connectAttr( co, pxr_shader+".diffuseColor" )
                                elif co_attr == "transparency":
                                    cmds.connectAttr( co_node+".outColorR", pxr_shader+".presence" )
                                elif co_attr == "normalCamera":
                                    pxr_normal = cmds.createNode( "PxrNormalMap", n=f"PxrNormalMap_{name}", ss=True )
                                    if co_node_type == "bump2d":
                                        cos_bump = cmds.listConnections( co_node+".bumpValue" )
                                        if cos_bump:
                                            file_path = cmds.getAttr( cos_bump[0]+".fileTextureName", asString=True )
                                            cmds.setAttr( pxr_normal+".filename", file_path, type="string" )
                                    cmds.connectAttr( pxr_normal+".resultN", pxr_shader+".bumpNormal" )
                                
        
        