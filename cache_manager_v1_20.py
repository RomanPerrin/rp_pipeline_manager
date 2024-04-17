# coding : utf-8

# Maya's Librairies
import maya.cmds as cmds
import maya.OpenMaya as om

# Python's Librairies
from functools import partial

# Global Variables
__author__ = { 'author':'Aymeric GESSE', "webSite":"https://aymericgesse.fr", "email":"aymeric.gesse@gmail.com" }
__version__ = 1.20
__license__ = 'CC BY-NC-SA 4.0'

_window_ = {}
_window_['name'] = "ESMA_CachingManager"
_window_['title'] = f"ESMA Caching Manager v.{__version__}"

_names_ = {}
_names_['geometry_displayed'] = "{tr_geometry_sn}ShapeABCReady"
_names_['geometry_intermediate'] = "{tr_geometry_sn}Shape"
_names_['geo_cache'] = "set_geocache"

# Functions
def get_sn( obj, *args ):
    return obj.split("|")[-1].split(":")[-1] # Get SN

def get_parent( obj, *args ):
    return cmds.listRelatives( obj, p=True, path=True )[0]
    
def get_om_dag_node( fullPath ):
	"""
	"""
	if not cmds.objExists(fullPath):
		return None
	else:
		selectionList = om.MSelectionList()
		selectionList.add( fullPath )
		dagPath = om.MDagPath()
		selectionList.getDagPath( 0, dagPath )
		return dagPath	

def get_other_instances( sel=[] ):
    sel = get_sel( sel )
    return cmds.ls( sel, ap=True )[1:]

def get_sel( sel=[] ):
    if not sel:
        sel = cmds.ls( selection=True, allPaths=True )
    sel = filter_list( sel )
    return sel

def is_shape( obj=""):
    return "shape" in cmds.nodeType( obj, inherited=True )
    
def is_shape_holder( obj ):
    return "dagNode" in cmds.nodeType( obj, inherited=True )

def is_instance( obj='' ):
	"""
	Return True or False if input is an instance
	"""
	dag_node = get_om_dag_node(obj)
	return dag_node.isInstanced()

def filter_list( input_list=[] ):
    if not isinstance( input_list, (list, tuple) ):
        input_list = [input_list]
    return input_list

def filter_sel( sel=[], filter_types=[], filter_prefix=[], filter_suffix=[], filter_instances=False, *args ):
    sel = get_sel( sel )
    filter_prefix = filter_list( filter_prefix )
    filter_suffix = filter_list( filter_suffix )
        
    # Filtering
    if filter_types or filter_prefix or filter_suffix:
        new_sel = []
        for obj in sel:
            if filter_types:
                obj_type = cmds.objectType( obj )
                if obj_type in filter_types:
                    new_sel.append( obj )
                    continue
            if filter_prefix or filter_suffix:
                obj_sn = get_sn( obj )
                if filter_prefix:
                    if obj_sn.split("_")[0] in filter_prefix:
                        new_sel.append( obj )
                        continue
                if filter_suffix:
                    if obj_sn.split("_")[-1] in filter_suffix:
                        new_sel.append( obj )
                        continue
        sel = new_sel
    if filter_instances:
        sel = filter_instances( sel )
        
    return sel

def filter_instances( sel=[] ):
    sel = get_sel( sel )
    new_sel = sel[:]
    print(sel, new_sel)
    for obj in sel:
        if not obj in new_sel:
            continue
        if is_instance(obj):
            for instance in get_other_instances( obj ):
                new_sel.remove( instance )
    return new_sel

def rename_meshes( force=False, message=True, *args ):
    """
    Usage:
        Just launch it in Lookdev, Rig and animation publishes
    Goal:
        It'll rename meshes, nurbsCurves and nurbsSurfaces in a precised way wich will allow safer export/import alembics
    """
    if not force and not cmds.about( batch=True ) and cmds.confirmDialog( title='Confirm', 
        message="It'll rename all the meshes/curves of the scene", 
        button=['Yes','No'], 
        defaultButton='Yes', 
        cancelButton='No', 
        dismissString='No' ) == "No":
        return None
    meshes_scene = cmds.ls( type="mesh", ap=True )
    curves_scene = cmds.ls( type="nurbsCurve", ap=True )
    surfaces_scene = cmds.ls( type="nurbsSurface", ap=True )
    geometries_scene = meshes_scene + curves_scene + surfaces_scene
    geometries_scene = filter_instances( geometries_scene ) # Remove instances
    print(geometries_scene)
    geometries_scene_intermediate = []
    geometries_scene_no_intermediate = []
    for geometry in geometries_scene:
        if cmds.getAttr( geometry+".intermediateObject" ):
            geometries_scene_intermediate.append( geometry )
        else:
            geometries_scene_no_intermediate.append( geometry )
            
    for geometry in geometries_scene_intermediate:
        tr_geometry = get_parent( geometry )
        tr_geometry_sn = get_sn( tr_geometry )
        cmds.rename( geometry, _names_['geometry_intermediate'].format( tr_geometry_sn=tr_geometry_sn ) )
    for geometry in geometries_scene_no_intermediate:
        tr_geometry = get_parent( geometry )
        tr_geometry_sn = get_sn( tr_geometry )
        cmds.rename( geometry, _names_['geometry_displayed'].format( tr_geometry_sn=tr_geometry_sn ) )
    
    if message:
        cmds.inViewMessage( amg='Geometries have been renamed correctly.\nMake sure it has been done in both <hl>lookDev_publish</hl>, <hl>rig_publish</hl> & <hl>anim_publish</hl>.', pos='midCenter', fade=True, fadeStayTime=1000, dragKill=True )
            
class MayaSets():
    
    @staticmethod
    def select_members( sel=[], *args ):
        if not sel:
            sel = cmds.ls( sl=True, ap=True )
        elif type(sel) is not list:
            sel = [sel]
        m_sets = []
        objs = []
        for obj in sel:
            if cmds.objectType( obj ) == "objectSet":
                m_sets.append( obj )
        cmds.select( cl=True )
        for m_set in m_sets:
            cmds.select( cmds.listConnections( m_set+".dagSetMembers" ), add=True )
    
    @staticmethod
    def add( sel=[], *args ):
        if not sel:
            sel = cmds.ls( sl=True, ap=True )
        elif type(sel) is not list:
            sel = [sel]
        m_sets = []
        objs = []
        for obj in sel:
            if cmds.objectType( obj ) == "objectSet":
                m_sets.append( obj )
            else:
                objs.append( obj )
        for m_set in m_sets:
            cmds.sets( objs, addElement=m_set, noWarnings=True )
            
    @staticmethod
    def remove( sel=[], *args ):
        if not sel:
            sel = cmds.ls( sl=True, ap=True )
        elif type(sel) is not list:
            sel = [sel]
        m_sets = []
        objs = []
        for obj in sel:
            if cmds.objectType( obj ) == "objectSet":
                m_sets.append( obj )
            else:
                objs.append( obj )
        for m_set in m_sets:
            cmds.sets( objs, remove=m_set, noWarnings=True )

# UI Functions
def edit_form( name, config, grid_nb=10, offset=0 ):
	"""
	Configs possible are:
		- equalRow
			'Auto scalable rowLayout'
		- title
			'Two Children only, the top one is fixed, bottom one is scalable'
		- grid
			'Allow auto scalable gridLayout'
			<!> Limited to 1024 ligns by default <!>
		- fill
	"""
	children = cmds.formLayout(name,q=True,ca=True)
	nb = len(children)
	nd = cmds.formLayout(name,q=True,nd=True)
	if config == 'equalRow':
		w = nd/nb;
		for i in range(0,nb):
			cmds.formLayout(name, e=True, af=[children[i], 'top', 0])
			cmds.formLayout(name, e=True, ap=[children[i], 'left', 0, (i*w)])
			cmds.formLayout(name, e=True, ap=[children[i], 'right', 0, ((i+1)*w)])
			cmds.formLayout(name, e=True, af=[children[i], 'bottom', 0])
	elif config == 'title':
		if nb != 2 and nb != 3:
			cmds.error('Must Have 2 or 3 children, found '+str(nb))
		cmds.formLayout(name, e=True, af=[children[0], 'top', 0])
		cmds.formLayout(name, e=True, af=[children[0], 'left', 0])
		cmds.formLayout(name, e=True, af=[children[0], 'right', 0])
		cmds.formLayout(name, e=True, an=[children[0], 'bottom'])
		
		cmds.formLayout(name, e=True, ac=[children[1], 'top', 0, children[0]])
		cmds.formLayout(name, e=True, af=[children[1], 'left', 0])
		cmds.formLayout(name, e=True, af=[children[1], 'right', 0])
		if nb != 3:
			cmds.formLayout(name, e=True, af=[children[1], 'bottom', 0])
		else:
			cmds.formLayout(name, e=True, ac=[children[1], 'bottom', 0, children[2]])
			
			cmds.formLayout(name, e=True, an=[children[2], 'top'])
			cmds.formLayout(name, e=True, af=[children[2], 'left', 0])
			cmds.formLayout(name, e=True, af=[children[2], 'right', 0])
			cmds.formLayout(name, e=True, af=[children[2], 'bottom', 0])
			
	elif config == 'grid':
		buttons=0
		x=0
		while x < 1024:
			for y in range(0,grid_nb):
				if buttons == nb:
					break
				if x>0:
					cmds.formLayout(name, e=True, ac=[children[buttons], 'top', 0, children[buttons-grid_nb]])
				cmds.formLayout(name, e=True, ap=[children[buttons], 'left', 0, (y*nd/grid_nb)])
				cmds.formLayout(name, e=True, ap=[children[buttons], 'right', 0, ((y+1)*nd/grid_nb)])
				buttons+=1
			x+=1
			if buttons >= nb:
				break
	elif config == 'gridSizeable':
		buttons=0
		x=0
		nb_lines = len( children ) / (grid_nb)
		if ( len( children ) % (grid_nb) ) > 0:
			nb_lines+=1
		grid_div_width = nd / (grid_nb)
		grid_div_heigth = nd / (nb_lines)
		for line in range( nb_lines ):
			for col in range( grid_nb ):
				if buttons >= ( len( children ) ):
					break
				# print buttons, 'top:', line*nd/nb_lines, 'bottom:', (line+1)*nd/nb_lines
				cmds.formLayout( name, e=True, ap=[ children[buttons], 'top', offset, (line*grid_div_heigth) ] )
				cmds.formLayout( name, e=True, ap=[ children[buttons], 'left', offset, (col*grid_div_width) ] )
				cmds.formLayout( name, e=True, ap=[ children[buttons], 'right', offset, ((col+1)*grid_div_width) ] )
				cmds.formLayout( name, e=True, ap=[ children[buttons], 'bottom', offset, (line+1)*grid_div_heigth ] )
				buttons+=1
			x+=1
			
	elif config == 'fill':
		if nb != 1:
			cmds.error('Must Have 1 child')
		cmds.formLayout(name, e=True, af=[children[0], 'top', 0])
		cmds.formLayout(name, e=True, af=[children[0], 'left', 0])
		cmds.formLayout(name, e=True, af=[children[0], 'right', 0])
		cmds.formLayout(name, e=True, af=[children[0], 'bottom', 0])

# UI
class UI():
    
    def __init__( self, *args ):
        """
        """
        self.window = _window_['name']
        self.uis = {}
        self.lays = {}
        self.buttons = {}
        
        if not cmds.about( batch=True ):
            self.create()
        
    def create( self ):
        """
        """
        # Window
        if cmds.window( self.window, q=True, exists=True ):
            cmds.deleteUI( self.window )
        self.window = cmds.window( self.window, t=_window_['title'], toolbox=True )
        cmds.showWindow( self.window )
        
        # Layouts
        self.lays['frame'] = cmds.frameLayout( lv=False, mh=5, mw=5 )
        
        # Buttons
        self.buttons['rename_meshes'] = cmds.iconTextButton( l="Rename Geometries", 
            c=partial( rename_meshes, False ),
            image="polyRemesh.png",
            style="iconAndTextHorizontal",
            annotation=rename_meshes.__doc__,
            align="center")
        self.lays['select_in_sets'] = cmds.rowLayout( adj=1, nc=3 )
        self.buttons['select_in_sets'] = cmds.iconTextButton( l="Select in Sets", 
            c=MayaSets.select_members, 
            image="setEdit.png", 
            style="iconAndTextHorizontal",
            annotation="DoubleClic : Select {}".format( _names_['geo_cache'] ),
            align="center")
        self.buttons['select_in_sets'] = cmds.iconTextButton( l="", 
            c=MayaSets.add, 
            image="setEdAddCmd.png", 
            style="iconOnly",
            annotation="Add selection to the set",
            align="center")
        self.buttons['select_in_sets'] = cmds.iconTextButton( l="", 
            c=MayaSets.remove, 
            image="setEdRemoveCmd.png", 
            style="iconOnly",
            annotation="DoubleClic : Select {}".format( _names_['geo_cache'] ),
            align="center")
