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

        sq_text = cmds.text(label="Sequence", p=layout)
        
        sequence_lay = cmds.formLayout(p=self.layout)
        scrollList = cmds.textScrollList("sequence", p=sequence_lay, numberOfRows=5, allowMultiSelection=False, selectCommand=partial(self.updateSequenceScrollList))
        addButton = cmds.symbolButton('sequenceAddButton', p=sequence_lay, ann=f'add sequence', i='pickHandlesComp', height=icon_size, width=icon_size, command=partial(self.addSequence))
        # Attach the assetsScrollList
        cmds.formLayout(sequence_lay, e=True, attachForm=[(scrollList, "left", 0), (scrollList, "top", 0), (scrollList, "bottom", 0)])
        # Attach the assetsAddButton
        cmds.formLayout(sequence_lay, e=True, attachForm=[(addButton, "right", 0), (addButton, "top", 0)])
        cmds.formLayout(sequence_lay, e=True, attachControl=[(scrollList, "right", 0, addButton)])

        sh_text = cmds.text(label="Shot", p=layout)

        shot_lay = cmds.formLayout(p=self.layout)
        scrollList = cmds.textScrollList("shot", p=shot_lay, numberOfRows=5, allowMultiSelection=False, selectCommand=partial(self.updateShotScrollList))
        addButton = cmds.symbolButton('shotAddButton', p=shot_lay, ann=f'add shot', i='pickHandlesComp', height=icon_size, width=icon_size, command=partial(self.addShot))
        # Attach the assetsScrollList
        cmds.formLayout(shot_lay, e=True, attachForm=[(scrollList, "left", 0), (scrollList, "top", 0), (scrollList, "bottom", 0)])
        # Attach the assetsAddButton
        cmds.formLayout(shot_lay, e=True, attachForm=[(addButton, "right", 0), (addButton, "top", 0)])
        cmds.formLayout(shot_lay, e=True, attachControl=[(scrollList, "right", 0, addButton)])

        cmds.formLayout( self.layout, edit=True,
                        attachForm=[(sq_text, 'top', 5),
                                    (sq_text, 'left', 5),
                                    (sq_text, 'right', 5),
                                    (sequence_lay, 'left', 5),
                                    (sequence_lay, 'right', 5),
                                    (sh_text, 'left', 5),
                                    (sh_text, 'right', 5),
                                    (shot_lay, 'left', 5),
                                    (shot_lay, 'right', 5),
                                    (shot_lay, 'bottom', 5)],

                        attachControl=[(sequence_lay, 'top', 5, sq_text),
                                       (sh_text, 'top', 5, sequence_lay),
                                       (shot_lay, 'top', 5, sh_text)])


    def updateSequenceScrollList(self):
        print("update sequence")

    def addSequence(self):
        print("ading sequence")

    def updateShotScrollList(self):
        print("update shot")

    def addShot(self):
        print("ading shot")