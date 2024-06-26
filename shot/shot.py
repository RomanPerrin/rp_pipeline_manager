# coding : utf-8parent_layout
__author__ = 'Roman PERRIN'
#Author: Roman PERRIN

#Libraries
import maya.cmds as cmds
import maya.mel as mel
import os
from functools import partial
import shutil

#files
from .. import main_window
from .addSqSh import addSequenceUI
from .addSqSh import addShotUI
from .. import sceneUtility

icon_size = 35
row_size = 35

class ShotUi():
    def __init__(self, parent_layout) -> None:
        self.parent_layout = parent_layout

        self.layout = cmds.formLayout(p=self.parent_layout)

        sq_text = cmds.text(label="Sequence", p=self.layout)
        
        sequence_lay = cmds.formLayout(p=self.layout)
        self.sequence_scrollList = cmds.textScrollList("sequence", p=sequence_lay, numberOfRows=8, allowMultiSelection=False, selectCommand=partial(self.updateShotScrollList))
        addButton = cmds.symbolButton('sequenceAddButton', p=sequence_lay, ann=f'add sequence', i='pickHandlesComp', height=icon_size, width=icon_size, command=partial(self.addSequence))
        # Attach the assetsScrollList
        cmds.formLayout(sequence_lay, e=True, attachForm=[(self.sequence_scrollList, "left", 0), (self.sequence_scrollList, "top", 0), (self.sequence_scrollList, "bottom", 0)])
        # Attach the assetsAddButton
        cmds.formLayout(sequence_lay, e=True, attachForm=[(addButton, "right", 0), (addButton, "top", 0)])
        cmds.formLayout(sequence_lay, e=True, attachControl=[(self.sequence_scrollList, "right", 0, addButton)])

        openSqLayoutButton = cmds.button(p=self.layout, label="open seq layout", command=self.openSqLayout)
        createShotLayoutButton = cmds.button(p=self.layout, label="create shot layout", command=self.createShotLayout)

        sh_text = cmds.text(label="Shot", p=self.layout)

        shot_lay = cmds.formLayout(p=self.layout)
        self.shot_scrollList = cmds.textScrollList("shot", p=shot_lay, numberOfRows=5, allowMultiSelection=False)
        addButton = cmds.symbolButton('shotAddButton', p=shot_lay, ann=f'add shot', i='pickHandlesComp', height=icon_size, width=icon_size, command=partial(self.addShot))
        openShotDirectoryButton = cmds.symbolButton('openShotDirectoryButton', p=shot_lay, ann=f'Open shot directory', i='fileOpen', height=icon_size, width=icon_size, command=partial(self.openShotDirectory))
        # Attach the shot_scrollList
        cmds.formLayout(shot_lay, e=True, attachForm=[(self.shot_scrollList, "left", 0), (self.shot_scrollList, "top", 0), (self.shot_scrollList, "bottom", 0)])
        # Attach the shots*Button
        cmds.formLayout(shot_lay, e=True, attachForm=[(addButton, "right", 0),
                                                      (addButton, "top", 0),
                                                      (openShotDirectoryButton, "right", 0)])
        cmds.formLayout(shot_lay, e=True, attachControl=[(self.shot_scrollList, "right", 0, addButton),
                                                         (self.shot_scrollList, "right", 0, openShotDirectoryButton),
                                                         (openShotDirectoryButton, "top", 0, addButton)])

        openShLayoutButton = cmds.button(p=self.layout, label="open shot layout", command=self.openShLayout)
        createConformityLayoutButton = cmds.button(p=self.layout, label="create conformity layout", command=self.createConformityLayout)
        
        openConformityLayoutButton = cmds.button(p=self.layout, label="open conformity layout", command=self.openConformityLayout)
        openShotRenderButton = cmds.button(p=self.layout, label="open shot render", command=self.openShotRender)
        openShotAnimButton = cmds.button(p=self.layout, label="open shot anim", command=self.openShotAnim)

        cmds.formLayout( self.layout, edit=True,
                        attachForm=[(sq_text, 'top', 5),
                                    (sq_text, 'left', 5),
                                    (sequence_lay, 'left', 5),
                                    (sequence_lay, 'right', 5),
                                    (openSqLayoutButton, 'left', 5),
                                    (createShotLayoutButton, 'right', 5),
                                    (sh_text, 'left', 5),
                                    (shot_lay, 'left', 5),
                                    (shot_lay, 'right', 5),
                                    (openShLayoutButton, 'left', 5),
                                    (openShLayoutButton, 'right', 5),
                                    (createConformityLayoutButton, 'left', 5),
                                    (openConformityLayoutButton, 'left', 5),
                                    (openConformityLayoutButton, 'right', 5),
                                    (openShotAnimButton, 'left', 5),
                                    (openShotAnimButton, 'right', 5),
                                    (openShotRenderButton, 'left', 5),
                                    (openShotRenderButton, 'right', 5),
                                    (openShotRenderButton, 'bottom', 5)],

                        attachControl=[(sequence_lay, 'top', 5, sq_text),
                                       (openSqLayoutButton, 'top', 5, sequence_lay),
                                       (createShotLayoutButton, 'top', 5, sequence_lay),
                                       (sh_text, 'top', 5, openSqLayoutButton),
                                       (shot_lay, 'top', 5, sh_text),
                                       (shot_lay, 'bottom', 5, openShLayoutButton),
                                       (openShLayoutButton, 'bottom', 5, createConformityLayoutButton),
                                       (createConformityLayoutButton, 'bottom', 5, openShotAnimButton),
                                       (openConformityLayoutButton, 'bottom', 5, openShotAnimButton),
                                       (openShotAnimButton, 'bottom', 5, openShotRenderButton)],
                        
                        attachPosition=[(openSqLayoutButton, 'right', 5, 50),
                                        (createShotLayoutButton, 'left', 5, 50),
                                        (createConformityLayoutButton, 'right', 5, 50),
                                        (openConformityLayoutButton, 'left', 5, 50)])
    
        try:
            self.updateSequenceScrollList()
        except:
            pass


    def updateSequenceScrollList(self, *args):
        # print("update sequence")
        self.pipe_dir = main_window.pipe_dir
        sequence_list = []
        if self.pipe_dir:
            self.sequence_dir = os.path.join(self.pipe_dir, "05_shot")
            for dir in os.listdir(self.sequence_dir):
                if os.path.isdir(os.path.join(self.sequence_dir, dir)):
                    sequence_list.append(dir)
        # print(sequence_list)
        cmds.textScrollList('sequence', e=True, removeAll=True)
        cmds.textScrollList('sequence', e=True, append=sequence_list)
        return sequence_list

    def addSequence(self, *args):
        print("adding sequence")
        addSequenceUI(self.sequence_dir, self)
    
    def openSqLayout(self, *args):
        print("opening sequence layout")
        sequence_name = cmds.textScrollList('sequence', q=True, si=True)[0]
        if not sequence_name:
            return
        
        if not f"{sequence_name}_master_layout" in os.listdir(os.path.join(self.sequence_dir, "_master_layout")):
            os.makedirs(os.path.join(self.sequence_dir, "_master_layout", f"{sequence_name}_master_layout"), exist_ok=True)

        filename = os.path.join(self.sequence_dir, "_master_layout", f"{sequence_name}_master_layout", f"{sequence_name}_master_layout.ma")
        try:
            sceneUtility.openScene(filename)
            return
        except IOError as e:
            print(e)
        
        cmds.file(f=True, new=True)
        cmds.file(rename=filename)
        cmds.setAttr("defaultResolution.width", 2048)
        cmds.setAttr("defaultResolution.height", 858)
        cmds.file(f=True, type='mayaAscii', save=True)
        
    def createShotLayout(self, *args):
        # print("creating shot layout")
        sequence_name = cmds.textScrollList('sequence', q=True, si=True)[0]
        if not sequence_name:
            return
        shot_list =self.getShotList(sequence_name)
        
        if not f"{sequence_name}_master_layout" in os.listdir(os.path.join(self.sequence_dir, "_master_layout")):
           cmds.warning(f"no sequence layout found for {sequence_name}")
           return

        existingShotList = []
        filename = os.path.join(self.sequence_dir, "_master_layout", f"{sequence_name}_master_layout", f"{sequence_name}_master_layout.ma").replace(os.sep, '/')
        for i in range(len(shot_list)):
            destination = os.path.join(self.shot_dir, shot_list[i], "maya", "scenes", "layout", f"{shot_list[i]}_shot_layout.ma").replace(os.sep, '/')
            if not os.path.exists(destination):
                shutil.copy(filename, destination)
                print(f"creating shot layout for {shot_list[i]}")
                pass
            else:   
                print(f"shot layout already exists for {shot_list[i]}")
                existingShotList.append({'name':shot_list[i], 'path':destination})
        
        if existingShotList:
            overwriteWindow = replaceLayout(existingShotList, filename, 'shot')
        
    def getShotList(self, sequence, *args):
        shot_list = []
        if self.pipe_dir:
            self.shot_dir = os.path.join(self.pipe_dir, "05_shot", sequence)
            for dir in os.listdir(self.shot_dir):
                if os.path.isdir(os.path.join(self.shot_dir, dir)):
                    shot_list.append(dir)
        
        return shot_list

    def updateShotScrollList(self, *args):
        # print("update shot")
        shot_list =self.getShotList(cmds.textScrollList('sequence', q=True, si=True)[0])

        # print(shot_list)
        cmds.textScrollList('shot', e=True, removeAll=True)
        cmds.textScrollList('shot', e=True, append=shot_list)
        return shot_list

    def addShot(self, *args):
        addShotUI(self.shot_dir, self)
    
    def openShotDirectory(self, *args):
        shot_name = cmds.textScrollList('shot', q=True, si=True)[0]
        if not shot_name:
            return
        
        dir = os.path.normpath(os.path.join(self.shot_dir, shot_name).replace(os.sep, "/"))
        print(dir)
        os.popen(fr'explorer "{dir}"')

    def openShLayout(self, *args):
        # print("opening shot layout")
        shot_name = cmds.textScrollList('shot', q=True, si=True)[0]
        if not shot_name:
            return
        
        
        project_dir = os.path.join(self.shot_dir, shot_name, "maya").replace(os.sep, '/')
        filename = os.path.join(project_dir, "scenes", "layout", f"{shot_name}_shot_layout.ma")
        
        if not os.path.exists(filename):
            cmds.warning(f"no shot layout found for {shot_name}")
            return
        
        try:
            sceneUtility.openScene(filename, project_dir)
            return
        except IOError as e:
            print(e)
        except RuntimeError as e:
            print(e)

    def createConformityLayout(self, *args):
        # print("creating conformity layout")
        shot_name = cmds.textScrollList('shot', q=True, si=True)[0]
        if not shot_name:
            return
        
        shot_layout = os.path.join(self.shot_dir, shot_name, "maya", "scenes", "layout", f"{shot_name}_shot_layout.ma")
        if not os.path.exists(shot_layout):
           cmds.warning(f"no shot layout found for {shot_name}")
           return

        existingShotList = []
        destination = os.path.join(self.shot_dir, shot_name, "maya", "scenes", "layout", f"{shot_name}_conformity_layout.ma")
        if not os.path.exists(destination):
            shutil.copy(shot_layout, destination)
            print(f"creating conformity layout for {shot_name}")
        else:    
            cmds.warning(f"conformity layout already exists for {shot_name}")
            existingShotList.append({'name':shot_name, 'path':destination})
        
        if existingShotList:
            overwriteWindow = replaceLayout(existingShotList, shot_layout, 'conformity')
        
        # mel.eval(f'setProject "{os.path.join(self.shot_dir, shot_name, "maya").replace(os.sep, "/")}"')
        # cmds.file(destination, open=True, force=True)

    def openConformityLayout(self, *args):
        # print("opening conformity layout")
        shot_name = cmds.textScrollList('shot', q=True, si=True)[0]
        if not shot_name:
            return
        
        filename = os.path.join(self.shot_dir, shot_name, "maya", "scenes", "layout", f"{shot_name}_conformity_layout.ma")
        if not os.path.exists(filename):
            cmds.warning(f"no conformity layout found for {shot_name}")
            return
            
        mel.eval(f'setProject "{os.path.join(self.shot_dir, shot_name, "maya").replace(os.sep, "/")}"')
        cmds.file(filename, open=True, force=True)

    def openShotAnim(self, *args):
        # print("opening shot anim")
        shot_name = cmds.textScrollList('shot', q=True, si=True)[0]
        if not shot_name:
            return
        
        project_dir = os.path.join(self.shot_dir, shot_name, "maya").replace(os.sep, '/')
        filename = os.path.join(project_dir, "scenes", "anim", f"{shot_name}_anim.ma")
        
        if not os.path.exists(filename):
            source = os.path.join(self.shot_dir, shot_name, "maya", "scenes", "layout", f"{shot_name}_conformity_layout.ma")
            shutil.copy(source, filename)
            print(f"creating shot anim for {shot_name}")
        
        mel.eval(f'setProject "{project_dir}"')
        cmds.file(filename, open=True , f=True)

    def openShotRender(self, *args):
        # print("opening shot render")
        shot_name = cmds.textScrollList('shot', q=True, si=True)[0]
        if not shot_name:
            return
        
        project_dir = os.path.join(self.shot_dir, shot_name, "maya").replace(os.sep, '/')
        filename = os.path.join(project_dir, "scenes", "render", f"{shot_name}_render.ma")
        render_setup = os.path.join(self.pipe_dir, "02_ressource/Templates/Render_settings/render_setup.ma").replace(os.sep, "/")
        
        if not os.path.exists(filename):
            cmds.file(render_setup, open=True , f=True)
            conformity_layout = os.path.join(self.shot_dir, shot_name, "maya", "scenes", "layout", f"{shot_name}_conformity_layout.ma")
            cmds.file(conformity_layout, i=True , f=True, preserveReferences=True)
            mel.eval(f'setProject "{project_dir}"')
            print(f"creating shot render for {shot_name}")
            cmds.file(rename=filename)
            cmds.file(f=True, type='mayaAscii', save=True )
            return
        
        mel.eval(f'setProject "{project_dir}"')
        cmds.file(filename, open=True , force=True)

class replaceLayout():
    def __init__(self, existingShotList, filename, layoutName) -> None:
        self.window = f'{layoutName}Layout'
        self.size = (200, 300)
        self.existingShotList = existingShotList
        self.filename = filename
        self.layoutName = layoutName
        self.UI()

    def UI(self):
        if cmds.window(self.window, q=True,exists=True):
            cmds.deleteUI(self.window)
        self.window = cmds.window(self.window, wh=self.size, minimizeButton=False, maximizeButton=False)
        
        mainLayout = cmds.formLayout()
        sh_text = cmds.text(label=f"Select the {self.layoutName}s to overwrite", p=mainLayout)
        self.shot_scrollList = cmds.textScrollList("shot", p=mainLayout, append=[i['name'] for i in self.existingShotList], numberOfRows=8, allowMultiSelection=True)
        self.overwriteButton  =cmds.button(p=mainLayout, label="Overwrite", command=self.confirmWindow)
        
        # Attach 
        cmds.formLayout(mainLayout, e=True, attachForm=[(sh_text, "left", 0),
                                                        (sh_text, "top", 0),
                                                        (self.shot_scrollList, "left", 0),
                                                        (self.shot_scrollList, "right", 0),
                                                        (self.overwriteButton, "left", 0),
                                                        (self.overwriteButton, "bottom", 0)])
        cmds.formLayout(mainLayout, e=True, attachControl=[(self.shot_scrollList, "top", 0, sh_text),
                                                           (self.shot_scrollList, "bottom", 0, self.overwriteButton)])

        cmds.showWindow(self.window)
        
    def confirmWindow(self, *args):
        if not cmds.textScrollList(self.shot_scrollList, q=1, si=1):
            return
        
        self.answer = cmds.confirmDialog(t='Confirm',
                                         m=f'Do you really want to replace the selected {self.layoutName}s?',
                                         b=['Replace', 'Cancel'],
                                         db='Cancel',
                                         cb='Cancel',
                                         p=self.window)
        if self.answer == 'Replace':
            self.overwrite()

        if self.answer == 'Cancel':
            pass
    
    def overwrite(self):
        cmds.waitCursor(state=True)
        shotList = cmds.textScrollList(self.shot_scrollList, q=1, si=1)

        shotList = [i for i in self.existingShotList if i['name'] in shotList]
        
        for i in range(len(shotList)):
            try:    
                destination = shotList[i]['path']
                shutil.copy(self.filename, destination)
                print(f"overwriting {self.layoutName} layout for {shotList[i]['name']}")
            except:
                print(f'error overwriting {self.layoutName} layout for {shotList[i]["name"]}')
        
        cmds.waitCursor(state=False)