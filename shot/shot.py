# coding : utf-8parent_layout
__author__ = 'Roman PERRIN'
#Author: Roman PERRIN

#Libraries
import maya.cmds as cmds
import maya.mel as mel
import os
from functools import partial

#files
from .. import main_window
from .addSqSh import addSequenceUI

icon_size = 35
row_size = 35

class ShotUi():
    def __init__(self, parent_layout) -> None:
        self.parent_layout = parent_layout

        self.layout = cmds.formLayout(p=self.parent_layout)

        sq_text = cmds.text(label="Sequence", p=self.layout)
        
        sequence_lay = cmds.formLayout(p=self.layout)
        scrollList = cmds.textScrollList("sequence", p=sequence_lay, numberOfRows=5, allowMultiSelection=False, selectCommand=partial(self.updateShotScrollList))
        addButton = cmds.symbolButton('sequenceAddButton', p=sequence_lay, ann=f'add sequence', i='pickHandlesComp', height=icon_size, width=icon_size, command=partial(self.addSequence))
        # Attach the assetsScrollList
        cmds.formLayout(sequence_lay, e=True, attachForm=[(scrollList, "left", 0), (scrollList, "top", 0), (scrollList, "bottom", 0)])
        # Attach the assetsAddButton
        cmds.formLayout(sequence_lay, e=True, attachForm=[(addButton, "right", 0), (addButton, "top", 0)])
        cmds.formLayout(sequence_lay, e=True, attachControl=[(scrollList, "right", 0, addButton)])

        openSqLayoutButton = cmds.button(p=self.layout, label="open seq layout", command=self.openSqLayout)
        createShotLayoutButton = cmds.button(p=self.layout, label="create shot layout", command=self.createShotLayoutLayout)

        sh_text = cmds.text(label="Shot", p=self.layout)

        shot_lay = cmds.formLayout(p=self.layout)
        scrollList = cmds.textScrollList("shot", p=shot_lay, numberOfRows=5, allowMultiSelection=False)
        addButton = cmds.symbolButton('shotAddButton', p=shot_lay, ann=f'add shot', i='pickHandlesComp', height=icon_size, width=icon_size, command=partial(self.addShot))
        # Attach the assetsScrollList
        cmds.formLayout(shot_lay, e=True, attachForm=[(scrollList, "left", 0), (scrollList, "top", 0), (scrollList, "bottom", 0)])
        # Attach the assetsAddButton
        cmds.formLayout(shot_lay, e=True, attachForm=[(addButton, "right", 0), (addButton, "top", 0)])
        cmds.formLayout(shot_lay, e=True, attachControl=[(scrollList, "right", 0, addButton)])

        openShLayoutButton = cmds.button(p=self.layout, label="open shot layout", command=self.openShLayout)
        createConformityLayoutButton = cmds.button(p=self.layout, label="create conformity layout", command=self.createConformityLayoutLayout)
        
        openShotRenderButton = cmds.button(p=self.layout, label="open shot layout", command=self.openShotRender)
        openShotAnimButton = cmds.button(p=self.layout, label="create conformity layout", command=self.openShotAnim)

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
                                    (createConformityLayoutButton, 'right', 5),
                                    (openShotRenderButton, 'left', 5),
                                    (openShotAnimButton, 'right', 5),
                                    (openShotRenderButton, 'bottom', 5),
                                    (openShotAnimButton, 'bottom', 5)],

                        attachControl=[(sequence_lay, 'top', 5, sq_text),
                                       (openSqLayoutButton, 'top', 5, sequence_lay),
                                       (createShotLayoutButton, 'top', 5, sequence_lay),
                                       (sh_text, 'top', 5, openSqLayoutButton),
                                       (shot_lay, 'top', 5, sh_text),
                                       (shot_lay, 'bottom', 5, openShLayoutButton),
                                       (openShLayoutButton, 'bottom', 5, openShotRenderButton),
                                       (createConformityLayoutButton, 'bottom', 5, openShotRenderButton)],
                        
                        attachPosition=[(openSqLayoutButton, 'right', 5, 50),
                                        (createShotLayoutButton, 'left', 5, 50),
                                        (openShLayoutButton, 'right', 5, 50),
                                        (createConformityLayoutButton, 'left', 5, 50),
                                        (openShotRenderButton, 'right', 5, 50),
                                        (openShotAnimButton, 'left', 5, 50)])
    
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
    
    def createShotLayoutLayout(self, *args):
        print("creating shot layout")

    def updateShotScrollList(self, *args):
        # print("update shot")
        shot_list = []
        if self.pipe_dir:
            self.shot_dir = os.path.join(self.pipe_dir, "05_shot", cmds.textScrollList('sequence', q=True, si=True)[0])
            for dir in os.listdir(self.shot_dir):
                if os.path.isdir(os.path.join(self.shot_dir, dir)):
                    shot_list.append(dir)
        # print(shot_list)
        cmds.textScrollList('shot', e=True, removeAll=True)
        cmds.textScrollList('shot', e=True, append=shot_list)
        return shot_list

    def addShot(self, *args):
        print("adding shot")
    
    def openShLayout(self, *args):
        print("opening shot layout")

    def createConformityLayoutLayout(self, *args):
        print("creating conformity layout")

    def openShotRender(self, *args):
        print("opening shot render")

    def openShotAnim(self, *args):
        print("opening shot anim")