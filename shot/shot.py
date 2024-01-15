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

        main_window.scrollListAdd(self.shot_lay, "sequence", self.updateSequenceScrollList, self.addSequence)

    def updateSequenceScrollList(self):
        print("update sequence")

    def addSequence(self):
        print("ading sequence")