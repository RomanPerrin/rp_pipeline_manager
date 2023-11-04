# coding : utf-8
__author__ = 'Roman PERRIN'
#Author: Roman PERRIN

#Libraries
import maya.cmds as cmds
import maya.mel as mel

#files


def onMayaDroppedPythonFile(*args):
    currentShelf = mel.eval("global string $gShelfTopLevel;\rstring $shelves = `tabLayout -q -selectTab $gShelfTopLevel`;")
    button = cmds.shelfButton(parent = currentShelf,
                visible = 1,
                flexibleWidthType = 1,
                annotation = "Pipeline Manager",
                label = "Pipeline Manager",
                useAlpha = 1,
                style = "iconOnly",
                image = "icone2.svg",
                command = "import rp_pipeline_manager\nfrom importlib import reload\nreload(rp_pipeline_manager)",
                sourceType = "python",
                commandRepeatable = 1,
                flat = 1)