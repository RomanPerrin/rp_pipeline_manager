# coding : utf-8
__author__ = 'Roman PERRIN'
#Author: Roman PERRIN

#Libraries
import maya.cmds as cmds
import os
import shutil

#files

icon_size = 35
row_size = 35

class addSequenceUI():
    def __init__(self, dir, obj, *args):
        self.pipe_dir = dir
        self.obj = obj
        self.UI()
    
    def UI(self, *args):
        size = (300, 50)
        
        self.window = f"Add sequence"
        if cmds.window(self.window, q=True,exists=True):
            cmds.deleteUI(self.window)
        self.window = cmds.window(self.window, wh=size, minimizeButton=False, maximizeButton=False)
        
        master_lay = cmds.rowLayout(numberOfColumns=3, height=row_size, adjustableColumn=2)
        cmds.text(label=f'name of the new sequence')
        self.name = cmds.textField(p=master_lay, enterCommand=self.create)
        cmds.button(p=master_lay, label='Create', command=self.create)
        
        cmds.showWindow(self.window)
    
    def create(self, *args):
        name = cmds.textField(self.name, q=True, text=True)
        dir = os.path.join(self.pipe_dir, name).replace(os.sep, '/')
        os.makedirs(dir, exist_ok=True)
        
        print(f'{name} created at {dir}')
        cmds.deleteUI(self.window)
        self.obj.updateSequenceScrollList()
        return

class addShotUI():
    def __init__(self, dir, obj, *args):
        self.pipe_dir = dir
        self.obj = obj
        self.UI()
    
    def UI(self, *args):
        size = (300, 50)
        
        self.window = f"Add shot"
        if cmds.window(self.window, q=True,exists=True):
            cmds.deleteUI(self.window)
        self.window = cmds.window(self.window, wh=size, minimizeButton=False, maximizeButton=False)
        
        master_lay = cmds.rowLayout(numberOfColumns=3, height=row_size, adjustableColumn=2)
        cmds.text(label=f'name of the new shot')
        self.name = cmds.textField(p=master_lay, enterCommand=self.create)
        cmds.button(p=master_lay, label='Create', command=self.create)
        
        cmds.showWindow(self.window)
    
    def create(self, *args):
        print(self.pipe_dir)
        shot_name = self.pipe_dir.split('/')[-1] + '_' + cmds.textField(self.name, q=True, text=True)
        print(shot_name)
        return
        shot_dir = os.path.join(self.pipe_dir, shot_name).replace(os.sep, '/')
        print(shot_dir)
        os.makedirs(shot_dir, exist_ok=True)
        return
        os.makedirs(os.path.join(shot_dir, 'camera'), exist_ok=True)
        os.makedirs(os.path.join(shot_dir, 'houdini'), exist_ok=True)
        os.makedirs(os.path.join(shot_dir, 'nuke'), exist_ok=True)
        self.createProject(os.path.join(shot_dir, 'maya'))
        
        print(f'{shot_name} created at {shot_dir}')
        cmds.deleteUI(self.window)
        self.obj.updateShotScrollList()
        cmds.textScrollList('assets', e=True, si=shot_name)
        return
    
    def createProject(self, project_dir, *args):
        os.makedirs(os.path.join(project_dir, 'cache', 'bifrost'), exist_ok=True)
        os.makedirs(os.path.join(project_dir, 'cache', 'nCache', 'fluid'), exist_ok=True)
        os.makedirs(os.path.join(project_dir, 'cache', 'particles'), exist_ok=True)
        os.makedirs(os.path.join(project_dir, 'data'), exist_ok=True)
        os.makedirs(os.path.join(project_dir, 'images'), exist_ok=True)
        os.makedirs(os.path.join(project_dir, 'movies'), exist_ok=True)
        os.makedirs(os.path.join(project_dir, 'scenes', 'anim'), exist_ok=True)
        os.makedirs(os.path.join(project_dir, 'scenes', 'layout'), exist_ok=True)
        os.makedirs(os.path.join(project_dir, 'scenes', 'render'), exist_ok=True)
        os.makedirs(os.path.join(project_dir, 'sound'), exist_ok=True)
        os.makedirs(os.path.join(project_dir, 'sourceimages', '3dPaintTextures'), exist_ok=True)
        os.makedirs(os.path.join(project_dir, 'sourceimages', 'environment'), exist_ok=True)
        os.makedirs(os.path.join(project_dir, 'sourceimages', 'imagePlane'), exist_ok=True)
        os.makedirs(os.path.join(project_dir, 'sourceimages', 'imageSequence'), exist_ok=True)
        
        source = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'workspace.mel')
        source = source.replace(os.sep, '/')
        destination = os.path.join(project_dir, 'workspace.mel')
        destination = destination.replace(os.sep, '/')
        shutil.copy(source, destination)
        
        return
