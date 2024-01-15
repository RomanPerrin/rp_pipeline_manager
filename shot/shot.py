# coding : utf-8parent_layout
__author__ = 'Roman PERRIN'
#Author: Roman PERRIN

#Libraries
import maya.cmds as cmds
import maya.mel as mel
import os
from functools import partial

#files
from rp_pipeline_manager import main_window

icon_size = 35
row_size = 35

class ShotUi():
    def __init__(self, parent_layout) -> None:
        self.parent_layout = parent_layout
        self.pipe_dir = ""

        self.layout = cmds.formLayout(p=self.parent_layout)

        sq_text = cmds.text(label="Sequence", p=self.layout)
        
        sequence_lay = cmds.formLayout(p=self.layout)
        scrollList = cmds.textScrollList("sequence", p=sequence_lay, numberOfRows=5, allowMultiSelection=False, selectCommand=partial(self.updateSequenceScrollList))
        addButton = cmds.symbolButton('sequenceAddButton', p=sequence_lay, ann=f'add sequence', i='pickHandlesComp', height=icon_size, width=icon_size, command=partial(self.addSequence))
        # Attach the assetsScrollList
        cmds.formLayout(sequence_lay, e=True, attachForm=[(scrollList, "left", 0), (scrollList, "top", 0), (scrollList, "bottom", 0)])
        # Attach the assetsAddButton
        cmds.formLayout(sequence_lay, e=True, attachForm=[(addButton, "right", 0), (addButton, "top", 0)])
        cmds.formLayout(sequence_lay, e=True, attachControl=[(scrollList, "right", 0, addButton)])

        openSqLayoutButton = cmds.button(p=self.layout, label="open seq layout", command=self.openSqLayout)
        createShotLayoutButton = cmds.button(p=self.layout, label="open seq layout", command=self.createShotLayoutLayout)

        sh_text = cmds.text(label="Shot", p=self.layout)

        shot_lay = cmds.formLayout(p=self.layout)
        scrollList = cmds.textScrollList("shot", p=shot_lay, numberOfRows=5, allowMultiSelection=False, selectCommand=partial(self.updateShotScrollList))
        addButton = cmds.symbolButton('shotAddButton', p=shot_lay, ann=f'add shot', i='pickHandlesComp', height=icon_size, width=icon_size, command=partial(self.addShot))
        # Attach the assetsScrollList
        cmds.formLayout(shot_lay, e=True, attachForm=[(scrollList, "left", 0), (scrollList, "top", 0), (scrollList, "bottom", 0)])
        # Attach the assetsAddButton
        cmds.formLayout(shot_lay, e=True, attachForm=[(addButton, "right", 0), (addButton, "top", 0)])
        cmds.formLayout(shot_lay, e=True, attachControl=[(scrollList, "right", 0, addButton)])

        assetsScrollList = cmds.textScrollList('assets', p=assets_lay, numberOfRows=5, allowMultiSelection=False, selectCommand=self.updateStepScrollList)

        self.openButton = cmds.button(p=self.layout, label="open", command=self.openLastEdit)

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
                                    (shot_lay, 'bottom', 5)],

                        attachControl=[(sequence_lay, 'top', 5, sq_text),
                                       (openSqLayoutButton, 'top', 5, sequence_lay),
                                       (createShotLayoutButton, 'top', 5, sequence_lay),
                                       (createShotLayoutButton, 'left', 5, openSqLayoutButton),
                                       (sh_text, 'top', 5, openSqLayoutButton),
                                       (shot_lay, 'top', 5, sh_text)])


    def updateSequenceScrollList(self, *args):
        print("update sequence")

    def addSequence(self, *args):
        print("adding sequence")
    
    def openSqLayout(self, *args):
        print("opening sequence layout")
    
    def createShotLayoutLayout(self, *args):
        print("creating shot layout")

    def updateShotScrollList(self, *args):
        print("update shot")

    def addShot(self, *args):
        print("adding shot")