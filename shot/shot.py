# coding : utf-8
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

        self.shot_lay = cmds.formLayout(p=self.parent_layout)

        
        lay = cmds.formLayout(p=self.shot_lay)
        scrollList = cmds.textScrollList("sequence", p=lay, numberOfRows=5, allowMultiSelection=False, selectCommand=partial(self.updateSequenceScrollList))
        addButton = cmds.symbolButton('sequenceAddButton', p=lay, ann=f'add sequence', i='pickHandlesComp', height=icon_size, width=icon_size, command=partial(self.addSequence))
        # Attach the assetsScrollList
        cmds.formLayout(lay, e=True, attachForm=[(scrollList, "left", 0), (scrollList, "top", 0), (scrollList, "bottom", 0)])
        # Attach the assetsAddButton
        cmds.formLayout(lay, e=True, attachForm=[(addButton, "right", 0), (addButton, "top", 0)])
        cmds.formLayout(lay, e=True, attachControl=[(scrollList, "right", 0, addButton)])

    def updateSequenceScrollList(self):
        print("update sequence")

    def addSequence(self):
        print("ading sequence")