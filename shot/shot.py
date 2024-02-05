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
        createShotLayoutButton = cmds.button(p=self.layout, label="create shot layout", command=self.createShotLayoutLayout)

        sh_text = cmds.text(label="Shot", p=self.layout)

        shot_lay = cmds.formLayout(p=self.layout)
        self.shot_scrollList = cmds.textScrollList("shot", p=shot_lay, numberOfRows=5, allowMultiSelection=False)
        addButton = cmds.symbolButton('shotAddButton', p=shot_lay, ann=f'add shot', i='pickHandlesComp', height=icon_size, width=icon_size, command=partial(self.addShot))
        # Attach the assetsshot_scrollList
        cmds.formLayout(shot_lay, e=True, attachForm=[(self.shot_scrollList, "left", 0), (self.shot_scrollList, "top", 0), (self.shot_scrollList, "bottom", 0)])
        # Attach the assetsAddButton
        cmds.formLayout(shot_lay, e=True, attachForm=[(addButton, "right", 0), (addButton, "top", 0)])
        cmds.formLayout(shot_lay, e=True, attachControl=[(self.shot_scrollList, "right", 0, addButton)])

        openShLayoutButton = cmds.button(p=self.layout, label="open shot layout", command=self.openShLayout)
        createConformityLayoutButton = cmds.button(p=self.layout, label="create conformity layout", command=self.createConformityLayoutLayout)
        
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
                                    (createConformityLayoutButton, 'right', 5),
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
        if not f"{sequence_name}_master_layout" in os.listdir(os.path.join(self.sequence_dir, "_master_layout")):
            os.makedirs(os.path.join(self.sequence_dir, "_master_layout", f"{sequence_name}_master_layout"), exist_ok=True)

        filename = os.path.join(self.sequence_dir, "_master_layout", f"{sequence_name}_master_layout", f"{sequence_name}_master_layout.ma")
        if os.path.exists(filename):
            cmds.file(filename, open=True , force=True)
            return
        
        cmds.file(rename=filename)
        cmds.file(f=True, type='mayaAscii', save=True )
        
    def createShotLayoutLayout(self, *args):
        # print("creating shot layout")
        sequence_name = cmds.textScrollList('sequence', q=True, si=True)[0]
        shot_list =self.getShotList(sequence_name)
        
        if not f"{sequence_name}_master_layout" in os.listdir(os.path.join(self.sequence_dir, "_master_layout")):
           cmds.warning(f"no sequence layout found for {sequence_name}")
           return

        filename = os.path.join(self.sequence_dir, "_master_layout", f"{sequence_name}_master_layout", f"{sequence_name}_master_layout.ma").replace(os.sep, '/')
        for i in range(len(shot_list)):
            destination = os.path.join(self.shot_dir, shot_list[i], "maya", "scenes", "layout", f"{shot_list[i]}_shot_layout.ma").replace(os.sep, '/')
            if not os.path.exists(destination):
                shutil.copy(filename, destination)
                print(f"creating shot layout for {shot_list[i]}")
                pass
            print(f"shot layout already exists for {shot_list[i]}")
        
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
    
    def openShLayout(self, *args):
        # print("opening shot layout")
        shot_name = cmds.textScrollList('shot', q=True, si=True)[0]
        filename = os.path.join(self.shot_dir, shot_name, "maya", "scenes", "layout", f"{shot_name}_shot_layout.ma")
        if not os.path.exists(filename):
            cmds.warning(f"no shot layout found for {shot_name}")
            return
        print(os.path.join(self.shot_dir, shot_name, "maya"))
        mel.eval(f'setProject "{os.path.join(self.shot_dir, shot_name, "maya")}"')
        cmds.file(filename, open=True, force=True)

    def createConformityLayoutLayout(self, *args):
        # print("creating conformity layout")
        shot_name = cmds.textScrollList('shot', q=True, si=True)[0]
        shot_layout = os.path.join(self.shot_dir, shot_name, "maya", "scenes", "layout", f"{shot_name}_shot_layout.ma")
        if not os.path.exists(shot_layout):
           cmds.warning(f"no shot layout found for {shot_name}")
           return

        destination = os.path.join(self.shot_dir, shot_name, "maya", "scenes", "layout", f"{shot_name}_conformity_layout.ma")
        if not os.path.exists(destination):
            shutil.copy(shot_layout, destination)
            print(f"creating conformity layout for {shot_name}")
            pass
        cmds.warning(f"conformity layout already exists for {shot_name}")

    def openConformityLayout(self, *args):
        # print("opening conformity layout")
        shot_name = cmds.textScrollList('shot', q=True, si=True)[0]
        filename = os.path.join(self.shot_dir, shot_name, "maya", "scenes", "layout", f"{shot_name}_conformity_layout.ma")
        if not os.path.exists(filename):
            cmds.warning(f"no conformity layout found for {shot_name}")
            return
            
        mel.eval(f'setProject "{os.path.join(self.shot_dir, shot_name, "maya")}"')
        cmds.file(filename, open=True, force=True)

    def openShotAnim(self, *args):
        # print("opening shot anim")
        shot_name = cmds.textScrollList('shot', q=True, si=True)[0]
        filename = os.path.join(self.shot_dir, shot_name, "maya", "scenes", "anim", f"{shot_name}_anim.ma")
        
        if not os.path.exists(filename):
            source = os.path.join(self.shot_dir, shot_name, "maya", "scenes", "layout", f"{shot_name}_conformity_layout.ma")
            shutil.copy(source, filename)
            print(f"creating shot anim for {shot_name}")
        
        mel.eval(f'setProject "{os.path.join(self.shot_dir, shot_name, "maya")}"')
        cmds.file(filename, open=True , f=True)

    def openShotRender(self, *args):
        # print("opening shot render")
        shot_name = cmds.textScrollList('shot', q=True, si=True)[0]
        filename = os.path.join(self.shot_dir, shot_name, "maya", "scenes", "render", f"{shot_name}_render.ma")
        render_setup = ""
        
        if not os.path.exists(filename):
            cmds.file(render_setup, open=True , f=True)
            conformity_layout = os.path.join(self.shot_dir, shot_name, "maya", "scenes", "layout", f"{shot_name}_conformity_layout.ma")
            cmds.file(conformity_layout, i=True , f=True)
            print(f"creating shot render for {shot_name}")
            cmds.file(rename=filename)
            cmds.file(f=True, type='mayaAscii', save=True )
            return
        
        mel.eval(f'setProject "{os.path.join(self.shot_dir, shot_name, "maya")}"')
        cmds.file(filename, open=True , force=True)
